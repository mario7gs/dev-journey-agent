🏛️ Architettura Completa del Sistema                 [Ticket Vago / Idea] + [GitHub Repo / Branch]
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 0: Context-Aware Refinement & Code Filtering                        │
│ - PyGithub / AST Parser per estrarre il contesto dalla codebase          │
│ - Chunking / Repo-to-Skill per gestire repo di grandi dimensioni        │
│ - Gap Analysis tra la richiesta e il codice esistente                    │
│ - Human-in-the-Loop: blocking di default; draft mode esplicita           │
└─────────────────────────────────────┬────────────────────────────────────┘
                                      │ (Stato salvato su MEMORY.md)
                                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 1: Job Done, Output Contracts & DoD                                 │
│ - Definizione contratti d'uscita (JSON Response, schema DB, HTTP status) │
│ - Definition of Done (DoD) con Guardrails di sicurezza (Secure-by-Default)│
│ - Milestone Breakdown (Scomposizione in step incrementali 1, 2, 3)       │
└─────────────────────────────────────┬────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 2: PRD, TRD, Flow & Security Assessment                             │
│ - Product Requirements Document (PRD) & Technical Requirements (TRD)     │
│ - Generazione diagrammi di sequenza e flusso in sintassi Mermaid.js      │
│ - Security Audit (OWASP Check, Input Sanitization, Auth Enforcement)     │
└─────────────────────────────────────┬────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ Critic / Self-Correction Agent (Audit di Qualità)                        │
│ - Valida completezza e coerenza dei riferimenti tra le sezioni            │
│ - Esegue un controllo finale anche dopo la generazione del TDD            │
└─────────────────────────────────────┬────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 3: TDD & Implementation Roadmap                                     │
│ - Generazione della suite di test unitari/integrazione (Red-Green Cycle) │
│ - Guida passo-passo di implementazione per lo sviluppatore junior        │
│ - Traceability IDs: REQ → CON/ACC → TEST → STEP                          │
└─────────────────────────────────────┬────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ STEP 4: Export & Stakeholder Delivery                                    │
│ - Salva FEATURE_SPEC.md / HTML / PDF per developer e stakeholder          │
│ - Genera FEATURE_CASE_STUDY.html / PDF per la presentazione portfolio    │
└──────────────────────────────────────────────────────────────────────────┘
🧩 Pillar di Ingegneria del Software Integrati
Resilienza LLM: Fallback automatico dei modelli gestito tramite LiteLLM (primario → fallback → modello locale).
Persistenza audit: checkpoint atomici e resume validato per ogni stage, con MEMORY.md append-only.
Guardrails deterministici: Validazione degli output e imposizione dei requisiti di sicurezza tramite schemi Pydantic.
Human-in-the-loop: blocking di default; draft mode continua l'analisi ma non consente l'approvazione.
Osservabilità Phoenix: recorder JSONL opzionale con run ID, latenza, fallback, token/cost metadata e gate events; bridge OpenTelemetry lazy-loaded when `arize-phoenix-otel` is installed.
Design system: identità D·J con D-delay flag, J-flagpole stabile, percorso ascendente che termina sul bordo della D e freccia contenuta; palette Ink/Indigo/Teal/Gold e token condivisi per HTML/PDF/presentazioni.
📂 Albero delle Cartelle del Progetto
Plaintextdev-journey-agent/
├── MEMORY.md                   # Registro persistente dello stato e dei checkpoint completati
├── README.md                   # Documentazione principale per il portafoglio GitHub
├── pyproject.toml              # Dipendenze del progetto (uv / poetry / pip)
├── .env.example                # Template variabili d'ambiente (OPENAI_API_KEY, GITHUB_TOKEN)
├── .gitignore
│
├── config/                     # Configurazione globale e guardrails
│   ├── __init__.py
│   ├── settings.py             # Setup Arize Phoenix, LiteLLM e variabili d'ambiente
│   └── security_guardrails.py  # Regole e default di sicurezza (Secure-by-Default)
│
├── docs/                       # Documentazione, artefatti e stato implementazione
│   ├── FEATURE_SPEC.md/.html   # Report tecnico e stakeholder
│   ├── IMPLEMENTATION_DASHBOARD.html
│   ├── IMPLEMENTATION_ROADMAP.md
│   └── OPERATIONS.md           # Privacy, recovery, costi e release checks
│
├── src/                        # Source code dell'applicazione
│   ├── __init__.py
│   ├── main.py                 # Entry point CLI e orchestratore principale
│   │
│   ├── core/                   # Gestione memoria e stato
│   │   ├── __init__.py
│   │   ├── state.py            # TypedDict / Pydantic state per il grafo dell'agente
│   │   ├── memory_manager.py   # Modulo di lettura e scrittura su MEMORY.md
│   │   └── traceability.py     # ID deterministici e riferimenti cross-stage
│   │
│   ├── tools/                  # Integrazioni esterne ed export
│   │   ├── __init__.py
│   │   ├── github_client.py    # Client PyGithub read-only (file e albero repo)
│   │   ├── repository_context.py # Contesto bounded read-only per Step 0
│   │   ├── repo_summarizer.py  # Chunking e AST parsing per repository grandi
│   │   ├── html_exporter.py    # Markdown/HTML/PDF orchestration
│   │   ├── pdf_exporter.py     # Rendering PDF tramite Chromium locale
│   │   └── presentation_exporter.py # Case-study portfolio view
│   │
│   ├── schemas/                # Model Pydantic per output deterministici
│   │   ├── __init__.py
│   │   ├── step0_refinement.py # Schema Gap Analysis e domande Human-in-the-Loop
│   │   ├── step1_dod.py        # Schema DoD, Output Contracts e Milestones
│   │   ├── step2_specs.py      # Schema PRD, TRD, Mermaid Flow & Security
│   │   └── step3_tdd.py        # Schema Suite di Test e Guida all'implementazione
│   │
│   ├── agents/                 # Logica dei singoli nodi dell'agente
│   │   ├── __init__.py
│   │   ├── refinement_agent.py # Step 0: Refinement + Code Context
│   │   ├── dod_agent.py        # Step 1: Definition of Done & Output Contracts
│   │   ├── specs_agent.py      # Step 2: PRD / TRD / Security Agent
│   │   ├── tdd_agent.py        # Step 3: TDD Generator
│   │   └── critic_agent.py     # Audit di qualità e auto-correzione
│   │
│   └── templates/              # Template Jinja2 e brand assets
│
└── tests/                      # Test unitari e di integrazione dell'agente
    ├── __init__.py
    ├── test_checkpoints.py
    ├── test_export.py
    ├── test_pipeline_modes.py
    ├── test_telemetry.py
    └── ...                      # suite completa (73 test)

