from __future__ import annotations

import runpy

import streamlit as st

_original_radio = st.radio


def _navigation_safe_radio(label, options, *args, **kwargs):
    """Keep the navigation widget separate from the mutable page state."""
    if kwargs.get("key") == "page":
        pages = list(options)
        kwargs["key"] = "navigation_page"

        desired_page = st.session_state.get("page", pages[0] if pages else None)
        if desired_page in pages:
            # Synchronize the widget value before the widget is instantiated.
            # This lets buttons such as "Mission starten" and "Öffnen" change pages.
            if st.session_state.get("navigation_page") != desired_page:
                st.session_state["navigation_page"] = desired_page
            kwargs.pop("index", None)

        selected = _original_radio(label, options, *args, **kwargs)
        st.session_state.page = selected
        return selected

    return _original_radio(label, options, *args, **kwargs)


st.radio = _navigation_safe_radio
runpy.run_path("academy_app.py", run_name="__main__")
