"""Web scraping utilities for fetching and parsing web content."""

import logging
import time
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

MAX_RETRIES = 3
RETRY_BACKOFF = 2  # seconds


@dataclass
class ScrapedPage:
    """Represents a scraped web page."""

    url: str
    title: str
    text_content: str
    status_code: int
    success: bool
    error: str | None = None


def fetch_page(url: str, timeout: int = 15) -> ScrapedPage:
    """Fetch a web page and return its parsed content.

    Retries on transient failures with exponential backoff.
    """
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(
                url, headers=DEFAULT_HEADERS, timeout=timeout, allow_redirects=True
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")

            # Remove script, style, nav, footer elements
            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()

            title = soup.title.string.strip() if soup.title and soup.title.string else ""
            text = soup.get_text(separator="\n", strip=True)

            # Collapse excessive whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            clean_text = "\n".join(lines)

            return ScrapedPage(
                url=url,
                title=title,
                text_content=clean_text,
                status_code=response.status_code,
                success=True,
            )

        except requests.RequestException as exc:
            last_error = str(exc)
            logger.warning(
                "Attempt %d/%d failed for %s: %s", attempt + 1, MAX_RETRIES, url, exc
            )
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BACKOFF * (attempt + 1))

    return ScrapedPage(
        url=url,
        title="",
        text_content="",
        status_code=0,
        success=False,
        error=last_error,
    )


def search_web(query: str, num_results: int = 10) -> list[dict]:
    """Search the web using DuckDuckGo HTML and return results.

    Returns a list of dicts with 'title', 'url', and 'snippet' keys.
    """
    search_url = "https://html.duckduckgo.com/html/"
    params = {"q": query}

    try:
        response = requests.post(
            search_url, data=params, headers=DEFAULT_HEADERS, timeout=15
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Search request failed: %s", exc)
        return []

    soup = BeautifulSoup(response.text, "lxml")
    results = []

    for result_div in soup.select(".result")[:num_results]:
        title_tag = result_div.select_one(".result__title a")
        snippet_tag = result_div.select_one(".result__snippet")

        if not title_tag:
            continue

        href = title_tag.get("href", "")
        title = title_tag.get_text(strip=True)
        snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

        if href:
            results.append({"title": title, "url": href, "snippet": snippet})

    return results
