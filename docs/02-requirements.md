# Product Requirements

## Personas
- **Data Engineer**: Builds pipelines, configures DQ rules programmatically, monitors jobs
- **Data Steward**: Defines business DQ rules, monitors scores, investigates issues
- **Platform Admin**: Manages deployment, security, scheduling

## MVP Scope
1. All 6 DQ dimension calculators (completeness, uniqueness, accuracy, consistency, timeliness, validity)
2. Rule CRUD API with YAML support
3. ADLS Gen2, Delta Table, SQL Server connectors
4. Spark job submission and monitoring
5. Dashboard: metrics overview, history, score cards
6. Docker-based deployment with PostgreSQL

## Epics
- **DQ Dimensions**: 6 stories (one per dimension) — all MUST priority
- **Rule Engine**: CRUD, YAML config, list/filter — MUST; SQL rules SHOULD; Python rules COULD
- **Data Sources**: ADLS Gen2, Delta, SQL Server connections + management — MUST
- **Spark Jobs**: Submit, monitor, history — MUST; Retry — SHOULD
- **Dashboard**: Metrics overview, historical runs, score cards — MUST; Rule UI — SHOULD
- **Scheduling**: Cron-based — SHOULD; Event-triggered — COULD
- **Deployment**: Container deployment — MUST; Managed Identity — SHOULD

## Future Phases
- Phase 2: Scheduling, custom Python rules, SQL rules, alerting
- Phase 3: Data lineage, anomaly detection, multi-tenant, RBAC
- Phase 4: Catalog integration (Purview), streaming DQ checks
