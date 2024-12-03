import logging

import typer
from kfp.dsl import Metrics, Output, component, pipeline

from pipelines.utils import job_constants, job_params, run_pipeline_on_vertex_or_locally

logging.basicConfig(level=logging.INFO)


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

    def main(
        local: bool = typer.Option(
            True, help="Run the pipeline locally instead of on Vertex AI"
        ),
    ):
        run_pipeline_on_vertex_or_locally(
            pipeline_function=demo_pipeline,
            params=job_params,
            constants=job_constants,
            local=local,
        )

    typer.run(main)
