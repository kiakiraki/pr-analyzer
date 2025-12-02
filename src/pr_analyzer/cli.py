"""Command-line interface for PR Analyzer."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import click
import pandas as pd

from .analyzer import (
    calculate_monthly_statistics,
    process_pr_data,
    save_statistics,
)
from .fetcher import fetch_pr_data, load_pr_data
from .visualizer import create_all_visualizations


def parse_timezone(tz_offset: int) -> timezone:
    """
    Parse timezone offset to timezone object.

    Args:
        tz_offset: UTC offset in hours (e.g., 9 for JST, -5 for EST)

    Returns:
        timezone object
    """
    return timezone(timedelta(hours=tz_offset))


@click.group()
@click.version_option()
def main():
    """PR Analyzer - Analyze PR statistics and productivity metrics."""


@main.command()
@click.option("--repo", required=True, help='Repository in format "owner/repo"')
@click.option("--label", default=None, help="Label to filter PRs (optional)")
@click.option(
    "--exclude-label",
    multiple=True,
    default=["dependencies"],
    help="Label(s) to exclude from results (default: dependencies)",
)
@click.option(
    "--output", "-o", default="pr_data_with_diff.json", help="Output JSON file"
)
@click.option("--no-diff", is_flag=True, help="Skip diff statistics")
@click.option(
    "--limit",
    default=10000,
    type=int,
    help="Maximum number of PRs to fetch (default: 10000)",
)
@click.option(
    "--state",
    default="merged",
    type=click.Choice(["all", "merged", "open", "closed"]),
    help="PR state to fetch (default: merged)",
)
@click.option(
    "--timeout", default=600, type=int, help="Command timeout in seconds (default: 600)"
)
def fetch(
    repo: str,
    label: str | None,
    exclude_label: tuple[str, ...],
    output: str,
    no_diff: bool,
    limit: int,
    state: str,
    timeout: int,
):
    """Fetch PR data from GitHub."""
    try:
        output_path = fetch_pr_data(
            repo=repo,
            label=label,
            exclude_labels=list(exclude_label),
            output_file=output,
            include_diff_stats=not no_diff,
            limit=limit,
            state=state,
            timeout=timeout,
        )
        click.echo(f"\n✓ Success! Data saved to: {output_path}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort from e


@main.command()
@click.option("--input", "-i", "input_file", required=True, help="Input JSON file")
@click.option("--output-dir", "-o", default=".", help="Output directory")
@click.option(
    "--cutoff-date",
    default=None,
    help="Filter PRs after this date (YYYY-MM-DD, optional)",
)
@click.option(
    "--end-date",
    default=None,
    help="Filter PRs before this date (YYYY-MM-DD, optional)",
)
@click.option(
    "--timezone",
    default=9,
    type=int,
    help="UTC offset in hours (default: 9 for JST)",
)
def analyze(
    input_file: str,
    output_dir: str,
    cutoff_date: str | None,
    end_date: str | None,
    timezone: int,
):
    """Analyze PR data and generate statistics."""
    try:
        # Parse timezone
        tz = parse_timezone(timezone)

        # Load data
        click.echo(f"Loading PR data from {input_file}...")
        prs = load_pr_data(input_file)
        click.echo(f"✓ Loaded {len(prs)} PRs")

        # Parse cutoff date
        cutoff = None
        if cutoff_date:
            cutoff = datetime.strptime(cutoff_date, "%Y-%m-%d").replace(tzinfo=tz)
            click.echo(f"✓ Filtering PRs after {cutoff_date}")

        # Parse end date
        end = None
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=tz)
            click.echo(f"✓ Filtering PRs before {end_date}")

        # Process data
        click.echo("\nProcessing PR data...")
        df = process_pr_data(prs, cutoff_date=cutoff, end_date=end, tz=tz)
        click.echo(f"✓ Processed {len(df)} PRs")

        # Calculate statistics
        click.echo("\nCalculating monthly statistics...")
        monthly_stats = calculate_monthly_statistics(df)
        click.echo(f"✓ Calculated statistics for {len(monthly_stats)} months")

        # Save statistics
        click.echo("\nSaving statistics...")
        save_statistics(monthly_stats, df, output_dir=output_dir)

        click.echo("\n✓ Analysis complete!")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort from e


@main.command()
@click.option(
    "--input", "-i", "input_file", required=True, help="Monthly statistics JSON file"
)
@click.option("--output-dir", "-o", default=".", help="Output directory")
@click.option(
    "--repo",
    default=None,
    help='Repository name to display in title (e.g., "owner/repo")',
)
def visualize(input_file: str, output_dir: str, repo: str | None):
    """Generate visualization charts."""
    try:
        # Load monthly statistics
        click.echo(f"Loading monthly statistics from {input_file}...")
        monthly_stats = pd.read_json(input_file)
        click.echo(f"✓ Loaded statistics for {len(monthly_stats)} months")

        # Create visualizations
        click.echo("\nGenerating visualizations...")
        create_all_visualizations(monthly_stats, output_dir=output_dir, repo_name=repo)

        click.echo("\n✓ Visualization complete!")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort from e


@main.command()
@click.option("--repo", required=True, help='Repository in format "owner/repo"')
@click.option("--label", default=None, help="Label to filter PRs (optional)")
@click.option(
    "--exclude-label",
    multiple=True,
    default=["dependencies"],
    help="Label(s) to exclude from results (default: dependencies)",
)
@click.option("--output-dir", "-o", default=".", help="Output directory")
@click.option(
    "--cutoff-date",
    default=None,
    help="Filter PRs after this date (YYYY-MM-DD, optional)",
)
@click.option(
    "--end-date",
    default=None,
    help="Filter PRs before this date (YYYY-MM-DD, optional)",
)
@click.option(
    "--limit",
    default=10000,
    type=int,
    help="Maximum number of PRs to fetch (default: 10000)",
)
@click.option(
    "--state",
    default="merged",
    type=click.Choice(["all", "merged", "open", "closed"]),
    help="PR state to fetch (default: merged)",
)
@click.option(
    "--timeout", default=600, type=int, help="Command timeout in seconds (default: 600)"
)
@click.option(
    "--timezone",
    default=9,
    type=int,
    help="UTC offset in hours (default: 9 for JST)",
)
def run(
    repo: str,
    label: str | None,
    exclude_label: tuple[str, ...],
    output_dir: str,
    cutoff_date: str | None,
    end_date: str | None,
    limit: int,
    state: str,
    timeout: int,
    timezone: int,
):
    """Run complete analysis pipeline (fetch + analyze + visualize)."""
    try:
        # Parse timezone
        tz = parse_timezone(timezone)

        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)

        # 1. Fetch data
        click.echo("=" * 70)
        click.echo("STEP 1: Fetching PR data")
        click.echo("=" * 70)
        data_file = output_dir_path / "pr_data_with_diff.json"
        fetch_pr_data(
            repo=repo,
            label=label,
            exclude_labels=list(exclude_label),
            output_file=str(data_file),
            include_diff_stats=True,
            limit=limit,
            state=state,
            timeout=timeout,
        )

        # 2. Analyze
        click.echo("\n" + "=" * 70)
        click.echo("STEP 2: Analyzing PR data")
        click.echo("=" * 70)

        prs = load_pr_data(str(data_file))
        click.echo(f"✓ Loaded {len(prs)} PRs")

        # Parse cutoff date
        cutoff = None
        if cutoff_date:
            cutoff = datetime.strptime(cutoff_date, "%Y-%m-%d").replace(tzinfo=tz)
            click.echo(f"✓ Filtering PRs after {cutoff_date}")

        # Parse end date
        end = None
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=tz)
            click.echo(f"✓ Filtering PRs before {end_date}")

        df = process_pr_data(prs, cutoff_date=cutoff, end_date=end, tz=tz)
        click.echo(f"✓ Processed {len(df)} PRs")

        monthly_stats = calculate_monthly_statistics(df)
        click.echo(f"✓ Calculated statistics for {len(monthly_stats)} months")

        save_statistics(monthly_stats, df, output_dir=str(output_dir_path))

        # 3. Visualize
        click.echo("\n" + "=" * 70)
        click.echo("STEP 3: Generating visualizations")
        click.echo("=" * 70)

        create_all_visualizations(
            monthly_stats, output_dir=str(output_dir_path), repo_name=repo
        )

        # Summary
        click.echo("\n" + "=" * 70)
        click.echo("✓ ANALYSIS COMPLETE!")
        click.echo("=" * 70)
        click.echo(f"\nResults saved to: {output_dir_path.absolute()}")
        click.echo("\nGenerated files:")
        click.echo("  - pr_data_with_diff.json (raw data)")
        click.echo("  - monthly_statistics.csv")
        click.echo("  - monthly_statistics.json")
        click.echo("  - pr_details.csv")
        click.echo("  - pr_details.json")
        click.echo("  - pr_analysis_overview.png")

    except Exception as e:
        click.echo(f"\n✗ Error: {e}", err=True)
        raise click.Abort from e


if __name__ == "__main__":
    main()
