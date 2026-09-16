# ZabedSec

ZabedSec is an original, defensive-first reconnaissance and security-assessment toolkit for systems you own or are explicitly authorized to test.

The design is informed by current open-source security tooling such as ProjectDiscovery's Nuclei ecosystem, but this project does not copy Nuclei source code or templates.

## Features
- URL/domain validation
- HTTP status and response-header inspection
- Security-header checks
- TLS certificate and protocol inspection
- DNS resolution
- Safe TCP connect checks for a small, explicitly supplied port list
- JSON report generation
- Explicit authorization reminder before scanning
- No exploit execution, credential attacks, destructive tests, or stealth/evasion features

## Usage

```bash
python -m zabedsec.cli https://example.com --ports 80,443,8080 --json report.json
```

Only scan assets you own or have written authorization to assess.

## Roadmap
- HTML reporting
- Passive technology fingerprinting
- CVE intelligence ingestion
- Optional integration with external scanners
- Web dashboard
- CI security checks

## License
MIT
