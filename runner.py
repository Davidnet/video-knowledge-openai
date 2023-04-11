import os
from google.cloud import aiplatform
from google.oauth2.credentials import Credentials
import subprocess


def run_command(command):
    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True
    )
    return result.stdout


authentication_token = run_command("gcloud auth print-access-token").rstrip()


creds = Credentials(authentication_token)


PROJECT = "mlops-explorations"

aiplatform.init(project=PROJECT, credentials=creds)


job = aiplatform.PipelineJob(
    display_name="kubeflow-tribal-pipeline",
    template_path="pipeline.yaml",
    # pipeline_root=PIPELINE_ROOT,
    credentials=creds,
    enable_caching=True,
    project=PROJECT,
    location="us-central1",
)

job.run()
