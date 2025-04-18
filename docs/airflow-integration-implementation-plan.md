# Airflow Integration Implementation Plan for Trade Manager

**Last Updated:** 2025-04-17

## Overview
This document outlines the plan for integrating the Trade Manager system with the centralized Airflow orchestration system (`airflow-hub`). The integration approach is designed to maintain alignment with the project's advanced portfolio management, risk control, and automation goals, while supporting robust, modular workflows.

---

## Project Goals (from Documentation)
- Provide a sophisticated trading system using Active Inference and Genetic Algorithms for optimal trade execution and portfolio management.
- Maintain modular, extensible code for risk management, portfolio allocation, and trade execution.
- Enable robust system state management, broker integration, and dynamic strategy optimization.
- Support automated, scheduled, and event-driven workflows.

## Airflow Integration Requirements
- **Identify management/execution/reporting functions** suitable for Airflow orchestration (e.g., scheduled portfolio rebalancing, risk audits, trade execution, performance reporting).
- **Refactor or modularize code** to ensure all Airflow tasks are importable/callable (avoid monolithic scripts).
- **Define DAGs** in `airflow-hub/dags/trade-manager/` that reference these callable functions or API endpoints.
- **Manage dependencies** via `airflow-hub/requirements.txt` or containerized tasks as needed.
- **Handle secrets/config** using Airflow connections and variables (never hardcoded).
- **Testing:**
  - Local unit tests remain in this repo.
  - DAG validation and integration tests live in `airflow-hub`.
- **Documentation:**
  - Maintain up-to-date integration docs in both repos.
  - Clearly document required Airflow connection IDs, variables, and expected DAG outputs.

## Implementation Steps
1. **Audit Existing Code**
   - Catalog all management, execution, and reporting functions relevant for Airflow orchestration.
   - Note any incomplete or placeholder code.
2. **Refactor for Modularity**
   - Split monolithic scripts into callable functions/classes.
   - Ensure all business logic to be orchestrated is importable by Airflow.
3. **Task Identification & Design**
   - Define which operations should be triggered by Airflow (e.g., scheduled rebalancing, risk audits, trade execution workflows).
   - Design function signatures and outputs for Airflow compatibility.
4. **DAG Development**
   - Collaborate with `airflow-hub` to create/maintain DAGs in `dags/trade-manager/`.
   - Follow naming conventions and modular structure as per `airflow-hub` integration guide.
5. **Dependency & Secrets Management**
   - List all required external libraries for Airflow tasks.
   - If dependency conflicts arise, prefer containerized Airflow tasks over modifying the shared environment.
   - Document and configure Airflow connections/variables (e.g., `trade_manager_broker_conn`).
6. **Testing & Validation**
   - Write/maintain local unit tests for all Airflow-tasked functions.
   - Ensure DAGs are covered by validation/integration tests in `airflow-hub`.
7. **Documentation & Verification**
   - Update this plan and integration guides as changes are made.
   - Provide clear mapping of Airflow DAGs to underlying functions/scripts.
   - Maintain a checklist for alignment with requirements/goals.

## Implementation Strategy

1.  **DAG Location:** All DAGs orchestrating `trade-manager` tasks will reside in `airflow-hub/dags/trade-manager/`.
2.  **Task Execution:**
    *   All tasks that execute code from the `trade-manager` repository **MUST** use the `airflow.providers.docker.operators.docker.DockerOperator`.
    *   This ensures tasks run in an isolated environment defined by the `trade-manager` project itself.
3.  **Docker Requirement:**
    *   A `Dockerfile` **MUST** exist in the root of the `trade-manager` repository.
    *   This `Dockerfile` will define the image used by the `DockerOperator`.
    *   It must:
        *   Start from a suitable base image (e.g., `python:3.9-slim`).
        *   Copy necessary `trade-manager` application code.
        *   Install dependencies from `trade-manager/requirements.txt`.
4.  **Code Interaction:**
    *   The `DockerOperator` will typically execute a specific script or command within the container (e.g., `docker_operator = DockerOperator(task_id='execute_trade', image='trade-manager:latest', command='python /app/scripts/place_order.py --order_id 123')`).
    *   Refactor `trade-manager` code into callable scripts or functions that can be easily invoked by the `DockerOperator`'s command.
5.  **Plugin Usage:** Common functionality (e.g., custom hooks shared across projects) might still reside in `airflow-hub/plugins/common/` and be used by the DAG definition, but the core `trade-manager` logic runs within its Docker container.
6.  **Dependencies:** All `trade-manager` specific dependencies are managed within its own `Dockerfile` and `requirements.txt`. No `trade-manager` specific dependencies should be added to `airflow-hub`.

## Identified Tasks & DAGs

## Verification Checklist
- [ ] All Airflow tasks are modular, callable, and documented.
- [ ] DAGs in `airflow-hub` reference only importable code from this repo.
- [ ] All dependencies and secrets are managed via Airflow best practices.
- [ ] Unit and integration tests cover all Airflow-integrated functionality.
- [ ] Documentation is up-to-date and clearly describes the integration.
- [ ] Implementation aligns with both the project and Airflow monorepo goals.

---

## References
- [README.md](../README.md)
- [docs/airflow-integration-guide.md](./airflow-integration-guide.md)
- [airflow-hub/docs/integration_guide.md](https://github.com/mprestonsparks/airflow-hub/docs/integration_guide.md)

---

*This plan is a living document and should be updated as the integration progresses or as requirements evolve.*
