import logging
from subprocess import CalledProcessError, run

import typer

from pipelines.demo import job_constants
from pipelines.utils import job_params
from scripts.helpers import get_adc, require_valid_gcp_adc, update_config
from google.cloud import aiplatform


@require_valid_gcp_adc
def build_container(
    project_id: str = job_constants.GCP_PROJECT,
    region: str = job_constants.REGION,
    sa: str = job_constants.SERVICE_ACCOUNT,
    image: str = job_constants.REMOTE_BASE_IMAGE,
    local: bool = True,
) -> None:
    """Build a Kubeflow container 📦."""
    if local:
        logging.info("Starting local build...")
        build_cmd = [
            "docker",
            "compose",
            "-f",
            "docker-compose-kfp-local.yml",
            "build",
            "--build-arg",
            f"ADC={get_adc()}",
        ]

    else:
        logging.info("Starting remote build...")
        build_cmd = [
            "gcloud",
            "builds",
            "submit",
            "--config",
            "cloudbuild-vertex.yml",
            "--project",
            project_id,
            "--region",
            region,
            "--substitutions",
            f"_IMAGE={image}",
            "--service-account",
            f"projects/{project_id}/serviceAccounts/{sa}",
        ]

    try:
        run(build_cmd, check=True)

    except CalledProcessError:
        logging.error("Build failed")
        raise typer.Exit()


def build_container_local() -> None:
    """Build a Kubeflow container locally 📦."""
    build_container(local=True)


def build_container_remote():
    """Submit a remote build for a Kubeflow container 📦."""
    build_container(local=False)


@require_valid_gcp_adc
def run_pipeline(local: bool = True, script_path: str = "pipelines/demo.py") -> None:
    """Run a Kubeflow pipeline 🚀."""
    try:
        mode = "local" if local else "remote"
        logging.info(f"Starting {mode} pipeline run...")

        update_config(local_run=local)
        cmd = ["python", script_path]
        if local:
            cmd.append("--local")

        run(cmd, check=True)

        logging.info(f"{mode.capitalize()} pipeline run completed successfully 🎉")

    except CalledProcessError as e:
        logging.error(f"Pipeline run failed with error: {e}")
        raise


def run_pipeline_local() -> None:
    """Run a Kubeflow pipeline locally 🚀."""
    run_pipeline(local=True)


def run_pipeline_remote() -> None:
    """Run a Kubeflow pipeline remotely 🚀."""
    run_pipeline(local=False)


@require_valid_gcp_adc
def fetch_metrics(
    experiment_name: str = job_params.experiment_name,
    project_id: str = job_constants.GCP_PROJECT,
    region: str = job_constants.REGION,
) -> None:
    """Fetch metrics from a Vertex AI experiment."""
    aiplatform.init(project=project_id, location=region)
    experiment = aiplatform.Experiment(experiment_name)
    experiment_df = experiment.get_data_frame()
    results = experiment_df[["experiment_name", "metric.accuracy"]]
    logging.info(results)
