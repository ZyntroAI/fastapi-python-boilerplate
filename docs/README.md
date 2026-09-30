c0-fastapi-python-boilerplate/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── migration.py
│   │
│   ├── engine/
│   │   ├── execution_engine.py
│   │   ├── dag.py
│   │   ├── scheduler.py
│   │   └── handlers/
│   │       ├── validate.py
│   │       ├── clone.py
│   │       ├── lfs.py
│   │       ├── create_repo.py
│   │       ├── push.py
│   │       ├── verify.py
│   │       └── report.py
│   │
│   ├── models/
│   │   ├── migration.py
│   │   └── execution.py
│   │
│   ├── services/
│   │   ├── github.py
│   │   ├── gitlab.py
│   │   └── git.py
│   │
│   └── main.py
│
├── plans/
├── executions/
├── reports/
└── tests/
