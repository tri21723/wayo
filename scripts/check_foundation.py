"""Read-only smoke check through the web -> API -> database boundary."""

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--web-url", default="http://localhost:3000")
    args = parser.parse_args()
    parsed = urllib.parse.urlsplit(args.web_url)
    if parsed.scheme not in ("http", "https") or parsed.username or parsed.password:
        parser.error("Use an HTTP(S) web URL without credentials.")
    try:
        with urllib.request.urlopen(
            f"{args.web_url.rstrip('/')}/api/health", timeout=12
        ) as response:
            data = json.load(response)
            if data != {
                "status": "ready",
                "database": "ready",
                "migrations": "current",
                "auth": "configured",
            }:
                raise ValueError("Not ready")
        print(
            json.dumps(
                {
                    "foundation": "ready",
                    "checks": ["web", "api", "database", "migrations", "auth_config"],
                }
            )
        )
        return 0
    except (urllib.error.URLError, ValueError):
        print(
            json.dumps(
                {
                    "foundation": "not_ready",
                    "hint": "Check API /ready and environment configuration.",
                }
            )
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
