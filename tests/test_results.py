import pytest

from src.connectionsbench.models import PuzzleResult, Tier
from src.connectionsbench.results import save_result, load_results, get_run_puzzle_ids, check_duplicate_run, \
    calculate_model_metrics

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

MOCK_RESULT_3 = PuzzleResult(
    puzzle_id=3,
    model="openai:gpt-4o",
    solved=False,
    groups_correct=0,
    tier_results={Tier.YELLOW: False, Tier.GREEN: False, Tier.BLUE: False, Tier.PURPLE: False},
)


@pytest.fixture
def results_dir(tmp_path):
    return tmp_path


@pytest.fixture
def populated_results_dir(tmp_path):
    path = tmp_path / "openai_gpt-4o.jsonl"
    with open(path, "w") as f:
        f.write(MOCK_RESULT_1.model_dump_json() + "\n")
        f.write(MOCK_RESULT_2.model_dump_json() + "\n")
        f.write(MOCK_RESULT_3.model_dump_json() + "\n")
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


def test_load_results_returns_puzzle_results(populated_results_dir):
    results = load_results("openai:gpt-4o", populated_results_dir)
    assert len(results) == 3
    assert all(isinstance(r, PuzzleResult) for r in results)


def test_load_results_returns_empty_when_no_file(results_dir):
    assert load_results("openai:gpt-4o", results_dir) == []


# get_run_puzzle_ids tests

def test_get_run_puzzle_ids_returns_correct_ids(populated_results_dir):
    ids = get_run_puzzle_ids("openai:gpt-4o", populated_results_dir)
    assert ids == {1, 2, 3}


def test_get_run_puzzle_ids_returns_empty_when_no_file(results_dir):
    assert get_run_puzzle_ids("openai:gpt-4o", results_dir) == set()


# check_duplicate_run tests

def test_check_duplicate_run_all_duplicate(populated_results_dir):
    all_dup, overlap = check_duplicate_run("openai:gpt-4o", [1, 2, 3], populated_results_dir)
    assert all_dup is True
    assert overlap == {1, 2, 3}


def test_check_duplicate_run_partial(populated_results_dir):
    all_dup, overlap = check_duplicate_run("openai:gpt-4o", [1, 2, 99], populated_results_dir)
    assert all_dup is False
    assert overlap == {1, 2}


def test_check_duplicate_run_none(populated_results_dir):
    all_dup, overlap = check_duplicate_run("openai:gpt-4o", [99, 100], populated_results_dir)
    assert all_dup is False
    assert overlap == set()


# calculate_model_metrics tests

def test_calculate_model_metrics_puzzle_count(populated_results_dir):
    results = load_results("openai:gpt-4o", populated_results_dir)
    metrics = calculate_model_metrics("openai:gpt-4o", results)
    assert metrics["puzzle_count"] == 3


def test_calculate_model_metrics_solve_rate(populated_results_dir):
    results = load_results("openai:gpt-4o", populated_results_dir)
    metrics = calculate_model_metrics("openai:gpt-4o", results)
    assert metrics["solve_pct"] == pytest.approx(33.33, rel=0.01)


def test_calculate_model_metrics_avg_groups(populated_results_dir):
    results = load_results("openai:gpt-4o", populated_results_dir)
    metrics = calculate_model_metrics("openai:gpt-4o", results)
    assert metrics["avg_groups"] == pytest.approx(2.0)


def test_calculate_model_metrics_purple_gap(populated_results_dir):
    results = load_results("openai:gpt-4o", populated_results_dir)
    metrics = calculate_model_metrics("openai:gpt-4o", results)
    assert metrics["purple_gap"] == pytest.approx(33.33, rel=0.01)


def test_calculate_model_metrics_tier_percentages(populated_results_dir):
    results = load_results("openai:gpt-4o", populated_results_dir)
    metrics = calculate_model_metrics("openai:gpt-4o", results)
    assert metrics["yellow_pct"] == pytest.approx(66.66, rel=0.01)
    assert metrics["green_pct"] == pytest.approx(66.66, rel=0.01)
    assert metrics["blue_pct"] == pytest.approx(33.33, rel=0.01)
    assert metrics["purple_pct"] == pytest.approx(33.33, rel=0.01)


def test_calculate_model_metrics_model(populated_results_dir):
    results = load_results("openai:gpt-4o", populated_results_dir)
    metrics = calculate_model_metrics("openai:gpt-4o", results)
    assert metrics["model"] == "openai:gpt-4o"


def test_calculate_model_metrics_ids_period(populated_results_dir):
    results = load_results("openai:gpt-4o", populated_results_dir)
    metrics = calculate_model_metrics("openai:gpt-4o", results)
    assert metrics["min_puzzle_id"] == 1
    assert metrics["max_puzzle_id"] == 3
