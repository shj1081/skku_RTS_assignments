# Real-Time Systems Assignments

This repository contains implementations of assignments from the Real-Time Systems course, organized into separate folders. Each folder includes its implementation files and documentation, adhering to course requirements and coding standards.

## Assignments Included

### PA1: Real-Time Task Generation

- **Objective:** Create a program to generate 100 sets of real-time tasks with parameters `(Ti, Ci, Di)` satisfying specific conditions.
- **Grade:** Full score for code
- **Key Features:**
  - Inputs: Number of tasks (`n`), utilization (`U`), and deadline type (`v` for implicit or constrained).
  - Outputs: Task sets saved in the format `yourid_{n}_{U}_{v}.txt` in the `./output` folder.
  - Utilization determined using the UUniFast algorithm.
  - Tasks have randomly generated parameters, ensuring valid real-time constraints.

### PA2: Real-Time Scheduler

- **Objective:** Implement a scheduler that simulates task execution based on various prioritization policies.
- **Grade:** Full score for code
- **Key Features:**
  - Inputs: Task set file, prioritization policy (`FCFS`, `SJF`, `RM`, `EDF`), and preemption option (`p` for preemptive, `np` for non-preemptive).
  - Outputs: Results saved in `yourid_HW2.txt` in the `./output` folder.
  - Simulates task execution for up to 100,000 time units and identifies deadline misses.
  - Supports single-processor, work-conserving scheduling.

### PA3: Schedulability Analysis

- **Objective:** Evaluate the schedulability of real-time task sets using different analysis methods.
- **Grade:** Full score for code
- **Key Features:**
  - Inputs: Task set file, prioritization policy (`RM/DM`, `EDF`), and analysis method (e.g., `U` for utilization-based or `R` for response time).
  - Outputs: Pass (`P`) or Fail (`F`) for each task set, saved in `yourid_HW3.txt` in the `./output` folder.
  - Supports both implicit and constrained deadline task sets.
  - Comprehensive schedulability analysis using response time, utilization-based, and demand-based methods.
