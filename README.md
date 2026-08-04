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
- Theorie, Beispiele, Quiz und Coding-Challenges
- Lokale Speicherung in `progress.json`
- Portfolio-Roadmap mit vier End-to-End-Projekten
- Interview- und Job-Readiness-Check

## Sicherheit

Der optionale Code-Runner führt Python lokal in einem separaten Prozess mit Timeout aus. Er ist für eigene Lerncodes gedacht, nicht für fremden oder nicht vertrauenswürdigen Code.
