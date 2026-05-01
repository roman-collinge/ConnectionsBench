import pytest

from src.connectionsbench.models import PuzzleResult, Tier
from src.connectionsbench.results import save_result, load_results

MOCK_RESULT_1 = PuzzleResult(
    puzzle_id=1,
    model="openai:gpt-4o",
    solved=True,
    groups_correct=4,
    tier_results={Tier.YELLOW: True, Tier.GREEN: True, Tier.BLUE: True, Tier.PURPLE: True},
)


@pytest.fixture
def results_dir(tmp_path):
    return tmp_path


def test_save_result_creates_file(results_dir):
    save_result(MOCK_RESULT_1, "openai:gpt-4o", results_dir)
    assert (results_dir / "openai_gpt-4o.jsonl").exists()


def test_load_results_returns_empty_when_no_file(results_dir):
    assert load_results("openai:gpt-4o", results_dir) == []
