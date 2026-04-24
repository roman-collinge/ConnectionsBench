"""
Fetches NYT Connections puzzles from the NYT v2 API and appends them to a local JSON dataset.
Runs incrementally — starts from the day after the last stored puzzle, or from the first
puzzle date if no dataset exists yet.
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

import requests
from loguru import logger

# When the connections game first released a puzzle
_FIRST_PUZZLE_DATE = "2023-06-12"
# v1 output colours with the groups, v2 just does an id so we need a map
_TIER_MAP = {0: "Yellow", 1: "Green", 2: "Blue", 3: "Purple"}
# Aforementioned Connections API transition from v1 to v2 broke lots of peoples code, this tracks schema changes in case
_SCHEMA_VERSION = 1
_DEFAULT_DATA_FILE = Path(__file__).parent.parent / "data" / "connections.json"


def parse_response(data: dict, puzzle_id: int, date: str) -> dict:
    categories = data.get("categories", [])
    if len(categories) != 4:
        raise ValueError(f"Expected 4 categories, got {len(categories)}")

    groups = []
    words = []
    has_images = False

    # Collate groups and words for each day's puzzle
    for i, category in enumerate(categories):
        members = []
        for card in category["cards"]:
            if "content" in card:
                members.append(card["content"])
            elif "image_url" in card:
                has_images = True
            else:
                raise ValueError(f"Card has neither 'content' nor 'image_url': {card}")
        words.extend(members)
        groups.append(
            {
                "label": category["title"],
                "tier": _TIER_MAP[i],
                "members": members,
            }
        )

    if has_images:
        logger.warning(f"Puzzle #{puzzle_id} ({date}) is image-based — storing with has_images flag")

    return {
        "schema_version": _SCHEMA_VERSION,
        "id": puzzle_id,
        "date": date,
        "has_images": has_images,
        "words": words if not has_images else [],
        "groups": groups if not has_images else [],
    }


def fetch_puzzle(date: str) -> dict | None:
    url = f"https://www.nytimes.com/svc/connections/v2/{date}.json"
    puzzle_json = requests.get(url, timeout=10)

    if puzzle_json.status_code == 404:
        return None

    puzzle_json.raise_for_status()

    content_type = puzzle_json.headers.get("Content-Type", "")
    if "application/json" not in puzzle_json.headers.get("Content-Type", ""):
        raise ValueError(f"Unexpected content type: {content_type}")

    return puzzle_json.json()


def load_existing_dataset(data_file: Path) -> list[dict]:
    if not data_file.exists():
        return []
    with open(data_file) as content:
        return json.load(content)


def save(puzzles: list[dict], data_file: Path) -> None:
    data_file.parent.mkdir(parents=True, exist_ok=True)
    with open(data_file, "w") as f:
        json.dump(puzzles, f, indent=4)


def main(data_file: Path) -> None:
    """
    Fetch puzzles incrementally from the NYT v2 API.
    Resumes from the day after the last stored puzzle, or backfills from the first puzzle date if no dataset exists yet.
    """
    puzzles = load_existing_dataset(data_file)

    # Determine start_date
    if puzzles:
        last_date = datetime.strptime(puzzles[-1]["date"], "%Y-%m-%d")
        next_id = puzzles[-1]["id"] + 1
        start_date = last_date + timedelta(days=1)
        logger.info(f"Resuming from #{next_id} ({start_date.strftime('%Y-%m-%d')})")
    else:
        start_date = datetime.strptime(_FIRST_PUZZLE_DATE, "%Y-%m-%d")
        next_id = 1
        logger.info(f"No existing dataset — backfilling from {_FIRST_PUZZLE_DATE}")

    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    current = start_date
    added = 0

    # Fetch from start_date
    while current <= today:
        date_str = current.strftime("%Y-%m-%d")
        logger.info(f"Fetching #{next_id} ({date_str})")

        data = fetch_puzzle(date_str)
        if data is None:
            logger.warning(f"No puzzle found for {date_str}, skipping")
            current += timedelta(days=1)
            continue

        puzzle = parse_response(data, puzzle_id=next_id, date=date_str)
        puzzles.append(puzzle)
        next_id += 1
        added += 1
        current += timedelta(days=1)

    save(puzzles, data_file)
    logger.info(f"Done. Added {added} puzzle(s). Total: {len(puzzles)}")


def create_parser() -> argparse.ArgumentParser:
    """
    Initialize command line argument parser with required and optional arguments.
    """
    parser = argparse.ArgumentParser(description="Fetch NYT Connections puzzles and append to local dataset.")

    parser.add_argument(
        "--data-file",
        type=Path,
        default=_DEFAULT_DATA_FILE,
        help=f"Path to the connections JSON dataset (default: {_DEFAULT_DATA_FILE})",
    )

    return parser


if __name__ == "__main__":
    args = create_parser().parse_args()

    try:
        logger.info("Starting fetch...")
        main(data_file=args.data_file)
        logger.info("Finished successfully")
    except Exception as e:
        logger.exception(e)
