"""Visualize PR statistics."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


# Set default style
sns.set_style("whitegrid")


def create_overview_charts(
    monthly_stats: pd.DataFrame,
    output_file: str = "pr_analysis_overview.png",
    repo_name: str | None = None,
) -> Path:
    """
    Create overview charts with key metrics.

    Args:
        monthly_stats: Monthly statistics DataFrame
        output_file: Output file path
        repo_name: Repository name to display in title (optional)

    Returns:
        Path to the output file
    """
    df = monthly_stats.copy()
    df["month"] = pd.to_datetime(df["month"])
    df = df.sort_values("month").reset_index(drop=True)

    fig, axes = plt.subplots(2, 3, figsize=(20, 12))

    # Create title with repository name if provided
    title = f"{repo_name} PRs Analysis" if repo_name else "PRs Analysis"

    fig.suptitle(
        title,
        fontsize=16,
        fontweight="bold",
    )

    # 1. Merged PR count
    ax1 = axes[0, 0]
    sns.lineplot(
        data=df,
        x="month",
        y="merged_pr_count",
        marker="o",
        linewidth=2,
        markersize=6,
        ax=ax1,
        color="#2E86AB",
    )
    ax1.set_title("Monthly Merged PR Count", fontsize=14, fontweight="bold")
    ax1.set_xlabel("Month", fontsize=12)
    ax1.set_ylabel("Number of Merged PRs", fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis="x", rotation=45)

    # Add trend line
    z = np.polyfit(range(len(df)), df["merged_pr_count"], 1)
    p = np.poly1d(z)
    ax1.plot(
        df["month"], p(range(len(df))), "--", alpha=0.5, color="red", label="Trend"
    )
    ax1.legend(loc="upper left")

    # 2. Average time to merge
    ax2 = axes[0, 1]
    sns.lineplot(
        data=df,
        x="month",
        y="avg_time_to_merge_days",
        marker="s",
        linewidth=2,
        markersize=6,
        ax=ax2,
        color="#A23B72",
    )
    ax2.set_title("Average Time to Merge PRs", fontsize=14, fontweight="bold")
    ax2.set_xlabel("Month", fontsize=12)
    ax2.set_ylabel("Days to Merge", fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis="x", rotation=45)

    avg_days = df["avg_time_to_merge_days"].mean()
    ax2.axhline(
        y=avg_days,
        color="red",
        linestyle="--",
        alpha=0.5,
        label=f"Overall avg: {avg_days:.2f} days",
    )
    ax2.legend(loc="upper left")

    # 3. Unique authors
    ax3 = axes[1, 0]
    sns.barplot(
        data=df, x="month", y="unique_authors", ax=ax3, color="#F18F01", alpha=0.7
    )
    ax3.set_title("Number of Unique Authors per Month", fontsize=14, fontweight="bold")
    ax3.set_xlabel("Month", fontsize=12)
    ax3.set_ylabel("Number of Authors", fontsize=12)
    ax3.grid(True, alpha=0.3, axis="y")
    ax3.tick_params(axis="x", rotation=45)

    # 4. PRs per person
    ax4 = axes[1, 1]
    sns.lineplot(
        data=df,
        x="month",
        y="avg_prs_per_person",
        marker="D",
        linewidth=2,
        markersize=6,
        ax=ax4,
        color="#C73E1D",
    )
    ax4.set_title("Average PRs per Person", fontsize=14, fontweight="bold")
    ax4.set_xlabel("Month", fontsize=12)
    ax4.set_ylabel("PRs per Person", fontsize=12)
    ax4.grid(True, alpha=0.3)
    ax4.tick_params(axis="x", rotation=45)

    avg_prs_per_person = df["avg_prs_per_person"].mean()
    ax4.axhline(
        y=avg_prs_per_person,
        color="red",
        linestyle="--",
        alpha=0.5,
        label=f"Overall avg: {avg_prs_per_person:.2f} PRs/person",
    )
    ax4.legend(loc="upper left")

    # 5. Median total changes (additions + deletions) per month
    ax5 = axes[0, 2]
    if "median_total_changes" in df.columns:
        sns.lineplot(
            data=df,
            x="month",
            y="median_total_changes",
            marker="o",
            linewidth=2,
            markersize=6,
            ax=ax5,
            color="#00B4D8",
        )
        ax5.set_title("Median Total Changes per Month", fontsize=14, fontweight="bold")
        ax5.set_xlabel("Month", fontsize=12)
        ax5.set_ylabel("Lines Changed (additions + deletions)", fontsize=12)
        ax5.grid(True, alpha=0.3)
        ax5.tick_params(axis="x", rotation=45)

    # 6. Median changed files per month
    ax6 = axes[1, 2]
    if "median_changed_files" in df.columns:
        sns.lineplot(
            data=df,
            x="month",
            y="median_changed_files",
            marker="s",
            linewidth=2,
            markersize=6,
            ax=ax6,
            color="#90BE6D",
        )
        ax6.set_title("Median Changed Files per Month", fontsize=14, fontweight="bold")
        ax6.set_xlabel("Month", fontsize=12)
        ax6.set_ylabel("Number of Files", fontsize=12)
        ax6.grid(True, alpha=0.3)
        ax6.tick_params(axis="x", rotation=45)

    plt.tight_layout()
    output_path = Path(output_file)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✓ Saved overview chart: {output_path}")
    return output_path


def create_all_visualizations(
    monthly_stats: pd.DataFrame,
    output_dir: str | Path = ".",
    repo_name: str | None = None,
) -> dict[str, Path]:
    """
    Create all visualization charts.

    Args:
        monthly_stats: Monthly statistics DataFrame
        output_dir: Output directory
        repo_name: Repository name to display in title (optional)

    Returns:
        Dictionary of output file paths
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_files = {}

    # Overview chart (includes PR size metrics)
    overview_path = output_dir / "pr_analysis_overview.png"
    create_overview_charts(monthly_stats, str(overview_path), repo_name=repo_name)
    output_files["overview"] = overview_path

    print("\n✓ Created visualizations:")
    for path in output_files.values():
        print(f"  - {path}")

    return output_files
