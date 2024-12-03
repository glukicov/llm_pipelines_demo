import configparser
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from google.cloud import aiplatform
from kfp import compiler
from kfp import local as kfp_local

logging.basicConfig(level=logging.INFO)
CURRENT_DIR = Path(__file__).parent


def get_value_from_config(
    option: str, config_file: Path = Path(CURRENT_DIR, "config.cfg")
) -> str:
    """Get a value from the config.cfg file before runtime."""
    config = configparser.ConfigParser()
    config.read(config_file)
    return config.get(section="job_constants", option=option)


@dataclass
class JobParams:
    """Store job parameters."""

    pipeline_name: str = "demo"
    experiment_name: str = "demo-experiment"
    data_source: str = "my_prompts"
    model_name: str = "gpt5"
    enable_caching: bool = True


@dataclass
class JobConstants:
    """Store job constants."""

    USER: str = str(os.getenv("USER")).lower()
    LOCATION: str = "us-central1"
    GCP_PROJECT: str = get_value_from_config(option="gcp_project")
    BASE_IMAGE: str = get_value_from_config(option="base_image")
    REPO_NAME: str = get_value_from_config(option="repo_name")
    SERVICE_ACCOUNT: str = f"{get_value_from_config(option="sa_name")}@{GCP_PROJECT}.iam.gserviceaccount.com"


job_params = JobParams()
job_constants = JobConstants()


def compile_and_run_pipeline_locally(pipeline_func):
    """Compile and run the pipeline locally."""
    compiler.Compiler().compile(
        pipeline_func=pipeline_func,
        package_path=str(Path(CURRENT_DIR, "compiled/pipeline.json")),
    )
    kfp_local.init(runner=kfp_local.DockerRunner())
    pipeline_func()


def get_date_time_now() -> str:
    """Return current date & time, e.g. `2024-08-08--15-27-51`"""
    london_tz = ZoneInfo("Europe/London")
    return datetime.now(tz=london_tz).strftime("%Y-%m-%d--%H-%M-%S")


def compile_and_run_pipeline_on_vertex(
    params: JobParams, constants: JobConstants, pipeline_func
):
    """Compile and run the pipeline on Vertex AI."""
    compiler.Compiler().compile(
        pipeline_func=pipeline_func, package_path="pipeline.json"
    )

    job = aiplatform.PipelineJob(
        display_name=params.pipeline_name,
        template_path="pipeline.json",
        job_id=f"{params.pipeline_name}-{constants.USER}-{get_date_time_now()}",
        enable_caching=params.enable_caching,
        location=constants.LOCATION,
        project=constants.GCP_PROJECT,
    )
    job.submit(
        service_account=constants.SERVICE_ACCOUNT, experiment=params.experiment_name
    )


def run_pipeline_on_vertex_or_locally(
    pipeline_function, params: JobParams, constants: JobConstants, local: bool
):
    """Run the pipeline on Vertex AI or locally."""
    if local:
        logging.info("Running the pipeline locally.")
        compile_and_run_pipeline_locally(pipeline_func=pipeline_function)
    else:
        logging.info(
            f"Running the pipeline on Vertex AI project {job_constants.GCP_PROJECT}."
        )
        compile_and_run_pipeline_on_vertex(
            pipeline_func=pipeline_function, params=params, constants=constants
        )
