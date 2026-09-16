from __future__ import annotations

import argparse
import json
import sys

from .scanner import ZabedSecError, scan, write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zabedsec",
        description="Defensive-first security assessment scanner for authorized targets.",
    )
    parser.add_argument("target", help="HTTP(S) URL or hostname you are authorized to assess")
    parser.add_argument("--ports", default="", help="Optional comma-separated TCP ports, e.g. 80,443,8080")
    parser.add_argument("--timeout", type=float, default=5.0, help="Network timeout in seconds")
    parser.add_argument("--json", dest="json_path", help="Write the complete report to a JSON file")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.target:
        return 2
    try:
        ports = []
        if args.ports:
            ports = [int(value.strip()) for value in args.ports.split(",") if value.strip()]
            if any(port < 1 or port > 65535 for port in ports):
                raise ZabedSecError("Ports must be between 1 and 65535")
        report = scan(args.target, ports=ports, timeout=args.timeout)
    except (ValueError, ZabedSecError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print("ZabedSec 0.1.0")
    print("Authorized security assessment only")
    print("=" * 60)
    print(f"Target: {report['target']}")
    print(f"Host:   {report['host']}")
    if "http" in report:
        print(f"HTTP:   {report['http']['status']} {report['http']['final_url']}")
    if "tls" in report:
        print(f"TLS:    {report['tls']['protocol']} / {report['tls']['cipher']}")
    if "ports" in report:
        print("Ports:  " + ", ".join(f"{p}={s}" for p, s in report["ports"].items()))

    print("\nFindings")
    for finding in report["findings"]:
        print(f"[{finding['severity'].upper():6}] {finding['check']}: {finding['message']}")
    print("\nSummary:", json.dumps(report["summary"]))

    if args.json_path:
        write_json(report, args.json_path)
        print(f"Report: {args.json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
