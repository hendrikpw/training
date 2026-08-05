"""Stable Streamlit entrypoint for the AI Engineering Academy."""

from __future__ import annotations

from pathlib import Path

source_path = Path(__file__).with_name("academy_app.py")
namespace = {"__name__": "__main__", "__file__": str(source_path), "__package__": None}
exec(compile(source_path.read_text(encoding="utf-8"), str(source_path), "exec"), namespace)
