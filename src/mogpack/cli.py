"""CLI for mogpack - initialize development tooling in Python projects."""

import argparse
import sys
from pathlib import Path


def get_nitpick_github_url(version: str = "main") -> str:
    """Get the GitHub URL for the mogpack nitpick style file."""
    return f"github://matthewgulliver/mogpack@{version}/nitpick-style.toml"


def init_project(git_ref: str = "main") -> int:
    """Initialize mogpack configuration in the current project.

    Args:
        git_ref: Git reference (branch, tag, commit) to use for the style file

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    project_root = Path.cwd()
    pyproject_path = project_root / "pyproject.toml"

    if not pyproject_path.exists():
        print("Error: pyproject.toml not found in current directory", file=sys.stderr)
        print("Please run this command from your project root", file=sys.stderr)
        return 1

    # Read existing pyproject.toml
    content = pyproject_path.read_text()

    # Check if [tool.nitpick] already exists
    if "[tool.nitpick]" in content:
        print("Warning: [tool.nitpick] section already exists in pyproject.toml")
        print("Current configuration will be preserved")
        return 0

    # Add nitpick configuration
    style_url = get_nitpick_github_url(git_ref)
    nitpick_config = f'\n[tool.nitpick]\nstyle = ["{style_url}"]\nignore_styles = []\n'

    # Append to pyproject.toml
    with pyproject_path.open("a") as f:
        f.write(nitpick_config)

    print(f"✅ Added mogpack configuration to {pyproject_path}")
    print(f"   Style URL: {style_url}")
    print("\nNext steps:")
    print("  1. Run 'nitpick check' to see what needs to be configured")
    print("  2. Run 'nitpick fix' to automatically apply configuration")
    print("  3. Install mogpack as a dev dependency:")
    print("     uv add --dev mogpack")

    return 0


def main() -> int:
    """Main entry point for the mogpack CLI."""
    parser = argparse.ArgumentParser(
        description="Initialize mogpack development tooling in your Python project"
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version="mogpack 0.1.0",
    )
    parser.add_argument(
        "--ref",
        default="main",
        help="Git reference (branch, tag, commit) to use for style file (default: main)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init command
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize mogpack in the current project",
    )
    init_parser.add_argument(
        "--ref",
        default="main",
        help="Git reference (branch, tag, commit) to use for style file (default: main)",
    )

    args = parser.parse_args()

    if args.command == "init":
        return init_project(git_ref=args.ref)

    # Default to init if no command specified
    return init_project(git_ref=args.ref)


if __name__ == "__main__":
    sys.exit(main())
