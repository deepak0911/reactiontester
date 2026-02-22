"""CLI entry point for the Competitor Feature Comparison tool."""

import argparse
import json
import logging
import sys

from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .competitor_finder import find_competitors
from .feature_extractor import extract_features, extract_features_batch
from .feature_comparator import compare_features
from .output_formatter import (
    print_competitors,
    print_features,
    print_comparison,
    save_results,
)

load_dotenv()

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="competitor-compare",
        description="Find top competitors for a company and compare their features.",
    )
    parser.add_argument("company", help="Name of the target company to analyze")
    parser.add_argument(
        "--company-url",
        help="URL of the target company's website (auto-detected if omitted)",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=5,
        help="Number of top competitors to analyze (default: 5)",
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory to save JSON results (default: output/)",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Output raw JSON instead of formatted tables",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    return parser.parse_args()


def run(args: argparse.Namespace) -> None:
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    console = Console()
    client = Anthropic()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        # Step 1: Find competitors
        task = progress.add_task("Discovering competitors...", total=None)
        competitors_data = find_competitors(args.company, client)
        competitors = competitors_data.get("competitors", [])[:args.top_n]
        competitors_data["competitors"] = competitors
        progress.remove_task(task)

    console.print()
    print_competitors(competitors_data, console)

    # Resolve target company URL
    target_url = args.company_url
    if not target_url:
        target_url = f"https://www.{args.company.lower().replace(' ', '')}.com"
        console.print(f"[dim]Auto-detected target URL: {target_url}[/dim]\n")

    # Step 2: Extract features for all companies (target + competitors)
    all_companies = [{"name": args.company, "url": target_url}] + [
        {"name": c["name"], "url": c["url"]} for c in competitors
    ]

    all_features = []
    for comp in all_companies:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task(
                f"Extracting features for {comp['name']}...", total=None
            )
            try:
                features = extract_features(comp["name"], comp["url"], client)
            except Exception as exc:
                logger.error("Failed for %s: %s", comp["name"], exc)
                features = {"company": comp["name"], "categories": [], "error": str(exc)}
            progress.remove_task(task)

        all_features.append(features)
        print_features(features, console)

    # Step 3: Compare features
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Comparing features across competitors...", total=None)
        comparison = compare_features(args.company, all_features, client)
        progress.remove_task(task)

    if args.json_only:
        print(json.dumps(comparison, indent=2))
    else:
        print_comparison(comparison, console)

    # Step 4: Save results
    out_path = save_results(competitors_data, all_features, comparison, args.output_dir)
    console.print(f"\n[green bold]Results saved to {out_path}/[/green bold]")


def main() -> None:
    args = parse_args()
    try:
        run(args)
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(1)
    except Exception as exc:
        logging.error("Fatal error: %s", exc, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
