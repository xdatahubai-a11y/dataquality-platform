"""Spark job submission utilities."""

import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class SparkSubmitConfig:
    """Configuration for Spark job submission."""

    master: str = "local[*]"
    deploy_mode: str = "client"
    driver_memory: str = "2g"
    executor_memory: str = "4g"
    num_executors: int = 2
    packages: str = "io.delta:delta-spark_2.12:3.0.0"


def submit_dq_job(
    job_config: dict,
    spark_config: Optional[SparkSubmitConfig] = None,
) -> subprocess.CompletedProcess:
    """Submit a DQ job via spark-submit.

    Args:
        job_config: Job configuration dict.
        spark_config: Spark submission configuration.

    Returns:
        CompletedProcess with stdout/stderr.
    """
    cfg = spark_config or SparkSubmitConfig()

    # Write job config to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(job_config, f)
        config_path = f.name

    job_script = str(Path(__file__).parent / "dq_job.py")

    cmd = [
        "spark-submit",
        "--master", cfg.master,
        "--deploy-mode", cfg.deploy_mode,
        "--driver-memory", cfg.driver_memory,
        "--executor-memory", cfg.executor_memory,
        "--num-executors", str(cfg.num_executors),
        "--packages", cfg.packages,
        job_script,
        config_path,
    ]

    return subprocess.run(cmd, capture_output=True, text=True, timeout=3600)


def submit_local(job_config: dict) -> dict:
    """Run DQ job locally (no Spark cluster needed).

    Useful for development and testing.
    """
    from spark.dq_job import run_dq_checks
    return run_dq_checks(job_config)
