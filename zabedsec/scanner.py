from __future__ import annotations

import json
import socket
import ssl
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse
from urllib.request import Request, urlopen


SECURITY_HEADERS = {
    "strict-transport-security": "HSTS",
    "content-security-policy": "CSP",
    "x-content-type-options": "X-Content-Type-Options",
    "x-frame-options": "X-Frame-Options",
    "referrer-policy": "Referrer-Policy",
    "permissions-policy": "Permissions-Policy",
}


@dataclass
class Finding:
    severity: str
    check: str
    message: str


class ZabedSecError(Exception):
    pass


def normalize_target(target: str) -> tuple[str, str]:
    value = target.strip()
    if not value:
        raise ZabedSecError("Target cannot be empty")
    if "://" not in value:
        value = "https://" + value
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ZabedSecError("Target must be an HTTP(S) URL or hostname")
    return value, parsed.hostname


def dns_check(host: str) -> dict:
    addresses = sorted({item[4][0] for item in socket.getaddrinfo(host, None)})
    return {"hostname": host, "addresses": addresses}


def http_check(url: str, timeout: float) -> dict:
    request = Request(url, headers={"User-Agent": "ZabedSec/0.1 authorized-security-assessment"})
    started = time.perf_counter()
    with urlopen(request, timeout=timeout) as response:
        headers = {k.lower(): v for k, v in response.headers.items()}
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        return {
            "status": response.status,
            "final_url": response.geturl(),
            "elapsed_ms": elapsed_ms,
            "headers": headers,
        }


def header_findings(headers: dict) -> list[Finding]:
    findings = []
    for key, label in SECURITY_HEADERS.items():
        if key not in headers:
            severity = "medium" if key in {"strict-transport-security", "content-security-policy"} else "low"
            findings.append(Finding(severity, label, f"Missing {label} header"))
    server = headers.get("server")
    if server and any(ch.isdigit() for ch in server):
        findings.append(Finding("low", "Server disclosure", "Server header appears to disclose version information"))
    return findings


def tls_check(host: str, port: int = 443, timeout: float = 5.0) -> dict:
    context = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=timeout) as raw:
        with context.wrap_socket(raw, server_hostname=host) as sock:
            cert = sock.getpeercert()
            return {
                "protocol": sock.version(),
                "cipher": sock.cipher()[0] if sock.cipher() else None,
                "subject": dict(x[0] for x in cert.get("subject", [])),
                "issuer": dict(x[0] for x in cert.get("issuer", [])),
                "not_before": cert.get("notBefore"),
                "not_after": cert.get("notAfter"),
            }


def port_check(host: str, ports: list[int], timeout: float = 0.7) -> dict:
    results = {}
    for port in ports:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                results[str(port)] = "open"
        except (TimeoutError, ConnectionRefusedError, OSError):
            results[str(port)] = "closed_or_filtered"
    return results


def scan(target: str, ports: list[int] | None = None, timeout: float = 5.0) -> dict:
    url, host = normalize_target(target)
    report = {
        "tool": "ZabedSec",
        "version": "0.1.0",
        "target": url,
        "host": host,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "authorization_required": True,
        "findings": [],
    }

    report["dns"] = dns_check(host)
    try:
        report["http"] = http_check(url, timeout)
        report["findings"].extend(asdict(f) for f in header_findings(report["http"]["headers"]))
    except Exception as exc:
        report["http_error"] = str(exc)
        report["findings"].append(asdict(Finding("info", "HTTP check", f"HTTP check did not complete: {exc}")))

    if urlparse(url).scheme == "https":
        try:
            report["tls"] = tls_check(host, timeout=timeout)
        except Exception as exc:
            report["tls_error"] = str(exc)
            report["findings"].append(asdict(Finding("medium", "TLS", f"TLS inspection failed: {exc}")))

    if ports:
        report["ports"] = port_check(host, ports)

    counts = {level: 0 for level in ("high", "medium", "low", "info")}
    for finding in report["findings"]:
        counts[finding["severity"]] += 1
    report["summary"] = counts
    return report


def write_json(report: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
