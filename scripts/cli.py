import logging
from subprocess import CalledProcessError, run

import typer

from pipelines.demo import job_constants
from scripts.helpers import get_adc, require_valid_gcp_adc


@require_valid_gcp_adc
def build_container(
    project_id: str = job_constants.GCP_PROJECT,
    user: str = job_constants.USER,
    repo_name: str = job_constants.REPO_NAME,
    local: bool = True,
):
    """Build a Kubeflow container 📦"""
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
            "--substitutions",
            f"_PROJECT_ID={project_id},REPO_NAME={repo_name},_USER={user}",
            "--service-account",
            f"projects/{project_id}/serviceAccounts/pipeline-runner@{project_id}.iam.gserviceaccount.com",
        ]

    try:
        run(build_cmd, check=True)

    except CalledProcessError:
        logging.error("Build failed")
        raise typer.Exit()