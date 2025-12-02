"""Analyze PR data and calculate statistics."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd


# Default timezone (JST)
DEFAULT_TIMEZONE = timezone(timedelta(hours=9))


def process_pr_data(
    prs: list[dict],
    cutoff_date: datetime | None = None,
    end_date: datetime | None = None,
    tz: timezone = DEFAULT_TIMEZONE,
) -> pd.DataFrame:
    """
    Process raw PR data into a DataFrame.

    Args:
        prs: List of PR dictionaries
        cutoff_date: Filter PRs created after this date
        end_date: Filter PRs created before this date
        tz: Timezone for date conversion (default: JST/UTC+9)

    Returns:
        DataFrame with processed PR data
    """
    filtered_prs = []

    for pr in prs:
        created_at = datetime.fromisoformat(
            pr["createdAt"].replace("Z", "+00:00")
        ).astimezone(tz)

        if (cutoff_date is None or created_at >= cutoff_date) and (
            end_date is None or created_at <= end_date
        ):
            pr_data = {
                "number": pr["number"],
                "title": pr["title"],
                "author": pr["author"]["login"] if pr["author"] else "unknown",
                "created_at": created_at.isoformat(),
                "merged_at": None,
                "state": pr["state"],
                "month": created_at.strftime("%Y-%m"),
                "year": created_at.year,
                "time_to_merge_hours": None,
                "time_to_merge_days": None,
            }

            # Calculate time to merge if merged
            if pr["mergedAt"]:
                merged_at = datetime.fromisoformat(
                    pr["mergedAt"].replace("Z", "+00:00")
                ).astimezone(tz)
                pr_data["merged_at"] = merged_at.isoformat()
                time_to_merge_hours = (merged_at - created_at).total_seconds() / 3600
                pr_data["time_to_merge_hours"] = time_to_merge_hours
                pr_data["time_to_merge_days"] = time_to_merge_hours / 24

            # Add diff stats if available
            if "additions" in pr:
                pr_data["additions"] = pr["additions"]
                pr_data["deletions"] = pr["deletions"]
                pr_data["changed_files"] = pr["changedFiles"]
                pr_data["total_changes"] = pr["additions"] + pr["deletions"]

            filtered_prs.append(pr_data)

    df = pd.DataFrame(filtered_prs)
    df["created_at"] = pd.to_datetime(df["created_at"])

    return df


def calculate_monthly_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate monthly statistics from PR data.

    Args:
        df: DataFrame with PR data

    Returns:
        DataFrame with monthly statistics
    """
    # Filter only merged PRs
    df_merged: pd.DataFrame = df[df["time_to_merge_days"].notna()].copy()

    monthly_data = {}

    for month in df_merged["month"].unique():
        month_prs: pd.DataFrame = df_merged[df_merged["month"] == month]

        stats = {
            "month": month,
            "merged_pr_count": len(month_prs),
            "avg_time_to_merge_hours": month_prs["time_to_merge_hours"].mean(),
            "avg_time_to_merge_days": month_prs["time_to_merge_hours"].mean() / 24,
            "unique_authors": month_prs["author"].nunique(),
        }

        # Calculate PRs per person
        stats["avg_prs_per_person"] = (
            stats["merged_pr_count"] / stats["unique_authors"]
            if stats["unique_authors"] > 0
            else 0
        )

        # Add diff stats if available
        if "total_changes" in month_prs.columns:
            stats["median_total_changes"] = month_prs["total_changes"].median()
            stats["median_changed_files"] = month_prs["changed_files"].median()

        monthly_data[month] = stats

    monthly_df = pd.DataFrame(monthly_data.values())
    return monthly_df.sort_values("month").reset_index(drop=True)


def save_statistics(
    monthly_stats: pd.DataFrame,
    pr_details: pd.DataFrame,
    output_dir: str | Path = ".",
) -> dict[str, Path]:
    """
    Save statistics to CSV and JSON files.

    Args:
        monthly_stats: Monthly statistics DataFrame
        pr_details: Detailed PR data DataFrame
        output_dir: Output directory

    Returns:
        Dictionary of output file paths
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_files = {}

    # Save monthly statistics
    monthly_csv = output_dir / "monthly_statistics.csv"
    monthly_stats.to_csv(monthly_csv, index=False)
    output_files["monthly_csv"] = monthly_csv

    monthly_json = output_dir / "monthly_statistics.json"
    monthly_stats.to_json(monthly_json, orient="records", indent=2)
    output_files["monthly_json"] = monthly_json

    # Save PR details
    details_csv = output_dir / "pr_details.csv"
    pr_details.to_csv(details_csv, index=False)
    output_files["details_csv"] = details_csv

    details_json = output_dir / "pr_details.json"
    pr_details.to_json(details_json, orient="records", indent=2)
    output_files["details_json"] = details_json

    print("\n✓ Saved statistics:")
    for path in output_files.values():
        print(f"  - {path}")

    return output_files
