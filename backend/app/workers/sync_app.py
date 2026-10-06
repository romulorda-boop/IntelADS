from __future__ import annotations

import argparse
import json
import sys

from app.services.app_sync import AppNotFoundError, AppSyncError, sync_app


def main() -> int:
    parser = argparse.ArgumentParser(description="Sincroniza metadados de um app com sua loja pública.")
    parser.add_argument("app_id", help="UUID do app no PostgreSQL ou store_app_id registrado")
    args = parser.parse_args()

    try:
        result = sync_app(args.app_id)
    except AppNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except AppSyncError as exc:
        print(f"{exc.code}: {exc.public_message}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
