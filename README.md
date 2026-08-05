# AI Engineering Academy

Gamifizierte Streamlit-Lernapp für angehende AI Engineers.

## Start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Enthalten

- Skill Tree mit 10 Tracks und 30 Lektionen
- XP, Level, Streak, Badges und Fortschrittsanzeige
- pro Lektion mindestens sechs ausführliche, aufeinander aufbauende Theoriekapitel
- Lernziele, präzise Begriffe, Praxisfälle, Abläufe und typische Failure Modes
- vier direkt auf die Theorie verlinkte Verständnis- und Szenariofragen je Lektion
- Debug Labs mit kaputtem Code beziehungsweise fehlerhaften Artefakten, Symptom, Diagnose und Musterlösung
- fünfstufige Build Missions mit messbarer Abnahme-Rubrik
- vollständige HTTP-Statuscode-Arbeitsreferenz mit typischen Fällen und Clientreaktionen
- Lokale Speicherung in `progress.json`
- Portfolio-Roadmap mit vier End-to-End-Projekten
- Interview- und Job-Readiness-Check

## Sicherheit

Der optionale Code-Runner führt Python lokal in einem separaten Prozess mit Timeout aus. Er ist für eigene Lerncodes gedacht, nicht für fremden oder nicht vertrauenswürdigen Code.

## Curriculum-Architektur

- `academy_app.py` enthält Tracks, Navigation, Fortschritt und die interaktive Lesson-Lab-Oberfläche.
- `lesson_content.py` enthält die testbare Wissensbasis und erzeugt für alle 30 Lektionen denselben verbindlichen Lernvertrag.
- `app.py` ist der stabile Streamlit-Einstiegspunkt.
- `tests/test_curriculum.py` prüft Vollständigkeit, Querverweise, Antwortindizes, Praxisumfang und die HTTP-Referenz.

Die drei Lernphasen sind absichtlich miteinander verbunden: Jede Quizfrage verweist auf ein konkretes Learn-Kapitel; Debug Lab und Build Mission greifen dessen Begriffe, Abläufe und Failure Modes erneut auf. Eine Lektion ist damit kein Nebeneinander unabhängiger Tabs mehr, sondern eine Lernkette von Theorie über Abruf und Diagnose bis zum Transfer.

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

Der Sidebar-Buildstempel zeigt, ob das aktuelle Deployment geladen wurde. Unerwartete Laufzeitfehler werden im Einstiegspunkt abgefangen und mit Fehler-ID sowie Traceback in der App sichtbar gemacht; dadurch bleibt die eigentliche Ursache auch ohne Zugriff auf die Cloud-Konsole diagnostizierbar.

## Community-Cloud-Deployment

Die Produktionsabhängigkeiten sind bewusst kompatibel gepinnt. Insbesondere bleibt
`starlette==0.49.3` fixiert, solange Streamlit 1.60 dessen 0.x-GZip-Schnittstelle
verwendet. Starlette 1.x würde den ASGI-Server bereits vor Ausführung von `app.py`
beenden; ein App-interner Fehlerbildschirm kann diesen Startfehler daher nicht
abfangen.

Für ein reproduzierbares Deployment wird Python 3.12 empfohlen. Community Cloud
installiert Änderungen an `requirements.txt` automatisch neu. Falls nach einer
Abhängigkeitsänderung noch ein alter Build läuft, unter **Manage app** einmal
**Reboot app** ausführen.
