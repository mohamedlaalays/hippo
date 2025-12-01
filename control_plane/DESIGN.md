# 📄 DESIGN.md: Call Scheduler

***

## 1. High-Level Architecture

| Module | Responsibility | Key Data In/Out |
| :--- | :--- | :--- |
| **Ingestion (`parser.py`)** | Handles file I/O, CSV reading, data validation, and **Time Normalization** (e.g., '9AM' → 9). | **Output:** List of validated `CallRequirement` objects. |
| **Engine (`scheduler.py`)** | Contains the core business logic. Calculates the agents needed per hour using the capacity formula. | **Output:** A 24-element `Schedule` array (indexed 0-23). |
| **Presentation (`formatter.py`)** | Manages CLI arguments (`--format`, `--utilization`) and renders the final schedule to `stdout`. | **Output:** Formatted 24-line text or JSON output. |

***

## 2. Core Algorithms & Implementation Details

### A. Time Normalization and Bucketing

1.  **Normalization:** All time strings are converted to 24-hour integer values (0-23). Special attention is paid to '12AM' (0) and '12PM' (12).
2.  **Boundary Rule:** The scheduling interval is **Start Time (Inclusive)** and **End Time (Exclusive)**. A requirement spanning 9AM to 1PM fills hours 9, 10, 11, and 12.
3.  **24-Hour Handling:** the program accepts `end_hour=24` for schedules that span till midnight, correctly filling all 24 schedule buckets (indices `start_hour` through 23).

### B. Agent Capacity Calculation

The scheduler applies the agent calculation formula to each customer request, assuming a **uniform distribution** of calls across the active duration.

**Required Agents per Hour:**
$$
\text{AgentsNeeded} = \lceil \frac{\text{CallsPerHour} \times \text{AvgDurationSeconds}}{3600 \times \text{Utilization}} \rceil
$$

* **Calls Per Hour:** $\text{CallsPerHour} = \text{TotalCalls} / (\text{EndHour} - \text{StartHour})$.
* **Utilization Parameter:** The `--utilization` flag (defaulting to 1.0) is baked directly into the formula. Setting it to a value like `0.8` (80%) increases the denominator, ensuring **more agents** are scheduled to meet the same demand, thus lowering the workload per agent.
* **Aggregation:** The calculated agents are summed hourly across all customers to produce the `total_agents` count for each 24-hour slot.

***

## 3. Testing and Deployment Strategy


* **Unit Tests:** Focus on the `parser` (time edge cases) and the `scheduler` (mathematical correctness of the agent formula, ensuring correct rounding/ceiling).
* **E2E Golden Test:** A test runs the provided `input.csv` with a fixed utilization and asserts that the resulting **JSON output** is byte-for-byte identical to a checked-in `golden.json` file. This guarantees **Idempotent** output.



## 4. Short Note on Future Work
- **Core Functionality Expansion:**  
  Implement priority-aware scheduling and smoothing logic to handle capacity limits

- **Deployment Readiness:**  
  Add repository scaffolding, linting and commit hooks, CI/CD pipelines, an image registry, and Kubernetes configuration to ensure the system is fully production-ready.

- **System Integration:**  
  Introduce persistent storage for logs and outputs, integrate with upstream data sources, and expose structured outputs for downstream consumers to fit seamlessly into the larger platform.