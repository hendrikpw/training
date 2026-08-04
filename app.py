from __future__ import annotations

from pathlib import Path

import streamlit as st

_original_radio = st.radio


def _navigation_safe_radio(label, options, *args, **kwargs):
    """Keep the navigation widget separate from the mutable page state."""
    if kwargs.get("key") == "page":
        pages = list(options)
        kwargs["key"] = "navigation_page"

        desired_page = st.session_state.get("page", pages[0] if pages else None)
        if desired_page in pages:
            if st.session_state.get("navigation_page") != desired_page:
                st.session_state["navigation_page"] = desired_page
            kwargs.pop("index", None)

        selected = _original_radio(label, options, *args, **kwargs)
        st.session_state.page = selected
        return selected

    return _original_radio(label, options, *args, **kwargs)


st.radio = _navigation_safe_radio

# The curriculum currently lives in academy_app.py. We apply the richer lesson
# format here so the deployed starter remains app.py while the original course
# data stays intact and can be migrated incrementally.
source_path = Path(__file__).with_name("academy_app.py")
source = source_path.read_text(encoding="utf-8")

lesson_start = source.index('            {"id":"python"')
lesson_end = source.index('            {"id":"git_api"', lesson_start)

expanded_python_lesson = '''            {"id":"python","title":"Python für AI Engineers","xp":180,"difficulty":"Beginner","minutes":90,
             "theory":"Python-Grundlagen für AI Engineering: Werte, Variablen, Datentypen, Listen, Funktionen, Bedingungen, Fehlerbehandlung und Type Hints.",
             "theory_sections":[
                {"title":"1. Was macht Python in einem AI-System?","content":"Python verbindet Daten, Modelle, APIs und Benutzeroberflächen. Ein AI Engineer trainiert nicht nur Modelle, sondern schreibt vor allem Software, die Eingaben prüft, Daten verarbeitet, Modelle aufruft und Ergebnisse zuverlässig weitergibt.","example":"```python\\nuser_text = 'Erkläre mir RAG'\\nmodel_name = 'example-model'\\nmax_tokens = 300\\n```","practice":"Lege drei Variablen für eine Modellanfrage an: einen Text, einen Modellnamen und eine maximale Tokenzahl."},
                {"title":"2. Werte und Datentypen","content":"Jeder Wert hat einen Datentyp. Texte sind `str`, ganze Zahlen `int`, Dezimalzahlen `float`, Wahrheitswerte `bool` und mehrere Werte werden häufig in einer `list` gespeichert. Der Datentyp bestimmt, welche Operationen sinnvoll sind.","example":"```python\\nprompt = 'Hallo'          # str\\nretries = 3               # int\\ntemperature = 0.2         # float\\nuse_cache = True          # bool\\nscores = [0.7, 0.9, 0.4] # list[float]\\n```","practice":"Erstelle eine Liste mit drei Modell-Scores und berechne deren Summe mit `sum(...)`."},
                {"title":"3. Funktionen: wiederverwendbare Arbeitsschritte","content":"Eine Funktion bündelt einen klaren Arbeitsschritt. Sie erhält Eingaben als Parameter und gibt mit `return` ein Ergebnis zurück. Gute Funktionen erledigen genau eine verständliche Aufgabe.","example":"```python\\ndef build_prompt(topic: str) -> str:\\n    return f'Erkläre {topic} in einfachen Worten.'\\n\\nprompt = build_prompt('Embeddings')\\n```","practice":"Schreibe eine Funktion `double(value)`, die eine Zahl verdoppelt und zurückgibt."},
                {"title":"4. Bedingungen und Sonderfälle","content":"Produktionscode muss auch mit Sonderfällen umgehen. Mit `if` prüfst du Bedingungen. Beispielsweise darf eine Durchschnittsfunktion keine leere Liste kommentarlos verarbeiten, weil eine Division durch null nicht definiert ist.","example":"```python\\ndef mean(values: list[float]) -> float:\\n    if not values:\\n        raise ValueError('values must not be empty')\\n    return sum(values) / len(values)\\n```","practice":"Erweitere eine Funktion so, dass sie bei einer leeren Liste `0.0` zurückgibt."},
                {"title":"5. Was bedeutet Normalisierung auf 0 bis 1?","content":"Normalisierung bringt Zahlen auf eine gemeinsame Skala. Bei Min-Max-Normalisierung wird der kleinste Wert zu 0 und der größte zu 1. Alle Werte dazwischen werden proportional eingeordnet. Die Formel lautet `(Wert - Minimum) / (Maximum - Minimum)`. Beispiel: Bei `[10, 20, 30]` gilt für 20: `(20 - 10) / (30 - 10) = 10 / 20 = 0.5`.","example":"```python\\nvalues = [10, 20, 30]\\nminimum = min(values)      # 10\\nmaximum = max(values)      # 30\\nnormalized_20 = (20 - minimum) / (maximum - minimum)\\n# Ergebnis: 0.5\\n```","practice":"Berechne auf Papier oder im Code den normalisierten Wert von 15 in der Liste `[10, 15, 20]`."},
                {"title":"6. Warum Type Hints?","content":"Type Hints beschreiben erwartete Ein- und Ausgaben. Python erzwingt sie nicht automatisch, aber Editoren, Tests und Teammitglieder erkennen dadurch Schnittstellenfehler früher. In AI-Systemen ist das wichtig, weil viele Komponenten miteinander verbunden sind.","example":"```python\\ndef normalize_scores(scores: list[float]) -> list[float]:\\n    ...\\n```","practice":"Lies die Signatur: Die Funktion erhält eine Liste aus Dezimalzahlen und gibt wieder eine Liste aus Dezimalzahlen zurück."}
             ],
             "example":"```python\\nfrom typing import Iterable\\n\\ndef mean(values: Iterable[float]) -> float:\\n    items = list(values)\\n    if not items:\\n        raise ValueError('values must not be empty')\\n    return sum(items) / len(items)\\n```",
             "quiz":{"q":"Warum sind Type Hints in AI-Systemen besonders nützlich?","options":["Sie machen Python automatisch schneller","Sie beschreiben Schnittstellen und helfen, Integrationsfehler früher zu erkennen","Sie ersetzen sämtliche Tests","Sie verschlüsseln Modellanfragen"],"answer":1,"why":"AI-Systeme verbinden viele Komponenten. Explizite Ein- und Ausgabetypen machen diese Schnittstellen verständlicher und kontrollierbarer."},
             "challenges":[
                {"title":"Aufgabe 1: Eine einfache Funktion","level":"Geführt","prompt":"Implementiere `double(value)`. Die Funktion soll die übergebene Zahl mit 2 multiplizieren und zurückgeben.","hint":"Eine Funktion gibt ihr Ergebnis mit `return` zurück. Der Rechenausdruck lautet `value * 2`.","starter":"def double(value: float) -> float:\\n    # Ersetze pass durch deine Lösung\\n    pass","tests":"assert double(4) == 8\\nassert double(1.5) == 3.0\\nassert double(-2) == -4"},
                {"title":"Aufgabe 2: Durchschnitt mit Sonderfall","level":"Basis","prompt":"Implementiere `safe_mean(values)`. Bei einer leeren Liste soll `0.0` zurückgegeben werden, sonst der Durchschnitt.","hint":"Prüfe zuerst `if not values:`. Der Durchschnitt ist `sum(values) / len(values)`.","starter":"def safe_mean(values: list[float]) -> float:\\n    # 1. Leere Liste behandeln\\n    # 2. Durchschnitt berechnen\\n    pass","tests":"assert safe_mean([]) == 0.0\\nassert safe_mean([2, 4, 6]) == 4.0\\nassert safe_mean([1.5, 2.5]) == 2.0"},
                {"title":"Aufgabe 3: Einen Wert normalisieren","level":"Aufbau","prompt":"Implementiere `normalize_value(value, minimum, maximum)`. Nutze die im Theorieteil erklärte Min-Max-Formel. Sind Minimum und Maximum identisch, gib `0.0` zurück.","hint":"Formel: `(value - minimum) / (maximum - minimum)`.","starter":"def normalize_value(value: float, minimum: float, maximum: float) -> float:\\n    # Sonderfall: kein Wertebereich vorhanden\\n    pass","tests":"assert normalize_value(20, 10, 30) == 0.5\\nassert normalize_value(10, 10, 30) == 0.0\\nassert normalize_value(30, 10, 30) == 1.0\\nassert normalize_value(4, 4, 4) == 0.0"},
                {"title":"Aufgabe 4: Eine ganze Liste normalisieren","level":"Transfer","prompt":"Implementiere `normalize_scores(scores)`. Leere Listen bleiben leer. Bei identischen Werten werden alle Ergebnisse `0.0`. Ansonsten normalisierst du jeden Wert mit der Min-Max-Formel.","hint":"Bestimme zuerst `minimum = min(scores)` und `maximum = max(scores)`. Erzeuge anschließend mit einer Schleife oder List Comprehension die Ergebnisliste.","starter":"def normalize_scores(scores: list[float]) -> list[float]:\\n    # 1. Leere Liste behandeln\\n    # 2. Minimum und Maximum bestimmen\\n    # 3. Identische Werte behandeln\\n    # 4. Jeden Wert normalisieren\\n    pass","tests":"assert normalize_scores([10, 20, 30]) == [0.0, 0.5, 1.0]\\nassert normalize_scores([4, 4]) == [0.0, 0.0]\\nassert normalize_scores([]) == []\\nassert normalize_scores([-10, 0, 10]) == [0.0, 0.5, 1.0]"}
             ],
             "challenge":{"prompt":"Implementiere `normalize_scores(scores)`.","starter":"def normalize_scores(scores: list[float]) -> list[float]:\\n    pass","tests":"assert normalize_scores([10, 20, 30]) == [0.0, 0.5, 1.0]"}},
'''
source = source[:lesson_start] + expanded_python_lesson + source[lesson_end:]

ui_start = source.index("    with tab1:")
ui_end = source.index("    with tab4:", ui_start)
expanded_lesson_ui = '''    with tab1:
        st.subheader("Lernpfad")
        if "theory_sections" in lesson:
            st.write("Arbeite die Abschnitte der Reihe nach durch. Jede neue Idee wird zuerst erklärt und anschließend direkt angewendet.")
            for section_number, section in enumerate(lesson["theory_sections"], start=1):
                with st.container(border=True):
                    st.markdown(f"### {section['title']}")
                    st.write(section["content"])
                    if section.get("example"):
                        st.markdown("**Beispiel**")
                        st.markdown(section["example"])
                    if section.get("practice"):
                        st.info("Mini-Übung: " + section["practice"])
        else:
            st.subheader("Kernkonzept")
            st.write(lesson["theory"])
            st.subheader("Beispiel")
            st.markdown(lesson["example"])
        st.info("Engineer-Mindset: Verstehe zuerst Eingaben, gewünschte Ausgabe und Sonderfälle. Schreibe erst danach Code.")
    with tab2:
        q = lesson["quiz"]
        answer = st.radio(q["q"], q["options"], key=f"quiz-{key}")
        if st.button("Antwort prüfen", key=f"check-{key}"):
            idx = q["options"].index(answer)
            if idx == q["answer"]:
                st.success("Richtig. " + q["why"])
                if key not in st.session_state.progress["quiz_correct"]:
                    st.session_state.progress["quiz_correct"].append(key)
                    st.session_state.progress["xp"] += 25
                    save_progress()
            else:
                st.error("Noch nicht. " + q["why"])
    with tab3:
        challenges = lesson.get("challenges")
        if challenges:
            st.write("Die Aufgaben bauen aufeinander auf. Beginne oben und gehe erst weiter, wenn die Tests bestanden sind.")
            for challenge_index, challenge in enumerate(challenges, start=1):
                challenge_key = f"{key}-{challenge_index}"
                with st.expander(f"{challenge['title']} · {challenge.get('level', 'Praxis')}", expanded=challenge_index == 1):
                    st.write(challenge["prompt"])
                    if challenge.get("hint"):
                        with st.expander("Hinweis anzeigen"):
                            st.write(challenge["hint"])
                    code = st.text_area(
                        "Deine Lösung",
                        challenge["starter"],
                        height=240,
                        key=f"code-{challenge_key}",
                    )
                    if st.button("Tests ausführen", key=f"run-{challenge_key}", type="primary"):
                        ok, output = run_python(code, challenge["tests"])
                        if ok:
                            st.success(output)
                            completion_key = f"{key}::challenge-{challenge_index}"
                            if completion_key not in st.session_state.progress["challenge_correct"]:
                                st.session_state.progress["challenge_correct"].append(completion_key)
                                st.session_state.progress["xp"] += 25
                                save_progress()
                        else:
                            st.error(output)
        elif "challenge" in lesson:
            challenge = lesson["challenge"]
            st.write(challenge["prompt"])
            code = st.text_area("Deine Lösung", challenge["starter"], height=220, key=f"code-{key}")
            st.caption("Der Runner ist für eigene Lerncodes gedacht. Führe keinen fremden Code aus.")
            if st.button("Tests ausführen", key=f"run-{key}", type="primary"):
                ok, output = run_python(code, challenge["tests"])
                if ok:
                    st.success(output)
                    if key not in st.session_state.progress["challenge_correct"]:
                        st.session_state.progress["challenge_correct"].append(key)
                        st.session_state.progress["xp"] += 50
                        save_progress()
                else:
                    st.error(output)
        else:
            st.markdown("### Mini Build Mission")
            st.write("Erstelle ein kleines Artefakt zu dieser Lektion: Diagramm, API-Skizze, Eval-Tabelle, Threat Model oder Architekturentscheidung.")
            st.text_area("Beschreibe dein Artefakt und die wichtigsten Trade-offs", height=180, key=f"mission-{key}")
'''
source = source[:ui_start] + expanded_lesson_ui + source[ui_end:]

namespace = {
    "__name__": "__main__",
    "__file__": str(source_path),
    "__package__": None,
}
exec(compile(source, str(source_path), "exec"), namespace)
