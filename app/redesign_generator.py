"""Generování návrhů redesignu."""

from __future__ import annotations

import os
from textwrap import dedent

from openai import OpenAI

from app.html_fetcher import FetchedPage


def _truncate_html(html: str, max_chars: int = 12000) -> str:
    cleaned = " ".join(html.split())
    return cleaned[:max_chars]


def _fallback_redesign(page: FetchedPage, custom_prompt: str | None = None) -> str:
    return dedent(
        f"""
        # Návrh redesignu (fallback bez OpenAI)

        **URL:** {page.final_url}
        **Title:** {page.title or 'N/A'}

        1) Hero s jasným benefitem + CTA
        2) 3 hlavní výhody
        3) Sociální důkaz
        4) FAQ + CTA

        Poznámka: {custom_prompt or '(bez dodatečného promptu)'}
        """
    ).strip()


def generate_redesign(page: FetchedPage, custom_prompt: str | None = None) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return _fallback_redesign(page, custom_prompt)

    client = OpenAI(api_key=api_key)
    prompt = dedent(
        f"""
        Připrav návrh redesignu webu v češtině.
        URL: {page.final_url}
        Title: {page.title}
        HTML výřez: {_truncate_html(page.html)}
        Dodatečný prompt: {custom_prompt or '(není)'}
        """
    ).strip()

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        input=prompt,
    )
    return response.output_text.strip()
