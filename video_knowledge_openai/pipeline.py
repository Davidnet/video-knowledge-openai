"""
Module that contains the pipeline steps that extracts transcriptions and context for a LLM.
Author: David Cardozo <david.cardozo@me.com>
"""
from kfp import dsl, compiler, components
from kfp.dsl import Artifact, PipelineTask

# pylint: disable=import-outside-toplevel

process_videos = components.load_component_from_file(
    "components/process_videos/component_metadata/process_videos.yaml"
)

create_knowledge_db = components.load_component_from_file(
    "components/create_knowledge_db/component_metadata/create_knowledge_db.yaml"
)


@dsl.component
def get_date_string() -> str:
    """
    Component that returns the current UTC date and time.
    """
    from datetime import datetime

    current_utc_datetime = datetime.utcnow()
    utc_date_string = current_utc_datetime.strftime("%Y-%m-%d %H:%M")
    return utc_date_string


@dsl.pipeline
def video_processing_pipeline(
    video_urls: str = "gs://mlops-explorations-vertex-pipelines-us-central1/urls.txt",  # pylint: disable=line-too-long
    window: int = 12,
    stride: int = 4,
):
    """
    Pipeline that extracts the transcriptions and context for a LLM.
    :param video_urls: The urls of the videos to process.
    """
    openai_key = "OPENAI_API_KEY"
    pinecone_key = "PINECONE_API_KEY"
    date_task: PipelineTask = get_date_string()
    import_task = dsl.importer(
        artifact_uri=video_urls,
        artifact_class=Artifact,
        reimport=False,
        metadata={"date": date_task.output},
    )
    transcribe_task = process_videos(video_urls=import_task.output)
    transcribe_task.set_display_name("Transcribe videos").set_retry(
        num_retries=4, backoff_duration="30s", backoff_factor="1"
    ).set_cpu_limit("4").set_memory_limit("32G").set_env_variable(
        "OPENAI_API_KEY", openai_key
    )

    embed_task = create_knowledge_db(
        transcriptions=transcribe_task.outputs["transcriptions"],
        window=window,
        stride=stride,
    )
    embed_task.set_display_name("Pinecone creator").set_cpu_limit("4").set_memory_limit(
        "32G"
    ).set_retry(
        num_retries=4, backoff_duration="60s", backoff_factor="1"
    ).set_env_variable(
        "OPENAI_API_KEY", openai_key
    ).set_env_variable(
        "PINECONE_API_KEY", pinecone_key
    )


if __name__ == "__main__":
    compiler.Compiler().compile(video_processing_pipeline, "pipeline.yaml")
