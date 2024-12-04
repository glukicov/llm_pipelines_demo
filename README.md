# LLM pipelines demo

Demo of local and remote pipelines for calling and evaluating LLMs using Kubeflow and Vertex AI.

<img src="docs/imgs/demo.png" width=500cm>

👉 This repo is a companion to this blog post [medium.com/p/1b688dcebee5/edit](medium.com/p/1b688dcebee5/edit)

# Setup

Install `uv`: https://docs.astral.sh/uv/getting-started/installation/

Download Python `3.12.7`:
```shell
uv python install 3.12.7
```
update the project's environment
```shell
uv sync
```
and activate the virtual environment
```shell
source .venv/bin/activate
```

## Google Cloud ☁️
If you haven't already, [create a Google Cloud account and project](https://console.cloud.google.com/getting-started),
then [install the Google Cloud SDK](https://cloud.google.com/sdk/docs/install) `gcloud`, and authenticate with GCP:
```shell
gcloud auth login --update-adc
```

- Navigate to, and click to enable any necessary APIs, in [Vertex AI Pipelines](https://console.cloud.google.com/vertex-ai/pipelines).

- Then in the IAM, [create a new service account (SA)](https://console.cloud.google.com/iam-admin/serviceaccounts) (e.g. `demo-sa`) with the following roles:
```
Artifact Registry Reader
Cloud Build Editor
Storage Object User
Vertex AI User
````

- Create a new Docker repository `demo-repo` in `us-central1` region in the [Artifact Registry](https://console.cloud.google.com/artifacts).

- Finally,  add your project ID (e.g. `plasma-set-442915-a1`), repository name and SA name to `pipelines/config.cfg`:
```
[job_constants]
gcp_project = plasma-set-442915-a1
sa_name = demo-sa
repo_name = demo-repo
```



# Local pipeline with Kubeflow
Build a local container with
```shell
build-local
```
and trigger a local pipeline with
```shell
python pipelines/demo.py --local
```

The pipeline outputs are saved in `./local_outputs/`.

# Remote pipeline on Vertex AI


## Experiment tracking

# Extending your pipeline
The next steps are to extend your pipeline with:
- BQ:
- LLM call example from OIA
- Accuracy evaluation
