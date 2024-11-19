import configparser
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import typer
from google.cloud import aiplatform
from kfp import compiler
from kfp import local as kfp_local
from kfp.dsl import Metrics, Output, component, pipeline

logging.basicConfig(level=logging.INFO)


def get_value_from_config(option: str, config_file: Path = Path("config.cfg")) -> str:
    config = configparser.ConfigParser()
    config.read(config_file)
    return config.get(section="job_constants", option=option)


@dataclass
class JobParams:
    pipeline_name: str = "demo"
    experiment_name: str = "demo-experiment"
    data_source: str = "my_prompts"
    model_name: str = "gpt5"
    enable_caching: bool = True


@dataclass
class JobConstants:
    GCP_PROJECT: str = "MY_GCP_PROJECT"
    LOCATION: str = "europe-west2"
    SERVICE_ACCOUNT: str = f"pipeline-runner@{GCP_PROJECT}.iam.gserviceaccount.com"
    BASE_IMAGE: str = get_value_from_config(option="base_image")


job_params = JobParams()
job_constants = JobConstants()


def compile_and_run_pipeline_locally(pipeline_func):
    compiler.Compiler().compile(pipeline_func=pipeline_func, package_path="pipeline.json")
    kfp_local.init(runner=kfp_local.DockerRunner())
    pipeline_func()


def get_date_time_now() -> str:
    """Return current date & time, e.g. `2024-08-08--15-27-51`"""
    london_tz = ZoneInfo("Europe/London")
    return datetime.now(tz=london_tz).strftime("%Y-%m-%d--%H-%M-%S")


def compile_and_run_pipeline_on_vertex(job_params: JobParams, pipeline_func):
    compiler.Compiler().compile(pipeline_func=pipeline_func, package_path="pipeline.json")

    job = aiplatform.PipelineJob(
        display_name=job_params.pipeline_name,
        template_path="pipeline.json",
        job_id=f"{job_params.pipeline_name}-{os.getenv('USER').lower()}-{get_date_time_now()}",
        enable_caching=job_params.enable_caching,
        location=job_constants.LOCATION,
        project=job_constants.GCP_PROJECT,
    )
    job.submit(service_account=job_constants.SERVICE_ACCOUNT, experiment=job_params.experiment_name)


def run_pipeline_on_vertex_or_locally(pipeline_function, job_params: JobParams, local: bool):
    if local:
        logging.info("Running the pipeline locally.")
        compile_and_run_pipeline_locally(pipeline_func=pipeline_function)
    else:
        logging.info(f"Running the pipeline on Vertex AI project {job_constants.GCP_PROJECT}.")
        compile_and_run_pipeline_on_vertex(pipeline_func=pipeline_function, job_params=job_params)


@component(base_image=job_constants.BASE_IMAGE)
def get_data(data_source: str) -> str:
    import logging

    logging.info(f"Getting data from: {data_source}")
    return "data"


@component(base_image=job_constants.BASE_IMAGE)
def call_llm(model_name: str, prompt: str) -> str:
    import logging

    logging.info(f"Calling LLM model {model_name} with prompt: {prompt}")
    return "results"


@component(base_image=job_constants.BASE_IMAGE)
def evaluate_results(results: str, metrics_output: Output[Metrics]):
    metrics_output.metadata = {"accuracy": float(results == "results")}


@pipeline(name=job_params.pipeline_name)
def demo_pipeline():
    # Step 1: Get data
    data_task = get_data(data_source=job_params.data_source)

    # Step 2: Call LLM with the data
    llm_task = call_llm(model_name=job_params.model_name, prompt=data_task.output)

    # Step 3: Evaluate results
    evaluate_results(results=llm_task.output)


if __name__ == "__main__":

    def main(local: bool = typer.Option(False, help="Run the pipeline locally instead of on Vertex AI")):
        run_pipeline_on_vertex_or_locally(pipeline_function=demo_pipeline, job_params=job_params, local=local)

    typer.run(main)
