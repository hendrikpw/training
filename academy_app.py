from __future__ import annotations

import ast
import json
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from lesson_content import build_lesson_lab, validate_labs

APP_DIR = Path(__file__).parent
PROGRESS_FILE = APP_DIR / "progress.json"

st.set_page_config(page_title="AI Engineering Academy", page_icon="🧠", layout="wide")

TRACKS: list[dict[str, Any]] = [
    {
        "id": "foundations", "title": "1. Engineering Foundations", "icon": "🧱", "color": "#64748B",
        "description": "Python, Git, APIs, Datenstrukturen und saubere Softwareentwicklung.",
        "lessons": [
            {"id":"python","title":"Python für AI Engineers","xp":120,"difficulty":"Beginner","minutes":45,
             "theory":"AI Engineering ist Software Engineering mit probabilistischen Komponenten. Beherrsche Funktionen, Typen, Fehlerbehandlung, Module, virtuelle Umgebungen und Tests.",
             "example":"```python\nfrom typing import Iterable\n\ndef mean(values: Iterable[float]) -> float:\n    items = list(values)\n    if not items:\n        raise ValueError('values must not be empty')\n    return sum(items) / len(items)\n```",
             "quiz":{"q":"Warum sind Type Hints in AI-Systemen besonders nützlich?","options":["Sie machen Python schneller","Sie reduzieren Integrationsfehler und verbessern Tooling","Sie ersetzen Tests","Sie verschlüsseln Prompts"],"answer":1,"why":"AI-Systeme verbinden viele Komponenten. Explizite Datentypen machen Schnittstellen kontrollierbarer."},
             "challenge":{"prompt":"Implementiere `normalize_scores(scores)`, sodass Werte linear auf 0 bis 1 skaliert werden. Bei identischen Werten sollen alle Ergebnisse 0.0 sein.","starter":"def normalize_scores(scores: list[float]) -> list[float]:\n    # dein Code\n    pass","tests":"assert normalize_scores([10, 20, 30]) == [0.0, 0.5, 1.0]\nassert normalize_scores([4, 4]) == [0.0, 0.0]\nassert normalize_scores([]) == []"}},
            {"id":"git_api","title":"Git, HTTP und APIs","xp":100,"difficulty":"Beginner","minutes":35,
             "theory":"Produktive AI-Anwendungen sind API-Systeme. Verstehe HTTP-Methoden, Statuscodes, JSON, Authentifizierung, Rate Limits, Retries und Git-Workflows.",
             "example":"```python\nimport requests\n\nr = requests.get(url, timeout=10)\nr.raise_for_status()\ndata = r.json()\n```",
             "quiz":{"q":"Welcher Statuscode signalisiert typischerweise Rate Limiting?","options":["200","401","404","429"],"answer":3,"why":"HTTP 429 bedeutet Too Many Requests."}},
            {"id":"testing","title":"Testing & Clean Architecture","xp":130,"difficulty":"Intermediate","minutes":50,
             "theory":"Trenne Domänenlogik, Provider-Adapter und UI. Teste deterministische Komponenten klassisch und probabilistische Komponenten mit Evals, Datensätzen und Schwellenwerten.",
             "example":"```text\nui -> application service -> model gateway\n                         -> retrieval service\n                         -> telemetry\n```",
             "quiz":{"q":"Was sollte ein Unit Test bevorzugt prüfen?","options":["Das komplette Produktionssystem","Eine kleine isolierte Verhaltenseinheit","Nur die UI-Farbe","Zufällige Modellantworten ohne Kriterien"],"answer":1,"why":"Unit Tests sollen klein, schnell und deterministisch sein."}},
        ]
    },
    {
        "id":"ml", "title":"2. Machine Learning Core", "icon":"📈", "color":"#0EA5E9",
        "description":"ML-Grundlagen, Training, Datenlecks, Metriken und Modellwahl.",
        "lessons":[
            {"id":"ml_basics","title":"Supervised ML & Generalisierung","xp":140,"difficulty":"Intermediate","minutes":55,
             "theory":"Lerne Features, Labels, Loss, Optimierung, Overfitting, Regularisierung und den Unterschied zwischen Training, Validation und Test.",
             "example":"```text\nTrain: Parameter lernen\nValidation: Hyperparameter wählen\nTest: einmalige, unverzerrte Endbewertung\n```",
             "quiz":{"q":"Warum darf der Testsatz nicht für Hyperparameter-Tuning verwendet werden?","options":["Er ist zu klein","Sonst wird die Endbewertung optimistisch verzerrt","Modelle können keine Testsätze lesen","Es ist technisch unmöglich"],"answer":1,"why":"Wiederholtes Entscheiden anhand des Testsatzes führt zu indirektem Overfitting."}},
            {"id":"metrics","title":"Metriken & Fehleranalyse","xp":140,"difficulty":"Intermediate","minutes":50,
             "theory":"Accuracy reicht selten. Nutze Precision, Recall, F1, ROC-AUC, PR-AUC, MAE/RMSE und segmentierte Fehleranalysen passend zu den Geschäftskosten.",
             "example":"```text\nPrecision = TP / (TP + FP)\nRecall    = TP / (TP + FN)\n```",
             "quiz":{"q":"Bei einer Krankheitserkennung sind übersehene Fälle besonders teuer. Welche Metrik ist zentral?","options":["Recall","Speicherverbrauch","R²","Latenz allein"],"answer":0,"why":"Hoher Recall reduziert False Negatives."}},
            {"id":"data_quality","title":"Data Quality & Leakage","xp":150,"difficulty":"Intermediate","minutes":55,
             "theory":"Datenqualität entscheidet häufig stärker als Modellwahl. Prüfe Schema, Missing Values, Duplikate, Label-Fehler, Drift, Sampling Bias und Leakage.",
             "example":"```text\nLeakage-Beispiel: Kündigungsdatum als Feature zur Vorhersage einer Kündigung verwenden.\n```",
             "quiz":{"q":"Was ist Target Leakage?","options":["Zu wenige Features","Information aus der Zukunft oder dem Ziel gelangt in die Features","Ein langsames Modell","Fehlende GPU"],"answer":1,"why":"Das Modell erhält Information, die zum Vorhersagezeitpunkt nicht verfügbar wäre."}},
        ]
    },
    {
        "id":"deep", "title":"3. Deep Learning & Transformers", "icon":"🧬", "color":"#14B8A6",
        "description":"Neuronale Netze, Embeddings, Attention und Transformer-Architektur.",
        "lessons":[
            {"id":"nn","title":"Neuronale Netze","xp":150,"difficulty":"Intermediate","minutes":60,"theory":"Verstehe Forward Pass, Aktivierungsfunktionen, Loss, Backpropagation, Gradient Descent, Batch-Größe, Lernrate und Regularisierung.","example":"```text\nz = Wx + b\na = activation(z)\n```","quiz":{"q":"Was bewirkt Backpropagation?","options":["Sie generiert Trainingsdaten","Sie berechnet Gradienten für Parameterupdates","Sie komprimiert das Modell","Sie tokenisiert Text"],"answer":1,"why":"Backpropagation nutzt die Kettenregel, um Loss-Gradienten zu berechnen."}},
            {"id":"embeddings","title":"Embeddings & semantische Suche","xp":160,"difficulty":"Intermediate","minutes":55,"theory":"Embeddings bilden Inhalte als Vektoren ab. Ähnliche Bedeutungen liegen näher beieinander. Anwendungen: Suche, Clustering, Empfehlungen, RAG und Anomalieerkennung.","example":"```python\nsimilarity = dot(a, b) / (norm(a) * norm(b))\n```","quiz":{"q":"Was misst Cosine Similarity primär?","options":["Vektorrichtung","Dateigröße","Tokenpreis","Trainingsdauer"],"answer":0,"why":"Sie misst den Winkel beziehungsweise die Richtungsähnlichkeit zweier Vektoren."}},
            {"id":"transformers","title":"Attention & Transformer","xp":180,"difficulty":"Advanced","minutes":70,"theory":"Self-Attention gewichtet Beziehungen zwischen Tokens. Transformer kombinieren Attention, Feed-Forward-Netze, Residual Connections und Normalisierung.","example":"```text\nAttention(Q,K,V) = softmax(QKᵀ / √d_k)V\n```","quiz":{"q":"Wozu dient die Skalierung durch √d_k?","options":["Token zu löschen","Extrem große Dot Products und instabile Softmax zu vermeiden","Das Modell zu quantisieren","Prompts zu cachen"],"answer":1,"why":"Mit steigender Dimension wachsen Dot Products; Skalierung stabilisiert die Softmax."}},
        ]
    },
    {
        "id":"llm", "title":"4. LLM Application Engineering", "icon":"💬", "color":"#8B5CF6",
        "description":"Prompting, strukturierte Outputs, Tool Calling, Kontext und Kosten.",
        "lessons":[
            {"id":"prompting","title":"Prompt & Context Engineering","xp":150,"difficulty":"Intermediate","minutes":50,"theory":"Definiere Ziel, Kontext, Constraints, Ausgabeformat und Beispiele. Behandle Prompts als versionierte Produktartefakte und teste sie gegen einen Eval-Datensatz.","example":"```text\nROLE + TASK + CONTEXT + CONSTRAINTS + OUTPUT SCHEMA + EXAMPLES\n```","quiz":{"q":"Was verbessert Prompt-Robustheit am stärksten?","options":["Mehr Adjektive","Klare Kriterien plus repräsentative Evals","Nur längere Prompts","Temperature immer auf 1"],"answer":1,"why":"Robustheit muss an realistischen Fällen gemessen und iterativ verbessert werden."}},
            {"id":"structured","title":"Structured Output & Tool Calling","xp":180,"difficulty":"Advanced","minutes":60,"theory":"Nutze validierte Schemas statt Freitext, wenn Antworten maschinell weiterverarbeitet werden. Tools sollten eng definiert, autorisiert und beobachtbar sein.","example":"```python\nclass Ticket(BaseModel):\n    category: Literal['billing','bug','other']\n    urgency: int\n```","quiz":{"q":"Warum ist JSON allein noch kein verlässlicher Structured Output?","options":["JSON ist nicht lesbar","Syntax kann stimmen, aber Felder und Werte können das Schema verletzen","JSON funktioniert nur im Browser","Es ist immer verschlüsselt"],"answer":1,"why":"Strukturvalidierung verlangt zusätzlich ein explizites Schema und Werteconstraints."}},
            {"id":"tokens","title":"Tokens, Context, Latency & Cost","xp":140,"difficulty":"Intermediate","minutes":45,"theory":"Optimiere Qualität, Latenz und Kosten gemeinsam. Messe Input-/Output-Tokens, Cache-Treffer, Time-to-first-token, Gesamtlatenz und Fehlerraten.","example":"```text\nKosten = input_tokens × input_rate + output_tokens × output_rate\n```","quiz":{"q":"Welche Maßnahme senkt häufig Kosten und Latenz?","options":["Jede Anfrage verdoppeln","Statische Promptteile cachen und Kontext kürzen","Alle Dokumente immer mitsenden","Mehr Agent-Schleifen"],"answer":1,"why":"Weniger wiederholter Kontext reduziert Verarbeitung und ermöglicht Caching."}},
        ]
    },
    {
        "id":"rag", "title":"5. Retrieval-Augmented Generation", "icon":"📚", "color":"#F59E0B",
        "description":"Ingestion, Chunking, Retrieval, Reranking, Zitierung und RAG-Evaluation.",
        "lessons":[
            {"id":"rag_pipeline","title":"RAG Pipeline","xp":170,"difficulty":"Advanced","minutes":60,"theory":"Eine RAG-Pipeline besteht aus Ingestion, Parsing, Chunking, Embeddings, Indexierung, Retrieval, optionalem Reranking und kontextgebundener Generierung.","example":"```text\nDocuments -> chunks -> embeddings -> vector index -> retrieve -> generate\n```","quiz":{"q":"Was ist der Hauptzweck von RAG?","options":["Ein Modell von Grund auf trainieren","Aktuelles oder privates Wissen zur Laufzeit bereitstellen","Token vollständig vermeiden","Nur Bilder generieren"],"answer":1,"why":"RAG ergänzt das Modell dynamisch um externe, kontrollierbare Wissensquellen."}},
            {"id":"chunking","title":"Chunking & Retrieval","xp":180,"difficulty":"Advanced","minutes":65,"theory":"Chunk-Größe und Überlappung sind domänenspezifisch. Kombiniere semantische Suche, Keyword-Suche, Metadatenfilter und Reranking. Evaluiere Recall@k und Precision@k.","example":"```text\nHybrid score = α · dense_score + (1-α) · BM25_score\n```","quiz":{"q":"Warum kann ein sehr großer Chunk schaden?","options":["Er enthält zu wenig Kontext","Er verwässert relevante Information und erhöht Tokenkosten","Vektordatenbanken verbieten ihn immer","Er erzeugt automatisch Leakage"],"answer":1,"why":"Große Chunks können mehrere Themen mischen und mehr irrelevanten Kontext liefern."}},
            {"id":"rag_eval","title":"RAG Evaluation & Citations","xp":190,"difficulty":"Advanced","minutes":70,"theory":"Trenne Retrieval- und Generationsevaluation. Prüfe Kontext-Relevanz, Faithfulness, Antwort-Relevanz, Zitatgenauigkeit, Latenz und Kosten.","example":"```text\nRetrieval: hit rate, recall@k, MRR\nGeneration: correctness, faithfulness, citation support\n```","quiz":{"q":"Was bedeutet Faithfulness?","options":["Die Antwort ist freundlich","Aussagen werden durch den bereitgestellten Kontext gestützt","Die Antwort ist besonders lang","Das Retrieval ist schnell"],"answer":1,"why":"Faithfulness misst, ob die generierte Antwort im verfügbaren Kontext verankert ist."}},
        ]
    },
    {
        "id":"agents", "title":"6. Agents & Workflows", "icon":"🤖", "color":"#EC4899",
        "description":"Toolnutzung, Zustandsmaschinen, Planung, Memory und Human-in-the-loop.",
        "lessons":[
            {"id":"workflow","title":"Deterministic Workflows first","xp":170,"difficulty":"Advanced","minutes":55,"theory":"Nutze feste Workflows, wenn der Prozess bekannt ist. Verwende agentische Entscheidungen nur dort, wo Flexibilität einen messbaren Mehrwert liefert.","example":"```text\nclassify -> retrieve -> draft -> validate -> human approval -> execute\n```","quiz":{"q":"Wann ist ein deterministischer Workflow meist besser?","options":["Wenn Schritte und Regeln bekannt sind","Wenn keinerlei Anforderungen existieren","Wenn maximale Unvorhersehbarkeit gewünscht ist","Nur bei Bildmodellen"],"answer":0,"why":"Bekannte Prozesse profitieren von kontrollierbaren, testbaren Übergängen."}},
            {"id":"tools","title":"Tool Use, State & Memory","xp":190,"difficulty":"Advanced","minutes":65,"theory":"Ein Agent benötigt klar definierte Tools, begrenzte Berechtigungen, Zustandsverwaltung, Abbruchbedingungen und beobachtbare Aktionen. Memory muss relevant, privat und löschbar sein.","example":"```text\nAgent state = messages + task status + tool results + budgets\n```","quiz":{"q":"Was ist eine wichtige Tool-Sicherheitsmaßnahme?","options":["Unbegrenzte Berechtigungen","Least Privilege und explizite Validierung","Keine Logs","Tools ohne Schema"],"answer":1,"why":"Minimale Rechte und validierte Argumente begrenzen mögliche Schäden."}},
            {"id":"hitl","title":"Human-in-the-loop","xp":160,"difficulty":"Advanced","minutes":50,"theory":"Risikoabhängige Freigaben sind zentral: irreversible, teure, rechtlich relevante oder externe Aktionen sollten durch Menschen bestätigt werden.","example":"```text\nread-only search: auto\nemail draft: review\nmoney transfer: explicit approval\n```","quiz":{"q":"Welche Aktion sollte zwingend eine explizite Freigabe haben?","options":["Interne Suche","Formatierung eines Entwurfs","Irreversible Zahlung","Lokale Sortierung"],"answer":2,"why":"Irreversible finanzielle Aktionen haben hohes Schadenspotenzial."}},
        ]
    },
    {
        "id":"eval", "title":"7. Evaluation & Reliability", "icon":"🧪", "color":"#22C55E",
        "description":"Eval-Datasets, LLM-as-Judge, Regression Tests und Fehleranalyse.",
        "lessons":[
            {"id":"eval_design","title":"Eval Design","xp":180,"difficulty":"Advanced","minutes":65,"theory":"Definiere klare Qualitätsdimensionen, repräsentative Testfälle, Gold Labels und Schwellenwerte. Segmentiere nach Schwierigkeit, Sprache, Risiko und Nutzergruppe.","example":"```text\nTask success | correctness | groundedness | safety | latency | cost\n```","quiz":{"q":"Was macht ein Eval-Dataset wertvoll?","options":["Nur leichte Fälle","Repräsentative reale und schwierige Fälle","Nur synthetische Zufallsdaten","Keine erwarteten Kriterien"],"answer":1,"why":"Evals müssen die tatsächliche Produktionsverteilung und relevante Fehlerfälle abbilden."}},
            {"id":"judge","title":"LLM-as-Judge","xp":170,"difficulty":"Advanced","minutes":60,"theory":"LLM-Judges skalieren qualitative Bewertung, können aber Bias und Instabilität haben. Kalibriere sie gegen menschliche Labels und nutze klare Rubrics.","example":"```text\nScore 1-5 with explicit anchors and evidence requirement\n```","quiz":{"q":"Wie validiert man einen LLM-Judge?","options":["Gar nicht","Übereinstimmung mit menschlichen Bewertungen prüfen","Nur das gleiche Modell bewerten lassen","Temperature maximieren"],"answer":1,"why":"Der Judge muss gegen verlässliche menschliche Referenzen kalibriert werden."}},
            {"id":"regression","title":"Regression Testing & Observability","xp":190,"difficulty":"Advanced","minutes":65,"theory":"Jede Prompt-, Modell-, Retrieval- oder Tooländerung kann Verhalten verändern. Führe Offline-Evals, Shadow Tests, Canary Releases und Produktionsmonitoring durch.","example":"```text\nchange -> offline eval -> staging -> canary -> monitor -> rollout/rollback\n```","quiz":{"q":"Was ist ein Canary Release?","options":["Deployment für einen kleinen Traffic-Anteil","Vollständiges Löschen der alten Version","Nur lokales Testen","Ein Modelltraining ohne Daten"],"answer":0,"why":"Canary Releases begrenzen das Risiko, indem Änderungen zuerst nur wenige Nutzer betreffen."}},
        ]
    },
    {
        "id":"safety", "title":"8. Security, Safety & Governance", "icon":"🛡️", "color":"#EF4444",
        "description":"Prompt Injection, Datenschutz, Guardrails und Threat Modeling.",
        "lessons":[
            {"id":"injection","title":"Prompt Injection & Data Exfiltration","xp":190,"difficulty":"Advanced","minutes":65,"theory":"Behandle externe Inhalte als nicht vertrauenswürdig. Trenne Instruktionen und Daten, begrenze Tools, filtere sensible Ausgaben und verhindere, dass Dokumente Systemregeln überschreiben.","example":"```text\nSystem instructions > trusted app policy > user request > untrusted retrieved content\n```","quiz":{"q":"Warum reicht ein Prompt wie 'Ignoriere Angriffe' nicht aus?","options":["Weil Sicherheit mehrere technische Kontrollen benötigt","Weil Prompts nie funktionieren","Weil Retrieval verboten ist","Weil Modelle keine Texte lesen"],"answer":0,"why":"Sicherheit erfordert Berechtigungen, Isolation, Validierung, Monitoring und robuste Architektur."}},
            {"id":"privacy","title":"Privacy & Data Governance","xp":170,"difficulty":"Advanced","minutes":55,"theory":"Minimiere Datenerhebung, klassifiziere Daten, definiere Retention, verschlüssele Übertragung und Speicherung und kontrolliere Provider-Verwendung und Logging.","example":"```text\ncollect minimum -> classify -> authorize -> redact -> retain briefly -> delete\n```","quiz":{"q":"Was ist Data Minimization?","options":["Alle Daten dauerhaft speichern","Nur notwendige Daten erheben und verarbeiten","Daten ohne Zweck kopieren","Logs öffentlich machen"],"answer":1,"why":"Weniger Daten reduzieren Datenschutz- und Sicherheitsrisiken."}},
            {"id":"redteam","title":"Red Teaming & Guardrails","xp":180,"difficulty":"Advanced","minutes":60,"theory":"Teste Missbrauch, Jailbreaks, PII-Leaks, Tool-Manipulation, Halluzinationen und Grenzfälle. Guardrails sollten Risiken reduzieren, ohne legitime Nutzung unnötig zu blockieren.","example":"```text\nattack library -> automated tests -> human red team -> fixes -> regression suite\n```","quiz":{"q":"Was ist ein gutes Red-Team-Ergebnis?","options":["Nur eine Liste kreativer Angriffe","Reproduzierbare Befunde mit Schweregrad und Regressionstest","Keine Dokumentation","Ein längerer Systemprompt"],"answer":1,"why":"Befunde müssen priorisierbar und dauerhaft testbar sein."}},
        ]
    },
    {
        "id":"production", "title":"9. Production AI & LLMOps", "icon":"⚙️", "color":"#06B6D4",
        "description":"Deployment, Skalierung, Tracing, Caching, CI/CD und Kostenkontrolle.",
        "lessons":[
            {"id":"deployment","title":"APIs, Containers & Deployment","xp":180,"difficulty":"Advanced","minutes":65,"theory":"Produktive AI-Dienste benötigen stabile APIs, Konfiguration, Secrets Management, Container, Health Checks, Timeouts, Retries und horizontale Skalierung.","example":"```text\nclient -> gateway -> application API -> model/retrieval providers\n```","quiz":{"q":"Wo sollten API-Schlüssel gespeichert werden?","options":["Im Git-Repository","In einem Secret Manager oder geschützter Laufzeitkonfiguration","Im Prompt","In öffentlichen Logs"],"answer":1,"why":"Secrets dürfen nicht versioniert oder öffentlich protokolliert werden."}},
            {"id":"observability","title":"Tracing, Metrics & Logging","xp":190,"difficulty":"Advanced","minutes":65,"theory":"Erfasse Trace IDs, Modellversion, Promptversion, Retrievalergebnisse, Tool Calls, Tokenverbrauch, Latenz und Fehler – ohne unnötige sensible Daten zu loggen.","example":"```text\nrequest trace -> retrieval span -> model span -> tool span -> response\n```","quiz":{"q":"Welche Kennzahl ist für Streaming UX besonders relevant?","options":["Time to first token","Repository-Größe","Trainings-Epochen","Anzahl CSS-Regeln"],"answer":0,"why":"Time to first token bestimmt, wie schnell die Ausgabe für Nutzer beginnt."}},
            {"id":"resilience","title":"Reliability, Caching & Cost Control","xp":180,"difficulty":"Advanced","minutes":60,"theory":"Nutze Timeouts, begrenzte Retries mit Backoff, Circuit Breaker, Fallbacks, Idempotenz, semantisches Caching und Budgets.","example":"```text\nretry only transient failures; cap attempts; add jitter; avoid retry storms\n```","quiz":{"q":"Warum müssen Retries begrenzt werden?","options":["Damit Fehler und Last nicht verstärkt werden","Damit Logs leer bleiben","Damit keine APIs existieren","Weil Backoff verboten ist"],"answer":0,"why":"Unbegrenzte Retries können Ausfälle verschärfen und hohe Kosten verursachen."}},
        ]
    },
    {
        "id":"career", "title":"10. AI Engineer Career Lab", "icon":"🎯", "color":"#A855F7",
        "description":"System Design, Portfolio, Interviews und reale End-to-End-Projekte.",
        "lessons":[
            {"id":"system_design","title":"AI System Design","xp":200,"difficulty":"Advanced","minutes":75,"theory":"Beginne mit Anforderungen, Qualitätsmetriken, Traffic, Daten und Risiken. Entwirf Komponenten, Schnittstellen, Failure Modes, Observability und Kostenmodell.","example":"```text\nrequirements -> architecture -> data flow -> evals -> failure modes -> rollout\n```","quiz":{"q":"Was sollte am Anfang eines System-Design-Interviews geklärt werden?","options":["Nur die Programmiersprache","Anforderungen, Constraints und Erfolgskriterien","Logo-Farbe","Welche GPU der Interviewer besitzt"],"answer":1,"why":"Ohne Anforderungen kann keine belastbare Architektur gewählt werden."}},
            {"id":"portfolio","title":"Portfolio-Projekte","xp":180,"difficulty":"All levels","minutes":45,"theory":"Ein starkes Portfolio zeigt Problemdefinition, Architektur, Daten, Evals, Trade-offs, Deployment, Monitoring und eine ehrliche Fehleranalyse – nicht nur eine Chat-UI.","example":"```text\nREADME + architecture diagram + eval report + live demo + tests + postmortem\n```","quiz":{"q":"Was unterscheidet ein starkes AI-Portfolio-Projekt?","options":["Viele Framework-Logos","Messbare Qualität und nachvollziehbare Engineering-Entscheidungen","Nur ein Screenshot","Keine Dokumentation"],"answer":1,"why":"Arbeitgeber suchen belastbare Problemlösung und Engineering-Reife."}},
            {"id":"interview","title":"Interview Practice","xp":170,"difficulty":"Advanced","minutes":60,"theory":"Übe Python, APIs, Datenstrukturen, ML/LLM-Grundlagen, RAG, Evals, System Design, Debugging und produktorientierte Trade-offs.","example":"```text\nExplain: why this architecture, how to measure it, what fails, what it costs.\n```","quiz":{"q":"Wie beantwortet man eine Architekturfrage am besten?","options":["Sofort Frameworks aufzählen","Annahmen klären und Trade-offs strukturiert begründen","Nur eine perfekte Lösung behaupten","Risiken ignorieren"],"answer":1,"why":"System Design bewertet strukturiertes Denken unter Unsicherheit."}},
        ]
    },
]

CURRICULUM_ERRORS = validate_labs(TRACKS)
for _track in TRACKS:
    for _lesson in _track["lessons"]:
        _lesson["lab"] = build_lesson_lab(_lesson)

PROJECTS = [
    {"title":"1. Support Ticket Classifier","level":"Foundation","deliverables":["REST-API", "validiertes Ausgabe-Schema", "Unit Tests", "Metrik-Report"],"skills":["Python","APIs","ML/Evals"]},
    {"title":"2. Citation-first Knowledge Assistant","level":"Core","deliverables":["Ingestion Pipeline", "Hybrid Retrieval", "Quellenangaben", "RAG-Eval-Dataset"],"skills":["RAG","Embeddings","Evaluation"]},
    {"title":"3. Tool-using Operations Copilot","level":"Advanced","deliverables":["State Machine", "Tool Permissions", "Human Approval", "Tracing"],"skills":["Agents","Security","Observability"]},
    {"title":"4. Production AI Platform","level":"Job-ready","deliverables":["Container Deployment", "CI/CD", "Canary Rollout", "Cost Dashboard", "Incident Runbook"],"skills":["LLMOps","Reliability","System Design"]},
]

BADGES = [
    ("First Steps", 1, "Eine Lektion abgeschlossen"),
    ("Builder", 5, "Fünf Lektionen abgeschlossen"),
    ("AI Practitioner", 10, "Zehn Lektionen abgeschlossen"),
    ("Systems Thinker", 20, "Zwanzig Lektionen abgeschlossen"),
    ("AI Engineer", 30, "Alle Lektionen abgeschlossen"),
]

DEFAULT_PROGRESS = {
    "completed": [], "quiz_correct": [], "challenge_correct": [], "xp": 0,
    "streak": 0, "last_active": None, "notes": {}, "projects": {}
}


def load_progress() -> dict[str, Any]:
    if PROGRESS_FILE.exists():
        try:
            data = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
            return {**DEFAULT_PROGRESS, **data}
        except (json.JSONDecodeError, OSError):
            pass
    return DEFAULT_PROGRESS.copy()


def save_progress() -> None:
    try:
        PROGRESS_FILE.write_text(json.dumps(st.session_state.progress, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass


def all_lessons() -> list[tuple[dict[str, Any], dict[str, Any]]]:
    return [(track, lesson) for track in TRACKS for lesson in track["lessons"]]


def lesson_key(track: dict[str, Any], lesson: dict[str, Any]) -> str:
    return f"{track['id']}::{lesson['id']}"


def get_level(xp: int) -> tuple[int, int, int]:
    level = xp // 500 + 1
    current = xp % 500
    return level, current, 500


def update_streak() -> None:
    today = date.today()
    last = st.session_state.progress.get("last_active")
    if last:
        try:
            delta = (today - date.fromisoformat(last)).days
            if delta == 1:
                st.session_state.progress["streak"] += 1
            elif delta > 1:
                st.session_state.progress["streak"] = 1
        except ValueError:
            st.session_state.progress["streak"] = 1
    else:
        st.session_state.progress["streak"] = 1
    st.session_state.progress["last_active"] = today.isoformat()
    save_progress()


def mark_complete(track: dict[str, Any], lesson: dict[str, Any]) -> None:
    key = lesson_key(track, lesson)
    if key not in st.session_state.progress["completed"]:
        st.session_state.progress["completed"].append(key)
        st.session_state.progress["xp"] += lesson["xp"]
        save_progress()
        st.balloons()


def run_python(code: str, tests: str) -> tuple[bool, str]:
    try:
        ast.parse(code)
    except SyntaxError as exc:
        return False, f"Syntaxfehler: {exc}"
    script = code + "\n\n" + tests
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(script)
            path = f.name
        result = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=3)
        Path(path).unlink(missing_ok=True)
        if result.returncode == 0:
            return True, "Alle Tests bestanden."
        return False, (result.stderr or result.stdout)[-2000:]
    except subprocess.TimeoutExpired:
        return False, "Zeitlimit überschritten. Prüfe Endlosschleifen."
    except OSError as exc:
        return False, f"Code konnte nicht ausgeführt werden: {exc}"


if "progress" not in st.session_state:
    st.session_state.progress = load_progress()
    update_streak()
if "navigation_page" not in st.session_state:
    st.session_state.navigation_page = "Dashboard"
if "pending_navigation" in st.session_state:
    # A widget-backed Session State key may only be changed before the widget
    # is instantiated. Navigation buttons therefore queue the destination for
    # the next rerun instead of mutating the radio key in their click run.
    st.session_state.navigation_page = st.session_state.pop("pending_navigation")
if "selected_lesson" not in st.session_state:
    st.session_state.selected_lesson = None

st.markdown("""
<style>
.stApp {background: radial-gradient(circle at 20% 0%, #17203a 0, #0b1020 35%, #080c18 100%);}
.hero {padding: 2rem; border: 1px solid rgba(139,92,246,.35); border-radius: 24px; background: linear-gradient(135deg, rgba(139,92,246,.18), rgba(14,165,233,.08)); margin-bottom: 1rem;}
.card {padding: 1.2rem; border: 1px solid rgba(148,163,184,.18); border-radius: 18px; background: rgba(21,28,50,.72); min-height: 150px;}
.lesson-card {padding: 1rem; border-left: 4px solid #8B5CF6; border-radius: 12px; background: rgba(21,28,50,.75); margin-bottom: .65rem;}
.objective-card {padding:.9rem 1rem; border-radius:14px; background:rgba(14,165,233,.08); border:1px solid rgba(14,165,233,.22); height:100%;}
.source-link {display:inline-block; color:#c4b5fd; background:rgba(139,92,246,.12); border:1px solid rgba(139,92,246,.25); padding:.15rem .5rem; border-radius:999px; font-size:.78rem; margin-bottom:.45rem;}
.status-ok {padding:.8rem 1rem; border-radius:14px; background:rgba(34,197,94,.08); border:1px solid rgba(34,197,94,.25);}
.badge {display:inline-block; padding:.25rem .65rem; border-radius:999px; background:rgba(139,92,246,.18); border:1px solid rgba(139,92,246,.35); margin:.15rem; font-size:.8rem;}
.small {color:#94a3b8; font-size:.86rem;}
[data-testid="stMetric"] {background:rgba(21,28,50,.75); border:1px solid rgba(148,163,184,.15); padding:12px; border-radius:15px;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🧠 AI Academy")
    st.caption("Build 2026-08-05.3")
    page = st.radio("Navigation", ["Dashboard", "Skill Tree", "Lesson Lab", "Projects", "Practice Arena", "Job Readiness"], key="navigation_page")
    level, current_xp, next_xp = get_level(st.session_state.progress["xp"])
    st.divider()
    st.subheader(f"Level {level}")
    st.progress(current_xp / next_xp)
    st.caption(f"{current_xp}/{next_xp} XP bis Level {level+1}")
    st.metric("🔥 Streak", f"{st.session_state.progress['streak']} Tage")
    if st.button("Fortschritt zurücksetzen", type="secondary"):
        st.session_state.progress = DEFAULT_PROGRESS.copy()
        save_progress()
        st.rerun()

completed = set(st.session_state.progress["completed"])
total_lessons = len(all_lessons())
completion_pct = len(completed) / total_lessons if total_lessons else 0

if page == "Dashboard":
    st.markdown("""
    <div class="hero">
      <div class="small">INTERACTIVE CAREER PATH</div>
      <h1>Werde zum produktionsreifen AI Engineer</h1>
      <p>Lerne nicht nur Prompts. Baue, evaluiere, sichere und betreibe reale AI-Systeme.</p>
    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Gesamt-XP", st.session_state.progress["xp"])
    c2.metric("Lektionen", f"{len(completed)}/{total_lessons}")
    c3.metric("Quiz korrekt", len(st.session_state.progress["quiz_correct"]))
    c4.metric("Coding-Challenges", len(st.session_state.progress["challenge_correct"]))
    st.progress(completion_pct, text=f"Gesamtfortschritt: {completion_pct:.0%}")

    st.subheader("Deine nächste Mission")
    next_item = next(((t, l) for t, l in all_lessons() if lesson_key(t, l) not in completed), None)
    if next_item:
        t, l = next_item
        col1, col2 = st.columns([4,1])
        with col1:
            st.markdown(f"### {t['icon']} {l['title']}")
            st.write(t["description"])
            st.caption(f"{l['difficulty']} · {l['minutes']} Min · +{l['xp']} XP")
        with col2:
            if st.button("Mission starten", type="primary", use_container_width=True):
                st.session_state.selected_lesson = lesson_key(t,l)
                st.session_state.pending_navigation = "Lesson Lab"
                st.rerun()
    else:
        st.success("Alle Curriculum-Lektionen abgeschlossen. Beginne jetzt die Portfolio-Projekte.")

    st.subheader("Track-Fortschritt")
    rows = []
    for track in TRACKS:
        done = sum(lesson_key(track,l) in completed for l in track["lessons"])
        rows.append({"Track":track["title"], "Abgeschlossen":done, "Gesamt":len(track["lessons"]), "Fortschritt":done/len(track["lessons"])})
    df = pd.DataFrame(rows)
    fig = px.bar(df, x="Fortschritt", y="Track", orientation="h", text=df["Fortschritt"].map(lambda x:f"{x:.0%}"), range_x=[0,1])
    fig.update_layout(height=450, margin=dict(l=0,r=0,t=10,b=0), showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Badges")
    for name, threshold, desc in BADGES:
        unlocked = len(completed) >= threshold
        st.markdown(f"<span class='badge'>{'🏆' if unlocked else '🔒'} <b>{name}</b> — {desc}</span>", unsafe_allow_html=True)

elif page == "Skill Tree":
    st.title("Skill Tree")
    st.write("Arbeite dich von Engineering-Grundlagen bis zu produktionsreifen AI-Systemen vor.")
    for track in TRACKS:
        done = sum(lesson_key(track,l) in completed for l in track["lessons"])
        with st.expander(f"{track['icon']} {track['title']} — {done}/{len(track['lessons'])}", expanded=done < len(track["lessons"])):
            st.write(track["description"])
            st.progress(done/len(track["lessons"]))
            for lesson in track["lessons"]:
                key = lesson_key(track,lesson)
                status = "✅" if key in completed else "⬜"
                c1,c2 = st.columns([5,1])
                with c1:
                    st.markdown(f"**{status} {lesson['title']}**  ")
                    st.caption(f"{lesson['difficulty']} · {lesson['minutes']} Min · {lesson['xp']} XP")
                with c2:
                    if st.button("Öffnen", key=f"open-{key}", use_container_width=True):
                        st.session_state.selected_lesson = key
                        st.session_state.pending_navigation = "Lesson Lab"
                        st.rerun()

elif page == "Lesson Lab":
    st.title("Lesson Lab")
    options = {lesson_key(t,l):f"{t['icon']} {t['title']} → {l['title']}" for t,l in all_lessons()}
    selected = st.selectbox("Lektion", list(options), format_func=options.get, index=list(options).index(st.session_state.selected_lesson) if st.session_state.selected_lesson in options else 0)
    st.session_state.selected_lesson = selected
    track, lesson = next((t,l) for t,l in all_lessons() if lesson_key(t,l)==selected)
    key = selected
    st.markdown(f"<div class='hero'><div class='small'>{track['title'].upper()}</div><h1>{lesson['title']}</h1><p>{lesson['difficulty']} · {lesson['minutes']} Minuten · +{lesson['xp']} XP</p></div>", unsafe_allow_html=True)

    if CURRICULUM_ERRORS:
        st.error("Curriculum-Vertrag verletzt: " + " · ".join(CURRICULUM_ERRORS))
        st.stop()

    lab = lesson["lab"]
    section_titles = {section["id"]: section["title"] for section in lab["sections"]}
    answered = sum(f"{key}::quiz::{q['id']}" in st.session_state.progress["quiz_correct"] for q in lab["quiz"])
    c1, c2, c3 = st.columns(3)
    c1.metric("Theorie-Kapitel", len(lab["sections"]))
    c2.metric("Fragen gemeistert", f"{answered}/{len(lab['quiz'])}")
    c3.metric("Praxisphasen", "2", help="Debug Lab und Build Mission")

    tab1, tab2, tab3, tab4 = st.tabs(["📖 Learn", "🧠 Quiz", "🛠️ Debug & Build", "📝 Notes"])
    with tab1:
        st.subheader("Das kannst du nach dieser Lektion")
        objective_columns = st.columns(min(3, len(lab["objectives"])))
        for index, objective in enumerate(lab["objectives"]):
            with objective_columns[index % len(objective_columns)]:
                st.markdown(f"<div class='objective-card'><b>0{index + 1}</b><br>{objective}</div>", unsafe_allow_html=True)
        st.divider()
        st.subheader("Geführter Lernpfad")
        st.caption("Die Kapitel bilden die Wissensbasis für Quiz, Debug Lab und Build Mission. Verweise in den Aufgaben führen zu genau diesen Abschnitten zurück.")
        for section_index, section in enumerate(lab["sections"]):
            with st.expander(section["title"], expanded=section_index == 0):
                st.markdown(section["body"])
                st.caption(f"Kapitel-ID: {section['id']}")
        st.info("Engineer-Mindset: Erst Vertrag und erwartetes Verhalten verstehen, dann Failure Modes benennen, danach implementieren und mit einem beobachtbaren Test verifizieren.")
    with tab2:
        st.subheader("Verstehen, anwenden, diagnostizieren")
        st.write("Die Fragen prüfen nicht unabhängiges Trivia: Jede Frage nennt das Learn-Kapitel, aus dem du die Antwort herleiten kannst.")
        for question_index, q in enumerate(lab["quiz"], start=1):
            quiz_key = f"{key}::quiz::{q['id']}"
            with st.container(border=True):
                st.markdown(f"<span class='source-link'>↩ Learn · {section_titles[q['source']]}</span>", unsafe_allow_html=True)
                st.markdown(f"**Frage {question_index} von {len(lab['quiz'])}**")
                answer = st.radio(q["q"], q["options"], key=f"quiz-answer-{quiz_key}", label_visibility="visible")
                if st.button("Antwort prüfen", key=f"check-{quiz_key}"):
                    idx = q["options"].index(answer)
                    if idx == q["answer"]:
                        st.success("Richtig. " + q["why"])
                        if quiz_key not in st.session_state.progress["quiz_correct"]:
                            st.session_state.progress["quiz_correct"].append(quiz_key)
                            st.session_state.progress["xp"] += 10
                            save_progress()
                    else:
                        st.error("Noch nicht. " + q["why"])
        if answered == len(lab["quiz"]):
            st.markdown("<div class='status-ok'><b>Quiz gemeistert.</b> Jetzt kannst du das Wissen im Debug Lab anwenden.</div>", unsafe_allow_html=True)
    with tab3:
        debug_tab, build_tab = st.tabs(["🧯 Debug Lab", "🏗️ Build Mission"])
        with debug_tab:
            debug = lab["debug"]
            st.markdown(f"<span class='source-link'>↩ Learn · {section_titles[debug['source']]}</span>", unsafe_allow_html=True)
            st.subheader("Vom Symptom zur belastbaren Korrektur")
            st.markdown("**Kaputtes Artefakt**")
            st.markdown(debug["snippet"])
            st.error(debug["symptom"])
            st.write(debug["task"])
            st.text_area("Deine korrigierte Version", height=220, key=f"debug-fix-{key}", placeholder="Ändere den Code, die Konfiguration oder den Ablauf so, dass die Ursache behoben wird …")
            st.text_area("Ursache, Fix und Regressionstest", height=150, key=f"debug-reason-{key}", placeholder="1. Ursache …\n2. Korrektur …\n3. So beweise ich den Fix …")
            st.markdown("**Self-check vor der Musterlösung**")
            checks = [st.checkbox(item, key=f"debug-check-{key}-{i}") for i, item in enumerate(debug["checkpoints"])]
            if st.button("Musterlösung freischalten", key=f"debug-solution-{key}", disabled=not all(checks)):
                st.session_state[f"show-debug-solution-{key}"] = True
            if st.session_state.get(f"show-debug-solution-{key}"):
                st.success("Mögliche belastbare Lösung: " + debug["expected"])
                completion_key = f"{key}::debug"
                if completion_key not in st.session_state.progress["challenge_correct"]:
                    st.session_state.progress["challenge_correct"].append(completion_key)
                    st.session_state.progress["xp"] += 20
                    save_progress()
        with build_tab:
            build = lab["build"]
            st.subheader(build["title"])
            st.markdown(build["brief"])
            st.markdown("#### Arbeitsauftrag in fünf Stufen")
            for step_index, step in enumerate(build["steps"], start=1):
                st.markdown(f"**{step_index}.** {step}")
            st.info("Abgabeformat: " + build["deliverable"])
            st.text_area("Dein Artefakt / deine Lösung", height=300, key=f"mission-{key}", placeholder="Arbeite die fünf Stufen sichtbar ab …")
            st.markdown("#### Abnahme-Rubrik")
            rubric_checks = [st.checkbox(item, key=f"build-rubric-{key}-{i}") for i, item in enumerate(build["rubric"])]
            st.progress(sum(rubric_checks) / len(rubric_checks), text=f"{sum(rubric_checks)}/{len(rubric_checks)} Kriterien erfüllt")
            if all(rubric_checks):
                st.success("Die Mission erfüllt die vollständige Engineering-Rubrik. Sichere dein Artefakt in den Notizen oder in einem eigenen Repository.")
                completion_key = f"{key}::build"
                if completion_key not in st.session_state.progress["challenge_correct"]:
                    st.session_state.progress["challenge_correct"].append(completion_key)
                    st.session_state.progress["xp"] += 30
                    save_progress()
    with tab4:
        note = st.text_area("Eigene Notizen", st.session_state.progress["notes"].get(key,""), height=240, key=f"notes-{key}")
        if st.button("Notizen speichern", key=f"save-note-{key}"):
            st.session_state.progress["notes"][key] = note
            save_progress()
            st.success("Gespeichert.")
    st.divider()
    if key in completed:
        st.success("Lektion abgeschlossen.")
    elif st.button(f"Lektion abschließen (+{lesson['xp']} XP)", type="primary"):
        mark_complete(track,lesson)
        st.rerun()

elif page == "Projects":
    st.title("Portfolio Questline")
    st.write("Vier Projekte führen dich von einem kleinen Service bis zu einer produktionsreifen AI-Plattform.")
    for i, project in enumerate(PROJECTS):
        project_key = f"project-{i}"
        with st.container(border=True):
            c1,c2 = st.columns([4,1])
            with c1:
                st.subheader(project["title"])
                st.caption(project["level"])
                st.write("**Deliverables:** " + " · ".join(project["deliverables"]))
                st.write("**Skills:** " + " · ".join(project["skills"]))
            with c2:
                status = st.selectbox("Status", ["Nicht begonnen","In Arbeit","Fertig"], index=["Nicht begonnen","In Arbeit","Fertig"].index(st.session_state.progress["projects"].get(project_key,"Nicht begonnen")), key=f"status-{i}")
                if status != st.session_state.progress["projects"].get(project_key):
                    st.session_state.progress["projects"][project_key] = status
                    save_progress()
            st.text_area("Projektlog / nächster Schritt", st.session_state.progress["notes"].get(project_key,""), key=f"project-note-{i}")
            if st.button("Projektlog speichern", key=f"project-save-{i}"):
                st.session_state.progress["notes"][project_key] = st.session_state[f"project-note-{i}"]
                save_progress()
                st.success("Projektlog gespeichert.")

elif page == "Practice Arena":
    st.title("Practice Arena")
    mode = st.selectbox("Trainingsmodus", ["System Design", "Incident Response", "Trade-off Drill", "Explain Like an Engineer"])
    prompts = {
        "System Design":"Entwirf einen internen Wissensassistenten für 5.000 Mitarbeitende. Anforderungen: Quellenangaben, Rollenrechte, 2 Sekunden mediane Latenz, sensible Dokumente.",
        "Incident Response":"Seit einem Modellwechsel steigt die Halluzinationsrate, während Kosten sinken. Erstelle Diagnoseplan, Sofortmaßnahmen, Rollback-Kriterien und langfristige Fixes.",
        "Trade-off Drill":"Vergleiche kleines schnelles Modell + RAG mit großem Modell ohne RAG hinsichtlich Qualität, Aktualität, Kosten, Datenschutz und Betrieb.",
        "Explain Like an Engineer":"Erkläre einem Product Manager den Unterschied zwischen Prompt Engineering, RAG, Fine-Tuning und Tool Calling. Nenne Entscheidungskriterien."
    }
    st.markdown(f"### Challenge\n{prompts[mode]}")
    response = st.text_area("Deine Antwort", height=320)
    rubric = ["Anforderungen geklärt", "Messgrößen definiert", "Architektur/Ansatz strukturiert", "Failure Modes berücksichtigt", "Trade-offs und Kosten benannt", "Rollout und Monitoring erklärt"]
    st.subheader("Self-review")
    score = 0
    for item in rubric:
        if st.checkbox(item, key=f"rubric-{mode}-{item}"):
            score += 1
    st.progress(score/len(rubric), text=f"{score}/{len(rubric)} Engineering-Kriterien")
    if response and score == len(rubric):
        st.success("Die Antwort deckt die zentrale Engineering-Rubric ab. Prüfe nun Präzision und konkrete Zahlenannahmen.")

elif page == "Job Readiness":
    st.title("Job Readiness Radar")
    categories = {
        "Software Engineering":["foundations"],
        "ML Fundamentals":["ml","deep"],
        "LLM Applications":["llm","rag"],
        "Agents":["agents"],
        "Evaluation":["eval"],
        "Safety":["safety"],
        "Production":["production"],
        "System Design":["career"],
    }
    scores=[]
    for name, ids in categories.items():
        relevant=[(t,l) for t,l in all_lessons() if t["id"] in ids]
        score=100*sum(lesson_key(t,l) in completed for t,l in relevant)/len(relevant)
        scores.append({"Skill":name,"Score":score})
    df=pd.DataFrame(scores)
    fig=px.line_polar(df, r="Score", theta="Skill", line_close=True, range_r=[0,100])
    fig.update_traces(fill="toself")
    fig.update_layout(height=520, paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig,use_container_width=True)
    weakest=df.sort_values("Score").iloc[0]
    st.info(f"Nächster Fokus: **{weakest['Skill']}** ({weakest['Score']:.0f}%).")
    st.subheader("Job-ready Checklist")
    checklist=[
        "Ich kann eine robuste Python-API mit Tests bauen.",
        "Ich kann RAG getrennt nach Retrieval und Generation evaluieren.",
        "Ich kann Tools und Agents mit Least Privilege absichern.",
        "Ich kann Kosten, Latenz und Qualität messen und optimieren.",
        "Ich kann ein AI-System deployen, beobachten und zurückrollen.",
        "Ich habe mindestens zwei dokumentierte End-to-End-Projekte.",
        "Ich kann Architekturentscheidungen und Trade-offs erklären.",
    ]
    checked=sum(st.checkbox(item,key=f"ready-{i}") for i,item in enumerate(checklist))
    st.progress(checked/len(checklist),text=f"{checked}/{len(checklist)} Job-ready Kriterien")
