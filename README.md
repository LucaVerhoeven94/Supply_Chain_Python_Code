# Supply_Chain_Python_Code

┌─────────────────────────────────────────────────────────────────────────┐
│                           SCENARIO INJECTION                            │
│                  (scenarios/isostearic_acid_scenario.py)               │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ Register Network Elements
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        CORE SIMULATION REGISTRY                         │
│                       (simulation/registry.py)                          │
└──────────────┬──────────────────────────────────────────┬───────────────┘
               │ Query Topology                           │ Expose States
               ▼                                          ▼
┌─────────────────────────────────────────┐   ┌───────────────────────────┐
│              LAYOUT ENGINE              │   │     TELEMETRY ENGINE      │
│     (visualization/layout_engine.py)     │   │ (simulation/telemetry.py) │
└──────────────┬──────────────────────────┘   └───────────┬───────────────┘
               │ Compute Node/Edge Matrix                 │
               ▼                                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            RENDERER PIPELINE                            │
│                     (visualization/renderer.py)                         │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                         WIDGET MATRIX                           │   │
│   │  SiteWidget ──> TankWidget ──> ProcessWidget ──> LinkWidget     │   │
│   └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
