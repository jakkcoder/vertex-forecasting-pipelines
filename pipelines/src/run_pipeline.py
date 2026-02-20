import argparse
import yaml

from google.cloud import aiplatform
from kfp import dsl, compiler
from google_cloud_pipeline_components.v1.custom_job import CustomTrainingJobOp


@dsl.pipeline(name="vertex-customjob-pipeline")
def hello_pipeline(project_id: str, region: str):
    CustomTrainingJobOp(
        project=project_id,
        location=region,
        display_name="hello-customjob",
        worker_pool_specs=[
            {
                "machine_spec": {
                    "machine_type": "e2-standard-4",  # Smallest supported; default for pipelines; cost-effective for free tier
                },
                "replica_count": 1,
                "container_spec": {
                    "image_uri": "us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-17.py310:latest",
                    "command": ["bash", "-lc"],
                    "args": ["echo Hello from CustomTrainingJobOp; sleep 5"],
                },
            }
        ],
    )


def load_config(env: str) -> dict:
    with open(f"configs/{env}.yaml", "r") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True, choices=["dev", "stage", "prod"])
    args = parser.parse_args()

    cfg = load_config(args.env)
    project_id = cfg["project_id"]
    region = cfg["region"]
    pipeline_root = cfg["pipeline_root"]
    service_account = cfg["service_account"]

    compiler.Compiler().compile(
        pipeline_func=hello_pipeline,
        package_path="pipelines/src/compiled_pipeline.json",
    )

    aiplatform.init(project=project_id, location=region)
    job = aiplatform.PipelineJob(
        display_name=f"customjob-{args.env}",
        template_path="pipelines/src/compiled_pipeline.json",
        pipeline_root=pipeline_root,
        parameter_values={"project_id": project_id, "region": region},
    )
    job.run(service_account=service_account)


if __name__ == "__main__":
    main()