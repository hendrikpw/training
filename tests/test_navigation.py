from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).parents[1] / "app.py"


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
