from __future__ import annotations

import ast
from pathlib import Path

from lesson_content import (
    HTTP_STATUS_GROUPS,
    LESSON_BLUEPRINTS,
    LESSON_EXTENSIONS,
    build_lesson_lab,
    validate_labs,
)


ROOT = Path(__file__).parents[1]


def load_tracks() -> list[dict]:
    tree = ast.parse((ROOT / "academy_app.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "TRACKS":
            return ast.literal_eval(node.value)
    raise AssertionError("TRACKS literal not found")


def test_all_thirty_lessons_have_complete_connected_labs() -> None:
    tracks = load_tracks()
    lessons = [lesson for track in tracks for lesson in track["lessons"]]

    assert len(lessons) == 30
    assert validate_labs(tracks) == []
    assert {lesson["id"] for lesson in lessons} == set(LESSON_BLUEPRINTS)


def test_each_quiz_and_practice_task_links_back_to_theory() -> None:
    for track in load_tracks():
        for lesson in track["lessons"]:
            lab = build_lesson_lab(lesson)
            section_ids = {section["id"] for section in lab["sections"]}

            assert len(lab["sections"]) >= 10
            assert len(lab["quiz"]) >= 4
            assert all(question["source"] in section_ids for question in lab["quiz"])
            assert lab["debug"]["source"] in section_ids
            assert len(lab["build"]["steps"]) == 5
            assert len(lab["build"]["rubric"]) >= 5


def test_every_lesson_meets_professional_depth_contract() -> None:
    lessons = [lesson for track in load_tracks() for lesson in track["lessons"]]

    assert set(LESSON_EXTENSIONS) == set(LESSON_BLUEPRINTS)
    for lesson in lessons:
        lab = build_lesson_lab(lesson)
        total_words = sum(len(section["body"].split()) for section in lab["sections"])

        assert total_words >= 2_200, lesson["id"]
        assert all(section["minutes"] >= 8 for section in lab["sections"])
        assert all(len(section["summary"].split()) >= 5 for section in lab["sections"])
        assert all(len(section["practice"].split()) >= 8 for section in lab["sections"])
        assert all(len(section["takeaways"]) >= 3 for section in lab["sections"])
        for section in lab["sections"]:
            check = section["check"]
            assert len(check["options"]) == 4
            assert 0 <= check["answer"] < len(check["options"])
            assert len(check["why"].split()) >= 5


def test_http_reference_covers_success_client_and_server_cases() -> None:
    statuses = {code for _, _, group in HTTP_STATUS_GROUPS for code, _, _ in group}

    assert {200, 201, 202, 204}.issubset(statuses)
    assert {301, 302, 304, 307, 308}.issubset(statuses)
    assert {400, 401, 403, 404, 405, 409, 415, 422, 429}.issubset(statuses)
    assert {500, 502, 503, 504}.issubset(statuses)


def test_http_quiz_includes_rate_limit_scenario() -> None:
    lesson = next(
        lesson
        for track in load_tracks()
        for lesson in track["lessons"]
        if lesson["id"] == "git_api"
    )
    lab = build_lesson_lab(lesson)

    assert any("429" in question["q"] for question in lab["quiz"])
    assert any("Statuscodes" in section["title"] for section in lab["sections"])
    assert len(lab["sections"]) >= 14
    assert sum(len(section["body"].split()) for section in lab["sections"]) >= 3_500
    assert "ReadTimeout" in lab["debug"]["symptom"]
