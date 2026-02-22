"""Format comparison results for terminal and file output."""

import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


def print_competitors(competitors_data: dict, console: Console) -> None:
    """Print discovered competitors in a formatted table."""
    table = Table(title=f"Top Competitors for {competitors_data['company']}")
    table.add_column("#", style="dim", width=3)
    table.add_column("Company", style="cyan bold")
    table.add_column("URL", style="blue")
    table.add_column("Description", style="white")

    for i, comp in enumerate(competitors_data.get("competitors", []), 1):
        table.add_row(str(i), comp["name"], comp["url"], comp["description"])

    console.print(table)
    console.print()


def print_features(features_data: dict, console: Console) -> None:
    """Print extracted features for a single company."""
    company = features_data.get("company", "Unknown")
    categories = features_data.get("categories", [])

    if features_data.get("error"):
        console.print(f"  [red]Error extracting features: {features_data['error']}[/red]")
        return

    panel_content = []
    for cat in categories:
        panel_content.append(f"[bold yellow]{cat['name']}[/bold yellow]")
        for feat in cat.get("features", []):
            tier_color = {"core": "green", "premium": "yellow", "enterprise": "red"}.get(
                feat.get("tier", ""), "white"
            )
            panel_content.append(
                f"  [{tier_color}][{feat.get('tier', '?')}][/{tier_color}] "
                f"[bold]{feat['name']}[/bold] — {feat.get('description', '')}"
            )
        panel_content.append("")

    console.print(Panel("\n".join(panel_content), title=f"Features: {company}", border_style="cyan"))


def print_comparison(comparison_data: dict, console: Console) -> None:
    """Print the full feature comparison."""
    comp = comparison_data.get("comparison", {})
    target = comparison_data.get("target_company", "Target")

    # --- Feature availability matrix ---
    for category in comp.get("categories", []):
        all_companies = set()
        for feat in category.get("features", []):
            all_companies.update(feat.get("availability", {}).keys())
        companies = sorted(all_companies)

        table = Table(title=category["name"])
        table.add_column("Feature", style="bold")
        for c in companies:
            style = "cyan bold" if c.lower() == target.lower() else "white"
            table.add_column(c, style=style)

        for feat in category.get("features", []):
            avail = feat.get("availability", {})
            row = [feat["name"]]
            for c in companies:
                status = avail.get(c, "—")
                if status in ("core", "standard"):
                    row.append("[green]yes[/green]")
                elif status in ("premium", "enterprise"):
                    row.append(f"[yellow]{status}[/yellow]")
                elif status == "not available":
                    row.append("[red]no[/red]")
                else:
                    row.append(status)
            table.add_row(*row)

        console.print(table)
        console.print()

    # --- Unique advantages ---
    advantages = comp.get("unique_advantages", {})
    if advantages:
        console.print(Panel.fit("[bold]Unique Advantages[/bold]", border_style="green"))
        for company, feats in advantages.items():
            console.print(f"  [cyan bold]{company}[/cyan bold]")
            for f in feats:
                console.print(f"    - {f}")
        console.print()

    # --- Gaps ---
    gaps = comp.get("gaps", [])
    if gaps:
        gap_table = Table(title=f"Feature Gaps for {target}")
        gap_table.add_column("Feature", style="bold")
        gap_table.add_column("Offered By", style="cyan")
        gap_table.add_column("Importance", style="yellow")

        for gap in gaps:
            importance_color = {"high": "red", "medium": "yellow", "low": "green"}.get(
                gap.get("importance", ""), "white"
            )
            gap_table.add_row(
                gap["feature"],
                ", ".join(gap.get("offered_by", [])),
                f"[{importance_color}]{gap.get('importance', '?')}[/{importance_color}]",
            )

        console.print(gap_table)
        console.print()

    # --- Summary ---
    summary = comp.get("summary", "")
    if summary:
        console.print(Panel(summary, title="Competitive Positioning Summary", border_style="magenta"))


def save_results(
    competitors_data: dict,
    all_features: list[dict],
    comparison_data: dict,
    output_dir: str = "output",
) -> Path:
    """Save all results as JSON files in the output directory."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    company = competitors_data.get("company", "unknown").replace(" ", "_").lower()

    with open(out / f"{company}_competitors.json", "w") as f:
        json.dump(competitors_data, f, indent=2)

    with open(out / f"{company}_features.json", "w") as f:
        json.dump(all_features, f, indent=2)

    with open(out / f"{company}_comparison.json", "w") as f:
        json.dump(comparison_data, f, indent=2)

    return out
