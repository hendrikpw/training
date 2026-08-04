from __future__ import annotations

import runpy

import streamlit as st

_original_radio = st.radio


def _navigation_safe_radio(label, options, *args, **kwargs):
    """Keep the navigation widget separate from the mutable page state."""
    if kwargs.get("key") == "page":
        pages = list(options)
        kwargs["key"] = "navigation_page"
        current = st.session_state.get("page", pages[0] if pages else None)
        if current in pages and "index" not in kwargs:
            kwargs["index"] = pages.index(current)
        selected = _original_radio(label, options, *args, **kwargs)
        st.session_state.page = selected
        return selected
    return _original_radio(label, options, *args, **kwargs)


st.radio = _navigation_safe_radio
runpy.run_path("academy_app.py", run_name="__main__")
