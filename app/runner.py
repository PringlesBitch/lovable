from __future__ import annotations
import argparse
from datetime import datetime
import html
import os
from pathlib import Path
import re

from dotenv import load_dotenv
from app.html_fetcher import fetch_html
from app.redesign_generator import generate_redesign


def _safe_slug(url: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", url).strip("-").lower()
    return slug[:80] or "website"


def _render_html_document(title: str, redesign_text: str) -> str:
    return f"""<!doctype html><html lang="cs"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title></head><body><pre>{html.escape(redesign_text)}</pre></body></html>"""


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Vygeneruje redesign pro jednu URL.")
    p.add_argument("--url", required=True)
    p.add_argument("--prompt", default="")
    p.add_argument("--prompt-file", default=None)
    p.add_argument("--artifacts-dir", default=None)
    return p.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    extra_prompt = args.prompt
    if args.prompt_file:
        extra_prompt = Path(args.prompt_file).read_text(encoding="utf-8").strip()

    artifacts_dir = Path(args.artifacts_dir or os.getenv("ARTIFACTS_DIR", "./artifacts"))
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    page = fetch_html(args.url)
    redesign = generate_redesign(page, custom_prompt=extra_prompt or None)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = _safe_slug(page.final_url)
    run_dir = artifacts_dir / f"run_{ts}_{slug}"
    run_dir.mkdir(parents=True, exist_ok=True)

    (run_dir / "redesign.md").write_text(redesign, encoding="utf-8")
    (run_dir / "index.html").write_text(
        _render_html_document(f"Redesign: {page.title or page.final_url}", redesign),
        encoding="utf-8",
    )

    print(f"HTML: {run_dir / 'index.html'}")


if __name__ == "__main__":
    main()
