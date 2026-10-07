"""Validate a curated JSON batch; dry-run unless --apply is provided."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.catalog import CatalogBatch, import_batch
from app.database import engine_for
from app.settings import get_settings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument(
        "--apply", action="store_true", help="Write the full batch in one transaction"
    )
    args = parser.parse_args()
    try:
        if args.file.stat().st_size > 5_000_000:
            raise ValueError("Batch exceeds 5 MB.")
        batch = CatalogBatch.model_validate_json(args.file.read_text(encoding="utf-8"))
    except ValidationError as exc:
        print(
            json.dumps(
                exc.errors(include_input=False, include_context=False, include_url=False),
                ensure_ascii=False,
            )
        )
        return 1
    except (OSError, ValueError):
        print("Cannot read batch; expected a UTF-8 JSON file of at most 5 MB.")
        return 1
    if not args.apply:
        print(f"VALID: {len(batch.places)} records. Dry run; no database writes.")
        return 0
    url = get_settings().database_url
    if not url:
        print("WAYO_DATABASE_URL is required for --apply.")
        return 1
    try:
        with Session(engine_for(url)) as session, session.begin():
            result = import_batch(session, batch)
        print(json.dumps(result))
    except Exception:
        print("Import failed; transaction rolled back. Check database configuration/migrations.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
