"""
Smoke tests for cli.py — tests wiring and error paths, not business logic.
"""
from unittest.mock import patch

from typer.testing import CliRunner

from src.connectionsbench.cli import app

runner = CliRunner()


def _mock_puzzles():
    from datetime import date
    from src.connectionsbench.models import Puzzle, Group, Tier
    return [Puzzle(
        schema_version=1, id=1, date=date(2023, 6, 12), has_images=False,
        words=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P"],
        groups=[
            Group(label="G1", tier=Tier.YELLOW, members=["A", "B", "C", "D"]),
            Group(label="G2", tier=Tier.GREEN, members=["E", "F", "G", "H"]),
            Group(label="G3", tier=Tier.BLUE, members=["I", "J", "K", "L"]),
            Group(label="G4", tier=Tier.PURPLE, members=["M", "N", "O", "P"]),
        ],
    )]


def test_run_requires_model():
    result = runner.invoke(app, ["run"])
    assert result.exit_code != 0


def test_run_command_exists():
    result = runner.invoke(app, ["run", "--help"])
    assert result.exit_code == 0
    assert "--model" in result.output


def test_results_command_exists():
    result = runner.invoke(app, ["results", "--help"])
    assert result.exit_code == 0


def test_run_no_puzzles(tmp_path):
    with patch("src.connectionsbench.cli.load_text_puzzles") as mock_load:
        mock_load.return_value = []
        result = runner.invoke(app, ["run", "--model", "openai:gpt-4o"])
    assert result.exit_code == 1
    assert "No puzzles found" in result.output


def test_run_dry_run(tmp_path):
    with patch("src.connectionsbench.cli.load_text_puzzles") as mock_load, \
            patch("src.connectionsbench.cli.check_duplicate_run") as mock_dup:
        mock_load.return_value = _mock_puzzles()
        mock_dup.return_value = (False, set())
        result = runner.invoke(app, ["run", "--model", "openai:gpt-4o", "--dry-run"])
    assert result.exit_code == 0
    assert "Dry run complete" in result.output


def test_results_no_results(tmp_path):
    result = runner.invoke(app, ["results", "--results-dir", str(tmp_path)])
    assert result.exit_code == 0
    assert "No results found" in result.output
