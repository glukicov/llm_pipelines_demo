import logging
from functools import wraps
from pathlib import Path
from subprocess import CalledProcessError
from google.auth.exceptions import DefaultCredentialsError

import typer
from google.auth import default
from google.auth.transport.requests import Request

GCP_ADC_ERROR_MSG: str = "Your GCP credentials are not valid. Re-authenticate with: gcloud auth login --update-adc"


def get_adc() -> str | None:
    """Get the user's Application Default Credentials (ADC)."""
    try:
        file_path = Path.expanduser(
            Path("~/.config/gcloud/application_default_credentials.json")
        )
        with Path.open(file_path) as file:
            adc = file.read()

    except CalledProcessError as e:
        logging.error(f"An error occurred while fetching the ADC: {e}")
        return None

    else:
        return adc


def check_if_adc_valid() -> bool | None:
    """Check if the user's ADC are valid, refresh if necessary, and return them."""
    try:
        credentials, project = default()

        if credentials.valid:
            return True

        elif credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())

            except Exception:
                logging.error(GCP_ADC_ERROR_MSG)
                raise typer.Exit()

            else:
                return True

        else:
            logging.error(GCP_ADC_ERROR_MSG)
            raise typer.Exit()

    except DefaultCredentialsError:
        logging.error(GCP_ADC_ERROR_MSG)
        raise typer.Exit()


def require_valid_gcp_adc(func):
    """Decorator to check if the user's GCP ADC are valid."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if check_if_adc_valid():
            return func(*args, **kwargs)
        else:
            return None

    return wrapper
