"""
Tests for fetch_puzzles.py
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.fetch_puzzles import fetch_puzzle, load_existing_dataset, parse_response

MOCK_RESPONSE = {
    "categories": [
        {"title": "EASY GROUP", "cards": [{"content": "A"}, {"content": "B"}, {"content": "C"}, {"content": "D"}]},
        {"title": "MEDIUM GROUP", "cards": [{"content": "E"}, {"content": "F"}, {"content": "G"}, {"content": "H"}]},
        {"title": "HARD GROUP", "cards": [{"content": "I"}, {"content": "J"}, {"content": "K"}, {"content": "L"}]},
        {"title": "TRICKY GROUP", "cards": [{"content": "M"}, {"content": "N"}, {"content": "O"}, {"content": "P"}]},
    ]
}

MOCK_IMAGE_RESPONSE = {
    "categories": [
        {
            "title": "IMAGE GROUP",
            "cards": [
                {"position": 0, "image_url": "https://example.com/a.png"},
                {"position": 1, "image_url": "https://example.com/b.png"},
                {"position": 2, "image_url": "https://example.com/c.png"},
                {"position": 3, "image_url": "https://example.com/d.png"},
            ],
        },
        {"title": "MEDIUM GROUP", "cards": [{"content": "E"}, {"content": "F"}, {"content": "G"}, {"content": "H"}]},
        {"title": "HARD GROUP", "cards": [{"content": "I"}, {"content": "J"}, {"content": "K"}, {"content": "L"}]},
        {"title": "TRICKY GROUP", "cards": [{"content": "M"}, {"content": "N"}, {"content": "O"}, {"content": "P"}]},
    ]
}


def test_parse_response_tiers_assigned_by_index():
    result = parse_response(MOCK_RESPONSE, puzzle_id=1, date="2023-06-12")
    assert result["groups"][0]["tier"] == "Yellow"
    assert result["groups"][1]["tier"] == "Green"
    assert result["groups"][2]["tier"] == "Blue"
    assert result["groups"][3]["tier"] == "Purple"


def test_parse_response_words_contains_all_16():
    result = parse_response(MOCK_RESPONSE, puzzle_id=1, date="2023-06-12")
    assert len(result["words"]) == 16


def test_parse_response_words_order_matches_groups():
    result = parse_response(MOCK_RESPONSE, puzzle_id=1, date="2023-06-12")
    assert result["words"][:4] == ["A", "B", "C", "D"]
    assert result["words"][12:] == ["M", "N", "O", "P"]


def test_parse_response_group_labels_preserved():
    result = parse_response(MOCK_RESPONSE, puzzle_id=1, date="2023-06-12")
    assert result["groups"][0]["label"] == "EASY GROUP"
    assert result["groups"][3]["label"] == "TRICKY GROUP"


def test_parse_response_group_members_correct():
    result = parse_response(MOCK_RESPONSE, puzzle_id=1, date="2023-06-12")
    assert result["groups"][0]["members"] == ["A", "B", "C", "D"]


def test_parse_response_id_and_date_passed_through():
    result = parse_response(MOCK_RESPONSE, puzzle_id=42, date="2024-01-15")
    assert result["id"] == 42
    assert result["date"] == "2024-01-15"


def test_parse_response_schema_version_present():
    result = parse_response(MOCK_RESPONSE, puzzle_id=1, date="2023-06-12")
    assert result["schema_version"] == 1


def test_parse_response_raises_on_wrong_category_count():
    bad_response = {"categories": MOCK_RESPONSE["categories"][:2]}
    with pytest.raises(ValueError, match="Expected 4 categories, got 2"):
        parse_response(bad_response, puzzle_id=1, date="2023-06-12")


def test_parse_response_raises_on_missing_categories_key():
    with pytest.raises(ValueError, match="Expected 4 categories, got 0"):
        parse_response({}, puzzle_id=1, date="2023-06-12")


def test_parse_response_has_images_false_for_text_puzzle():
    result = parse_response(MOCK_RESPONSE, puzzle_id=1, date="2023-06-12")
    assert result["has_images"] is False


def test_parse_response_has_images_true_for_image_puzzle():
    result = parse_response(MOCK_IMAGE_RESPONSE, puzzle_id=1, date="2023-06-12")
    assert result["has_images"] is True


def test_parse_response_image_puzzle_has_empty_words_and_groups():
    result = parse_response(MOCK_IMAGE_RESPONSE, puzzle_id=1, date="2023-06-12")
    assert result["words"] == []
    assert result["groups"] == []


def test_load_existing_dataset_returns_empty_list_when_file_missing():
    result = load_existing_dataset(Path("/nonexistent/path/connections.json"))
    assert result == []


def test_fetch_puzzle_returns_none_on_404():
    mock_response = MagicMock()
    mock_response.status_code = 404
    with patch("scripts.fetch_puzzles.requests.get", return_value=mock_response):
        result = fetch_puzzle("2024-01-15")
    assert result is None


def test_fetch_puzzle_raises_on_non_json_content_type():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "text/html"}
    with patch("scripts.fetch_puzzles.requests.get", return_value=mock_response):
        with pytest.raises(ValueError, match="Unexpected content type"):
            fetch_puzzle("2024-01-15")
