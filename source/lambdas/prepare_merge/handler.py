import logging
import os
import time
from typing import Any

import boto3


LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

CODEBUILD = boto3.client("codebuild")


def _wait_for_completion(build_id: str, poll_seconds: int = 10) -> dict[str, Any]:
    """Poll CodeBuild until the build finishes."""
    terminal_statuses = {"SUCCEEDED", "FAILED", "FAULT", "STOPPED", "TIMED_OUT"}
    while True:
        response = CODEBUILD.batch_get_builds(ids=[build_id])
        builds = response.get("builds", [])
        if not builds:
            raise RuntimeError(f"Build {build_id} not found.")
        build = builds[0]
        status = build["buildStatus"]
        LOGGER.info("Build %s status: %s", build_id, status)
        if status in terminal_statuses:
            return build
        time.sleep(poll_seconds)


def lambda_handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    LOGGER.info("Starting merge/test CodeBuild for event: %s", event)
    project = os.environ["CODEBUILD_PROJECT_MERGE"]
    upstream_version = event["upstream_version"]

    env_overrides = [
        {"name": "TARGET_VERSION", "value": upstream_version, "type": "PLAINTEXT"},
        {"name": "RELEASE_URL", "value": event.get("release_url", ""), "type": "PLAINTEXT"},
    ]

    response = CODEBUILD.start_build(projectName=project, environmentVariablesOverride=env_overrides)
    build_id = response["build"]["id"]

    LOGGER.info("Triggered CodeBuild %s for project %s", build_id, project)

    build = _wait_for_completion(build_id)

    status = build["buildStatus"]
    if status != "SUCCEEDED":
        exception = RuntimeError(f"Merge/Build failed with status {status}")
        exception.build = build  # type: ignore[attr-defined]
        raise exception

    artifact_location = ""
    if build.get("artifacts"):
        artifact_location = build["artifacts"].get("location", "")

    logs = build.get("logs", {})

    return {
        "upstream_version": upstream_version,
        "artifact_id": artifact_location,
        "build_id": build_id,
        "log_group": logs.get("groupName"),
        "log_stream": logs.get("streamName"),
    }
