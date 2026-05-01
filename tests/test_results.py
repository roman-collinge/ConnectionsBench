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

MOCK_RESULT_2 = PuzzleResult(
    puzzle_id=2,
    model="openai:gpt-4o",
    solved=False,
    groups_correct=2,
    tier_results={Tier.YELLOW: True, Tier.GREEN: True, Tier.BLUE: False, Tier.PURPLE: False},
)


@pytest.fixture
def results_dir(tmp_path):
    return tmp_path


# save_result tests
def test_save_result_creates_file(results_dir):
    save_result(MOCK_RESULT_1, "openai:gpt-4o", results_dir)
    assert (results_dir / "openai_gpt-4o.jsonl").exists()


def test_save_result_appends(results_dir):
    save_result(MOCK_RESULT_1, "openai:gpt-4o", results_dir)
    save_result(MOCK_RESULT_2, "openai:gpt-4o", results_dir)
    results = load_results("openai:gpt-4o", results_dir)
    assert len(results) == 2


def test_load_results_returns_empty_when_no_file(results_dir):
    assert load_results("openai:gpt-4o", results_dir) == []
