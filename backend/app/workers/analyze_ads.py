from __future__ import annotations

import json

from app.services.ad_analysis import run_ad_analysis


def main() -> None:
    report = run_ad_analysis()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report.get("errors") or report.get("committed") is False:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
