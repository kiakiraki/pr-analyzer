"""Fetch PR data from GitHub."""

import json
import re
import subprocess
from pathlib import Path


def validate_repo_format(repo: str) -> None:
    """
    Validate repository format (owner/repo).

    Args:
        repo: Repository string to validate

    Raises:
        ValueError: If repository format is invalid
    """
    pattern = r"^[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+$"
    if not re.match(pattern, repo):
        msg = (
            f"Invalid repository format: '{repo}'. "
            "Expected format: 'owner/repo' (e.g., 'octocat/hello-world')"
        )
        raise ValueError(msg)


def fetch_pr_data(
    repo: str,
    label: str | None = None,
    exclude_labels: list[str] | None = None,
    output_file: str | None = None,
    include_diff_stats: bool = True,
    limit: int = 10000,
    state: str = "merged",
    timeout: int = 600,
) -> Path:
    """
    Fetch PR data from GitHub using gh CLI.

    Args:
        repo: Repository in format "owner/repo"
        label: Label to filter PRs (optional, if None fetches all PRs)
        exclude_labels: List of labels to exclude from results
        output_file: Output file path. If None, uses default.
        include_diff_stats: Whether to include diff statistics
        limit: Maximum number of PRs to fetch (default: 10000)
        state: PR state to fetch - "all", "merged", "open", "closed" (default: "merged")
        timeout: Command timeout in seconds (default: 600)

    Returns:
        Path to the output JSON file
    """
    # Validate repository format
    validate_repo_format(repo)

    if output_file is None:
        output_file = f"pr_data_{'with_diff' if include_diff_stats else 'raw'}.json"

    output_path = Path(output_file)

    # Build gh command
    fields = [
        "number",
        "title",
        "author",
        "createdAt",
        "mergedAt",
        "state",
        "labels",
    ]

    if include_diff_stats:
        fields.extend(["additions", "deletions", "changedFiles"])

    cmd = [
        "gh",
        "pr",
        "list",
        "--repo",
        repo,
    ]

    # Add label filter only if specified
    if label is not None:
        cmd.extend(["--label", label])

    cmd.extend(
        [
            "--state",
            state,
            "--limit",
            str(limit),
            "--json",
            ",".join(fields),
        ]
    )

    print(f"Fetching PR data from {repo}...")
    print(f"State: {state}, Limit: {limit}")
    if label:
        print(f"Filtering by label: {label}")
    else:
        print("Fetching all PRs (no label filter)")
    if exclude_labels:
        print(f"Excluding labels: {', '.join(exclude_labels)}")
    print(f"Command: {' '.join(cmd)}")

    result = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Failed to fetch PR data: {result.stderr}")

    # Parse and filter data
    data = json.loads(result.stdout)

    # Filter out PRs with excluded labels
    if exclude_labels:
        original_count = len(data)
        exclude_set = set(exclude_labels)
        data = [
            pr
            for pr in data
            if not any(
                label_obj.get("name") in exclude_set
                for label_obj in pr.get("labels", [])
            )
        ]
        filtered_count = original_count - len(data)
        print(
            f"✓ Excluded {filtered_count} PRs with labels: {', '.join(exclude_labels)}"
        )

    # Write to file
    with output_path.open("w") as f:
        json.dump(data, f, indent=2)

    print(f"✓ Fetched {len(data)} PRs")
    print(f"✓ Saved to {output_path}")

    return output_path


def load_pr_data(file_path: str) -> list[dict]:
    """Load PR data from JSON file."""
    path = Path(file_path)
    with path.open() as f:
        return json.load(f)
