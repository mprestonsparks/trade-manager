# Airflow Integration - Trading System (`trade-manager` Module)

This document explains how the **`trade-manager`** module of the trading system integrates with the centralized 
[airflow-hub](https://github.com/mprestonsparks/airflow-hub) monorepo.

---

## 1. Purpose

- The **`trade-manager`** module contains code that is scheduled or triggered by Airflow. 
- Our ultimate goal: have tasks that run on a schedule or in response to certain events.

## 2. Repository Layout and Code Status

- **Current Code**:  
  - Summarize the major scripts/modules that might be relevant to Airflow.
  - Note which scripts are incomplete or placeholders (i.e., “This is not fully implemented yet”).
- **Code Changes Allowed**:  
  - The AI or maintainers may reorganize these scripts, rename functions, or introduce new modules if necessary for better integration.

## 3. How to Integrate with Airflow-Hub

1. **Identify Potential Tasks**  
   - Decide which functions, classes, or scripts should become Airflow tasks. Typically, tasks do things like “fetch data,” “run analysis,” “generate a report,” etc.

2. **Refactor if Needed**  
   - If your script just has a `main()` function, consider splitting it into smaller callable functions or classes that a DAG can import (e.g., `def fetch_data(): ...`).

3. **Add/Update DAG**  
   - In the `airflow-hub` repo, under `dags/<project_name>/`, create a `.py` file referencing these functions/operators. 
     You can name it something like `dag_project_name_main.py`.

4. **Dependencies**
   - **Execution Environment:** Tasks originating from the `trade-manager` repository **MUST** be executed within Docker containers using the `DockerOperator` in Airflow.
   - **Dockerfile:** A `Dockerfile` **MUST** be maintained within the `trade-manager` repository. This file defines the specific environment (Python version, libraries, system tools) required to run `trade-manager` tasks.
   - **Dependency Management:** All Python dependencies required by `trade-manager` tasks should be listed in a `requirements.txt` file within the `trade-manager` repository and installed within the `Dockerfile`. They should **NOT** be added to the central `airflow-hub/requirements.txt`.
   - **Conflicts:** This containerized approach prevents potential dependency conflicts between `trade-manager` and other projects integrated with `airflow-hub`.

5. **Secrets and Config**  
   - If your code needs credentials (API keys, DB logins), configure an Airflow connection or variable. 
   - Mention the required connection IDs or variable names here (e.g. `project_name_s3_conn`).

6. **Testing**  
   - For local unit tests, keep them in this repo. 
   - For DAG validation, the `airflow-hub/tests/` directory may contain integration tests that reference your code.

## 4. Links

- **Airflow-Hub Integration Guide**: 
  See [integration_guide.md in airflow-hub](https://github.com/mprestonsparks/airflow-hub/docs/integration_guide.md) 
  for the overall structure and best practices.