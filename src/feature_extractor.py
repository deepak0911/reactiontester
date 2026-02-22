"""Extract product features from company web pages using scraping and Claude API."""

import json
import logging

from anthropic import Anthropic

from .web_scraper import fetch_page, search_web

logger = logging.getLogger(__name__)

# Maximum characters of page text to send to Claude
MAX_PAGE_TEXT = 12000


def _gather_feature_content(company_name: str, company_url: str) -> str:
    """Scrape the company's website and feature-related search results."""
    texts = []

    # Try the main website
    page = fetch_page(company_url)
    if page.success:
        texts.append(f"=== Main page: {company_url} ===\n{page.text_content[:MAX_PAGE_TEXT]}")

    # Try common feature/pricing pages
    for suffix in ["/features", "/pricing", "/product"]:
        base = company_url.rstrip("/")
        feature_page = fetch_page(base + suffix)
        if feature_page.success and feature_page.text_content:
            texts.append(
                f"=== {base + suffix} ===\n{feature_page.text_content[:MAX_PAGE_TEXT]}"
            )

    # Supplement with search results
    results = search_web(f"{company_name} features list", num_results=5)
    for r in results:
        texts.append(f"=== Search: {r['title']} ===\n{r['snippet']}")

    return "\n\n".join(texts) if texts else f"(No content found for {company_name})"


def _build_extraction_prompt(company_name: str, raw_content: str) -> str:
    return f"""Analyze the following web content for "{company_name}" and extract their key product features.

Organize features into categories. For each feature, note:
- Feature name
- Brief description
- Whether it appears to be a core/standard feature or premium/enterprise

Web content:
{raw_content[:30000]}

Respond ONLY with valid JSON (no markdown fences):
{{
  "company": "{company_name}",
  "categories": [
    {{
      "name": "Category Name",
      "features": [
        {{
          "name": "Feature Name",
          "description": "Brief description",
          "tier": "core|premium|enterprise"
        }}
      ]
    }}
  ]
}}"""


def extract_features(
    company_name: str, company_url: str, client: Anthropic
) -> dict:
    """Extract structured features for a single company.

    Scrapes the company's website and related pages, then uses Claude
    to parse the raw content into structured feature data.
    """
    logger.info("Extracting features for %s (%s)", company_name, company_url)

    raw_content = _gather_feature_content(company_name, company_url)
    prompt = _build_extraction_prompt(company_name, raw_content)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text.strip()
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1]
        response_text = response_text.rsplit("```", 1)[0].strip()

    return json.loads(response_text)


def extract_features_batch(
    competitors: list[dict], client: Anthropic
) -> list[dict]:
    """Extract features for a list of competitors.

    Each competitor dict must have 'name' and 'url' keys.
    Returns a list of feature extraction results.
    """
    results = []
    for comp in competitors:
        try:
            features = extract_features(comp["name"], comp["url"], client)
            results.append(features)
        except Exception as exc:
            logger.error("Failed to extract features for %s: %s", comp["name"], exc)
            results.append({
                "company": comp["name"],
                "categories": [],
                "error": str(exc),
            })
    return results
