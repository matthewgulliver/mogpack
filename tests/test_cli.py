"""Tests for mogpack CLI functionality."""

import sys
from collections.abc import Callable
from pathlib import Path

import pytest

from mogpack.cli import get_nitpick_github_url, init_project, main


class TestGetNitpickGithubUrl:
    """Tests for get_nitpick_github_url function."""

    def test_returns_github_url_with_default_version(self) -> None:
        """Should return GitHub URL with 'main' when no version specified."""
        url = get_nitpick_github_url()

        assert url == "github://matthewgulliver/mogpack@main/nitpick-style.toml"

    def test_returns_github_url_with_custom_version(self) -> None:
        """Should return GitHub URL with specified version."""
        url = get_nitpick_github_url(version="v1.0.0")

        assert url == "github://matthewgulliver/mogpack@v1.0.0/nitpick-style.toml"

    def test_returns_github_url_with_commit_hash(self) -> None:
        """Should return GitHub URL with commit hash when provided."""
        url = get_nitpick_github_url(version="abc123def")

        assert url == "github://matthewgulliver/mogpack@abc123def/nitpick-style.toml"

    def test_returns_github_url_with_branch_name(self) -> None:
        """Should return GitHub URL with branch name when provided."""
        url = get_nitpick_github_url(version="develop")

        assert url == "github://matthewgulliver/mogpack@develop/nitpick-style.toml"


class TestInitProject:
    """Tests for init_project function."""

    def test_adds_nitpick_config_to_pyproject_toml(
        self,
        tmp_path: Path,
        create_pyproject_toml: Callable[[Path, str], Path],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Should add [tool.nitpick] section to pyproject.toml."""
        create_pyproject_toml(tmp_path)
        monkeypatch.chdir(tmp_path)

        exit_code = init_project()

        pyproject_content = (tmp_path / "pyproject.toml").read_text()
        assert exit_code == 0
        assert "[tool.nitpick]" in pyproject_content
        assert 'style = ["github://matthewgulliver/mogpack@main/nitpick-style.toml"]' in pyproject_content
        assert "ignore_styles = []" in pyproject_content

    def test_adds_nitpick_config_with_custom_git_ref(
        self,
        tmp_path: Path,
        create_pyproject_toml: Callable[[Path, str], Path],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Should use custom git ref when specified."""
        create_pyproject_toml(tmp_path)
        monkeypatch.chdir(tmp_path)

        exit_code = init_project(git_ref="v1.0.0")

        pyproject_content = (tmp_path / "pyproject.toml").read_text()
        assert exit_code == 0
        assert 'style = ["github://matthewgulliver/mogpack@v1.0.0/nitpick-style.toml"]' in pyproject_content

    def test_returns_error_when_pyproject_toml_not_found(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Should return error code when pyproject.toml doesn't exist."""
        monkeypatch.chdir(tmp_path)

        exit_code = init_project()

        captured = capsys.readouterr()
        assert exit_code == 1
        assert "Error: pyproject.toml not found in current directory" in captured.err
        assert "Please run this command from your project root" in captured.err

    def test_preserves_existing_nitpick_config(
        self,
        tmp_path: Path,
        create_pyproject_toml: Callable[[Path, str], Path],
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Should not modify pyproject.toml if [tool.nitpick] already exists."""
        existing_content = """[project]
name = "test-project"
version = "0.1.0"

[tool.nitpick]
style = ["github://other/repo@main/style.toml"]
"""
        create_pyproject_toml(tmp_path, existing_content)
        monkeypatch.chdir(tmp_path)

        exit_code = init_project()

        pyproject_content = (tmp_path / "pyproject.toml").read_text()
        captured = capsys.readouterr()
        assert exit_code == 0
        assert pyproject_content == existing_content
        assert "Warning: [tool.nitpick] section already exists" in captured.out
        assert "Current configuration will be preserved" in captured.out

    def test_success_message_includes_style_url(
        self,
        tmp_path: Path,
        create_pyproject_toml: Callable[[Path, str], Path],
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Should display success message with style URL."""
        create_pyproject_toml(tmp_path)
        monkeypatch.chdir(tmp_path)

        init_project(git_ref="v2.0.0")

        captured = capsys.readouterr()
        assert "✅ Added mogpack configuration" in captured.out
        assert "Style URL: github://matthewgulliver/mogpack@v2.0.0/nitpick-style.toml" in captured.out

    def test_success_message_includes_next_steps(
        self,
        tmp_path: Path,
        create_pyproject_toml: Callable[[Path, str], Path],
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Should display next steps in success message."""
        create_pyproject_toml(tmp_path)
        monkeypatch.chdir(tmp_path)

        init_project()

        captured = capsys.readouterr()
        assert "Next steps:" in captured.out
        assert "nitpick check" in captured.out
        assert "nitpick fix" in captured.out
        assert "uv add --dev mogpack" in captured.out

    def test_appends_config_to_existing_pyproject_content(
        self,
        tmp_path: Path,
        create_pyproject_toml: Callable[[Path, str], Path],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Should append nitpick config without removing existing content."""
        existing_content = """[project]
name = "my-project"
version = "1.0.0"

[tool.mypy]
strict = true
"""
        create_pyproject_toml(tmp_path, existing_content)
        monkeypatch.chdir(tmp_path)

        init_project()

        pyproject_content = (tmp_path / "pyproject.toml").read_text()
        assert "[project]" in pyproject_content
        assert 'name = "my-project"' in pyproject_content
        assert "[tool.mypy]" in pyproject_content
        assert "strict = true" in pyproject_content
        assert "[tool.nitpick]" in pyproject_content


class TestMain:
    """Tests for main CLI entry point."""

    def test_init_command_initializes_project(
        self,
        tmp_path: Path,
        create_pyproject_toml: Callable[[Path, str], Path],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Should initialize project when 'init' command is used."""
        create_pyproject_toml(tmp_path)
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(sys, "argv", ["mogpack", "init"])

        exit_code = main()

        pyproject_content = (tmp_path / "pyproject.toml").read_text()
        assert exit_code == 0
        assert "[tool.nitpick]" in pyproject_content

    def test_init_command_with_ref_argument(
        self,
        tmp_path: Path,
        create_pyproject_toml: Callable[[Path, str], Path],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Should use specified ref when provided to init command."""
        create_pyproject_toml(tmp_path)
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(sys, "argv", ["mogpack", "init", "--ref", "v3.0.0"])

        exit_code = main()

        pyproject_content = (tmp_path / "pyproject.toml").read_text()
        assert exit_code == 0
        assert 'style = ["github://matthewgulliver/mogpack@v3.0.0/nitpick-style.toml"]' in pyproject_content

    def test_no_command_defaults_to_init(
        self,
        tmp_path: Path,
        create_pyproject_toml: Callable[[Path, str], Path],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Should run init when no command is specified."""
        create_pyproject_toml(tmp_path)
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(sys, "argv", ["mogpack"])

        exit_code = main()

        pyproject_content = (tmp_path / "pyproject.toml").read_text()
        assert exit_code == 0
        assert "[tool.nitpick]" in pyproject_content

    def test_no_command_with_ref_argument(
        self,
        tmp_path: Path,
        create_pyproject_toml: Callable[[Path, str], Path],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Should use ref argument when no command specified."""
        create_pyproject_toml(tmp_path)
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(sys, "argv", ["mogpack", "--ref", "develop"])

        exit_code = main()

        pyproject_content = (tmp_path / "pyproject.toml").read_text()
        assert exit_code == 0
        assert 'style = ["github://matthewgulliver/mogpack@develop/nitpick-style.toml"]' in pyproject_content

    def test_version_flag_displays_version(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Should display version and exit when --version flag is used."""
        monkeypatch.setattr(sys, "argv", ["mogpack", "--version"])

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0

    def test_version_short_flag_displays_version(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Should display version and exit when -v flag is used."""
        monkeypatch.setattr(sys, "argv", ["mogpack", "-v"])

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0

    def test_init_command_returns_error_code_on_failure(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Should return error code when init fails."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(sys, "argv", ["mogpack", "init"])

        exit_code = main()

        assert exit_code == 1


class TestMainModuleExecution:
    """Tests for module execution as script."""

    def test_script_execution_calls_main(
        self,
        tmp_path: Path,
        create_pyproject_toml: Callable[[Path, str], Path],
    ) -> None:
        """Should execute main() and exit with correct code when run as script."""
        import subprocess

        create_pyproject_toml(tmp_path)

        # Run the CLI module directly as a script
        result = subprocess.run(
            [sys.executable, "-m", "mogpack.cli", "init"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "[tool.nitpick]" in (tmp_path / "pyproject.toml").read_text()
