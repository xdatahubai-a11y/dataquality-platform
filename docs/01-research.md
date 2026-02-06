# Research Report: Data Quality Platform

## Executive Summary
Comprehensive analysis of the data quality tool landscape, identifying gaps and opportunities for an enterprise DQ platform targeting Azure/Spark environments.

## Competitor Analysis

| Tool | Strengths | Weaknesses | Pricing |
|------|-----------|------------|---------|
| **Great Expectations** | Large community, 300+ expectations, good docs | Complex setup, steep learning curve, no native UI | OSS / GX Cloud ~$5k/mo |
| **Soda** | Simple YAML syntax (SodaCL), good CI/CD integration | Limited Spark support, cloud required for full features | OSS / Soda Cloud ~$10k/yr |
| **Deequ** | Native Spark, constraint suggestion, scalable | AWS-centric, Scala only, no UI, sparse docs | OSS (Apache 2.0) |
| **Monte Carlo** | Automated anomaly detection, lineage, incident mgmt | Expensive, black-box ML, no custom rules | $50k-200k/yr |
| **Atlan** | Unified catalog + DQ, good UX | DQ is secondary, expensive | $36k+/yr |
| **Collibra DQ** | Automated profiling, Spark support | Very expensive, complex, vendor lock-in | $100k+/yr |

## Standards
- **ISO 25012**: 15 data quality characteristics
- **DAMA DMBOK**: 6 core dimensions — Completeness, Uniqueness, Accuracy, Consistency, Timeliness, Validity
- **ISO 8000**: Master data quality management

## Key Gaps in Current Tools
1. No tool combines configurable rule engine + Spark execution + Azure-native deployment
2. Most lack YAML-based rules WITH Python extensibility
3. No OSS tool provides DQ scoring with historical trending dashboards
4. Limited Delta Lake and Lakehouse table profiling support
5. Poor Azure-native deployment patterns (Container Apps, Managed Identity)

## Technical Decisions
- **Rule Engine**: Hybrid YAML + Python (declarative for 80%, code for 20%)
- **Backend**: FastAPI (Python-first for Spark alignment)
- **Dashboard**: React + TypeScript + Recharts
- **Database**: PostgreSQL (reliable, JSON support)
- **Deployment**: Azure Container Apps (simpler than AKS)
- **Spark**: PySpark with local/cluster submit modes
