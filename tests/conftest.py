"""Pytest configuration and shared fixtures."""

from collections.abc import Callable
from pathlib import Path

import pytest


@pytest.fixture
def create_pyproject_toml() -> Callable[[Path, str], Path]:
    """Factory fixture to create a pyproject.toml file with given content.

    Returns:
        A callable that accepts a directory path and content string,
        creates the pyproject.toml file, and returns its path.
    """

    def _create(directory: Path, content: str = "") -> Path:
        pyproject_path = directory / "pyproject.toml"
        if content:
            pyproject_path.write_text(content)
        else:
            # Default minimal pyproject.toml
            default_content = """[project]
name = "test-project"
version = "0.1.0"
description = "Test project"
requires-python = ">=3.10"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""
            pyproject_path.write_text(default_content)
        return pyproject_path

    return _create
