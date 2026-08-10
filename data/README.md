# Workforce Intelligence Platform Data Layer

> [!WARNING]
> **SYNTHETIC / DEMONSTRATION DATA ONLY**
>
> All employee names, employee numbers, emails, skills, scores, and review histories in this dataset are generated programmatically for demonstration purposes. This is NOT real company or Tata Steel employee data and contains no personally identifiable information (PII).

## Data Provenance
* **Dataset Type**: `SYNTHETIC_DEMO`
* **Industry Context**: Steel Manufacturing / Metallurgy / Industrial Engineering
* **Reference Timeline**: FY 2021-22 to FY 2025-26 (5 years of history)

## Target Statistics
* **Employees**: ~500
* **Departments**: 10
* **Job Roles**: 50
* **Skills**: 200
* **Training Courses**: 100
* **Employee-Skill Relationships**: ~3,000
* **Employee-Training Records**: ~3,000
* **Career Goals**: ~500
* **Performance Reviews**: ~1,000

## Directory Structure
* `raw/`: Raw generated CSV files.
* `processed/`: Validated and cleaned intermediate files (ready for loading).
* `ml/`: Synthetic historical training data reserved for ML training (kept separate from live employee operational data to prevent target leakage).
