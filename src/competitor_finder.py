"""Discover top competitors for a given company using web scraping and Claude API."""

import logging

from anthropic import Anthropic

from .web_scraper import search_web

logger = logging.getLogger(__name__)


def _build_competitor_prompt(company: str, search_context: str) -> str:
    return f"""Based on the following web search results about "{company}" competitors,
identify the top 5 competitors. For each competitor, provide:
1. Company name
2. Website URL (best guess if not explicit)
3. A one-line description of what they do

Search results:
{search_context}

Respond ONLY with valid JSON in this exact format (no markdown fences):
{{
  "company": "{company}",
  "competitors": [
    {{
      "name": "Competitor Name",
      "url": "https://competitor.com",
      "description": "One-line description"
    }}
  ]
}}"""


def find_competitors(company: str, client: Anthropic) -> dict:
    """Find top competitors for the given company.

    Uses web search to gather context, then Claude to extract structured
    competitor data from the results.
    """
    queries = [
        f"{company} top competitors",
        f"{company} alternatives comparison",
        f"{company} vs competitors features",
    ]

    all_snippets = []
    for query in queries:
        results = search_web(query, num_results=8)
        for r in results:
            all_snippets.append(f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['snippet']}")

    if not all_snippets:
        logger.warning("No search results found for %s, using Claude's knowledge", company)
        search_context = "(No search results available — use your general knowledge.)"
    else:
        search_context = "\n---\n".join(all_snippets[:20])

    prompt = _build_competitor_prompt(company, search_context)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    import json

    response_text = message.content[0].text.strip()
    # Handle possible markdown fences in response
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1]
        response_text = response_text.rsplit("```", 1)[0].strip()

    return json.loads(response_text)
