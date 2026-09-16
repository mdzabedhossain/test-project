from __future__ import annotations

import json
import os
import socket
import ssl
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .scanner import normalize_target, scan

app = FastAPI(title="ZabedSec API", version="0.2.0")
HISTORY = Path(os.getenv("ZABE DSEC_HISTORY_DIR", "/tmp/zabedsec-history").replace(" ", ""))
HISTORY.mkdir(parents=True, exist_ok=True)


def allowed_hosts() -> set[str]:
    raw = os.getenv("ZABEDSEC_ALLOWED_HOSTS", "localhost,127.0.0.1")
    return {x.strip().lower().rstrip(".") for x in raw.split(",") if x.strip()}


def check_authorization(target: str, authorization: str | None) -> str:
    if (authorization or "").lower() != "authorized":
        raise HTTPException(403, "Set X-ZabedSec-Authorization: authorized after confirming you own or are authorized to assess the target")
    _, host = normalize_target(target)
    host = host.lower().rstrip(".")
    if host not in allowed_hosts():
        raise HTTPException(403, f"Target host is not in ZABEDSEC_ALLOWED_HOSTS: {host}")
    return host


class ScanRequest(BaseModel):
    target: str = Field(min_length=1, max_length=2048)
    ports: list[int] = Field(default_factory=list, max_length=32)
    timeout: float = Field(default=5.0, ge=1.0, le=15.0)


def tech_fingerprint(report: dict) -> list[str]:
    headers = report.get("http", {}).get("headers", {})
    found: list[str] = []
    server = headers.get("server", "").lower()
    powered = headers.get("x-powered-by", "").lower()
    for token, name in (("nginx", "Nginx"), ("apache", "Apache"), ("iis", "Microsoft IIS"), ("cloudflare", "Cloudflare"), ("express", "Express"), ("php", "PHP"), ("asp.net", "ASP.NET")):
        if token in server or token in powered:
            found.append(name)
    if powered and "X-Powered-By: " + powered not in found:
        found.append("X-Powered-By: " + powered)
    return sorted(set(found))


def passive_subdomains(domain: str) -> list[str]:
    if "." not in domain or domain in {"localhost", "127.0.0.1"}:
        return []
    url = "https://crt.sh/?q=" + urllib.parse.quote("%." + domain) + "&output=json"
    req = urllib.request.Request(url, headers={"User-Agent": "ZabedSec/0.2 passive-certificate-enumeration"})
    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.load(response)
        names: set[str] = set()
        for item in data:
            for name in item.get("name_value", "").splitlines():
                name = name.strip().lower().lstrip("*.")
                if name == domain or name.endswith("." + domain):
                    names.add(name)
        return sorted(names)[:200]
    except Exception:
        return []


def render_html(report: dict) -> str:
    summary = report.get("summary", {})
    findings = report.get("findings", [])
    rows = "".join(f"<tr><td>{f.get('severity')}</td><td>{f.get('check')}</td><td>{f.get('message')}</td></tr>" for f in findings)
    return f"""<!doctype html><html><head><meta charset='utf-8'><title>ZabedSec Report</title><style>body{{font-family:system-ui;max-width:1100px;margin:2rem auto;padding:0 1rem}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:.5rem;text-align:left}}code{{background:#f3f3f3;padding:.2rem}}</style></head><body><h1>ZabedSec Security Assessment</h1><p><b>Target:</b> <code>{report.get('target')}</code></p><p><b>Generated:</b> {report.get('timestamp')}</p><h2>Summary</h2><p>High: {summary.get('high',0)} · Medium: {summary.get('medium',0)} · Low: {summary.get('low',0)} · Info: {summary.get('info',0)}</p><h2>Technologies</h2><p>{', '.join(report.get('technologies', [])) or 'No passive fingerprint identified'}</p><h2>Findings</h2><table><tr><th>Severity</th><th>Check</th><th>Message</th></tr>{rows}</table></body></html>"""


@app.get("/health")
def health():
    return {"status": "ok", "service": "zabedsec", "version": "0.2.0"}


@app.get("/api/info")
def info():
    return {"name": "ZabedSec", "version": "0.2.0", "authorization_required": True, "allowed_hosts_configured": sorted(allowed_hosts())}


@app.post("/api/scan")
def run_scan(payload: ScanRequest, x_zabedsec_authorization: str | None = Header(default=None)):
    host = check_authorization(payload.target, x_zabedsec_authorization)
    if any(p < 1 or p > 65535 for p in payload.ports):
        raise HTTPException(400, "Ports must be between 1 and 65535")
    report = scan(payload.target, payload.ports or None, payload.timeout)
    report["version"] = "0.2.0"
    report["technologies"] = tech_fingerprint(report)
    report["passive_subdomains"] = passive_subdomains(host)
    scan_id = uuid.uuid4().hex
    report["scan_id"] = scan_id
    (HISTORY / f"{scan_id}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


@app.get("/api/history")
def history():
    items = []
    for path in sorted(HISTORY.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:50]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            items.append({"scan_id": data.get("scan_id"), "target": data.get("target"), "timestamp": data.get("timestamp"), "summary": data.get("summary", {})})
        except Exception:
            continue
    return items


@app.get("/api/report/{scan_id}")
def report(scan_id: str):
    path = HISTORY / f"{scan_id}.json"
    if not path.exists():
        raise HTTPException(404, "Scan not found")
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/api/report/{scan_id}/html", response_class=HTMLResponse)
def report_html(scan_id: str):
    data = report(scan_id)
    return render_html(data)


@app.get("/api/cve")
def cve_search(keyword: str = Query(min_length=2, max_length=100)):
    params = urllib.parse.urlencode({"keywordSearch": keyword, "resultsPerPage": 10})
    url = "https://services.nvd.nist.gov/rest/json/cves/2.0?" + params
    req = urllib.request.Request(url, headers={"User-Agent": "ZabedSec/0.2 CVE-intelligence"})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.load(response)
        results = []
        for item in data.get("vulnerabilities", []):
            cve = item.get("cve", {})
            desc = next((d.get("value") for d in cve.get("descriptions", []) if d.get("lang") == "en"), "")
            results.append({"id": cve.get("id"), "published": cve.get("published"), "description": desc})
        return {"keyword": keyword, "results": results}
    except Exception as exc:
        raise HTTPException(502, f"CVE intelligence lookup failed: {exc}")


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>ZabedSec</title><style>body{font-family:system-ui;max-width:1000px;margin:auto;padding:2rem}input,button{padding:.7rem;margin:.25rem}button{cursor:pointer}.card{border:1px solid #ddd;border-radius:12px;padding:1rem;margin:1rem 0}pre{white-space:pre-wrap;background:#f5f5f5;padding:1rem;border-radius:8px}</style></head><body><h1>🛡️ ZabedSec</h1><p>Authorized security assessment dashboard — v0.2.0</p><div class='card'><input id='target' placeholder='https://authorized-target.example' size='45'><input id='ports' placeholder='80,443'><button onclick='run()'>Run assessment</button><p>Authorization header is added by this demo UI. The server also enforces an explicit host allowlist.</p></div><div class='card'><h2>Result</h2><pre id='out'>Ready.</pre></div><script>async function run(){const target=document.getElementById('target').value;const ports=document.getElementById('ports').value.split(',').map(x=>x.trim()).filter(Boolean).map(Number);document.getElementById('out').textContent='Scanning...';try{const r=await fetch('/api/scan',{method:'POST',headers:{'Content-Type':'application/json','X-ZabedSec-Authorization':'authorized'},body:JSON.stringify({target,ports})});document.getElementById('out').textContent=JSON.stringify(await r.json(),null,2)}catch(e){document.getElementById('out').textContent=String(e)}}</script></body></html>"""
