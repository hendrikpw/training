"""Stable Streamlit entrypoint for the AI Engineering Academy."""

from __future__ import annotations

from pathlib import Path
import sys
import traceback

import streamlit as st

source_path = Path(__file__).with_name("academy_app.py")
app_dir = str(source_path.parent.resolve())
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

namespace = {"__name__": "__main__", "__file__": str(source_path), "__package__": None}
try:
    exec(compile(source_path.read_text(encoding="utf-8"), str(source_path), "exec"), namespace)
except Exception as exc:  # Keep deployment failures observable in the public UI.
    error_id = f"{type(exc).__name__}:{abs(hash(str(exc))) % 1_000_000:06d}"
    st.error("Die Academy konnte diesen Lauf nicht abschließen.")
    st.markdown(f"**Fehler-ID:** `{error_id}`")
    st.code(f"{type(exc).__name__}: {exc}", language="text")
    with st.expander("Technische Details für die Fehlersuche"):
        st.code(traceback.format_exc(), language="text")
    st.info("Bitte kopiere die Fehler-ID oder sende einen Screenshot dieser Meldung. Der genaue Fehler ist jetzt sichtbar.")
