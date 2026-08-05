from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).parents[1] / "app.py"


def fresh_progress() -> dict:
    return {
        "completed": [], "quiz_correct": [], "challenge_correct": [], "xp": 0,
        "streak": 0, "last_active": None, "notes": {}, "projects": {},
        "lesson_started": [], "chapter_completed": [],
    }


def test_dashboard_mission_button_opens_lesson_without_session_state_error() -> None:
    app = AppTest.from_file(APP_PATH, default_timeout=20).run()

    next(button for button in app.button if button.label == "Mission starten").click().run()

    assert not app.exception
    assert app.session_state["navigation_page"] == "Lesson Lab"
    assert len(app.selectbox) == 1
    assert app.selectbox[0].label == "Lektion"


def test_skill_tree_open_button_uses_safe_queued_navigation() -> None:
    app = AppTest.from_file(APP_PATH, default_timeout=20)
    app.session_state["navigation_page"] = "Skill Tree"
    app.run()

    next(button for button in app.button if button.label == "Öffnen").click().run()

    assert not app.exception
    assert app.session_state["navigation_page"] == "Lesson Lab"
    assert len(app.selectbox) == 1


def test_lesson_overview_starts_a_sequential_chapter_player() -> None:
    app = AppTest.from_file(APP_PATH, default_timeout=30)
    app.session_state["navigation_page"] = "Lesson Lab"
    app.session_state["progress"] = fresh_progress()
    app.run()

    assert next(metric for metric in app.metric if metric.label == "Ausführliche Kapitel").value == "10"
    assert any(button.label in {"Lektion starten", "Lektion fortsetzen"} for button in app.button)
    assert not any(selectbox.label == "Kapitel auswählen" for selectbox in app.selectbox)

    next(button for button in app.button if button.label in {"Lektion starten", "Lektion fortsetzen"}).click().run()

    assert not app.exception
    assert any(selectbox.label == "Kapitel auswählen" for selectbox in app.selectbox)
    assert any(area.label == "Deine Ausarbeitung" for area in app.text_area)
    assert any(button.label == "Kapitelantwort prüfen" for button in app.button)
    assert next(button for button in app.button if button.label == "Nächstes Kapitel →").disabled


def test_correct_chapter_check_unlocks_the_next_chapter_without_widget_error() -> None:
    app = AppTest.from_file(APP_PATH, default_timeout=30)
    app.session_state["navigation_page"] = "Lesson Lab"
    app.session_state["progress"] = fresh_progress()
    app.run()
    start = next(button for button in app.button if button.label in {"Lektion starten", "Lektion fortsetzen"})
    start.click().run()

    check = next(radio for radio in app.radio if radio.label == "Wann ist das Thema beruflich beherrscht?")
    check.set_value(check.options[0])
    next(button for button in app.button if button.label == "Kapitelantwort prüfen").click().run()

    assert not app.exception
    next_button = next(button for button in app.button if button.label == "Nächstes Kapitel →")
    assert not next_button.disabled
    next_button.click().run()

    assert not app.exception
    chapter = next(selectbox for selectbox in app.selectbox if selectbox.label == "Kapitel auswählen")
    assert chapter.value == 1
