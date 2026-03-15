"""Načítání HTML obsahu webů."""

from __future__ import annotations

from dataclasses import dataclass
import re

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


@dataclass(slots=True)
class FetchedPage:
    """Výsledek načtení webové stránky."""
    url: str
    final_url: str
    status_code: int
    html: str
    title: str


@retry(
    retry=retry_if_exception_type(httpx.HTTPError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
)
def fetch_html(url: str, timeout_s: float = 20.0) -> FetchedPage:
    """Stáhne HTML z URL a vrátí základní metadata."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        )
    }

    with httpx.Client(follow_redirects=True, timeout=timeout_s, headers=headers) as client:
        response = client.get(url)
        response.raise_for_status()

    html = response.text
    match = TITLE_RE.search(html)
    title = re.sub(r"\s+", " ", match.group(1)).strip() if match else ""

    return FetchedPage(
        url=url,
        final_url=str(response.url),
        status_code=response.status_code,
        html=html,
        title=title,
    )
