"""Compare features across multiple competitors using Claude API."""

import json
import logging

from anthropic import Anthropic

logger = logging.getLogger(__name__)


def _build_comparison_prompt(company: str, all_features: list[dict]) -> str:
    features_json = json.dumps(all_features, indent=2)
    return f"""You are a product analyst. Below is structured feature data for "{company}" and its competitors.

Produce a comprehensive feature comparison that includes:
1. A unified list of feature categories across all companies
2. For each feature, which companies offer it and at what tier
3. Competitive advantages — features unique to each company
4. Gaps — important features that "{company}" is missing vs competitors
5. An overall competitive positioning summary

Feature data:
{features_json}

Respond ONLY with valid JSON (no markdown fences):
{{
  "target_company": "{company}",
  "comparison": {{
    "categories": [
      {{
        "name": "Category Name",
        "features": [
          {{
            "name": "Feature Name",
            "availability": {{
              "CompanyA": "core",
              "CompanyB": "premium",
              "CompanyC": "not available"
            }}
          }}
        ]
      }}
    ],
    "unique_advantages": {{
      "CompanyA": ["feature1", "feature2"],
      "CompanyB": ["feature3"]
    }},
    "gaps": [
      {{
        "feature": "Feature Name",
        "offered_by": ["CompanyB", "CompanyC"],
        "importance": "high|medium|low"
      }}
    ],
    "summary": "Overall competitive positioning analysis."
  }}
}}"""


def compare_features(
    company: str, all_features: list[dict], client: Anthropic
) -> dict:
    """Generate a structured comparison of features across all companies.

    Args:
        company: The target company being analyzed.
        all_features: List of feature extraction results for target + competitors.
        client: Anthropic API client.

    Returns:
        Structured comparison dict.
    """
    prompt = _build_comparison_prompt(company, all_features)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text.strip()
    if response_text.startswith("```"):
        response_text = response_text.split("\n", 1)[1]
        response_text = response_text.rsplit("```", 1)[0].strip()

    return json.loads(response_text)
