import logging
import os
import time
from typing import Any

import boto3


LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

CODEBUILD = boto3.client("codebuild")


def _wait_for_completion(build_id: str, poll_seconds: int = 10) -> dict[str, Any]:
    terminal_statuses = {"SUCCEEDED", "FAILED", "FAULT", "STOPPED", "TIMED_OUT"}
    while True:
        response = CODEBUILD.batch_get_builds(ids=[build_id])
        builds = response.get("builds", [])
        if not builds:
            raise RuntimeError(f"Build {build_id} not found.")
        build = builds[0]
        status = build["buildStatus"]
        LOGGER.info("Deploy build %s status: %s", build_id, status)
        if status in terminal_statuses:
            return build
        time.sleep(poll_seconds)


def lambda_handler(event: dict[str, Any], _context: Any) -> dict[str, Any]:
    LOGGER.info("Deploy request: %s", event)
    project = os.environ["CODEBUILD_PROJECT_DEPLOY"]
    artifact_id = event.get("artifact_id", "")
    upstream_version = event.get("upstream_version")

    if not upstream_version:
        raise ValueError("upstream_version is required")

    env_overrides = [
        {"name": "TARGET_VERSION", "value": upstream_version, "type": "PLAINTEXT"},
        {"name": "ARTIFACT_ID", "value": artifact_id or "", "type": "PLAINTEXT"},
    ]

    response = CODEBUILD.start_build(projectName=project, environmentVariablesOverride=env_overrides)
    build_id = response["build"]["id"]
    LOGGER.info("Triggering deploy CodeBuild %s", build_id)

    build = _wait_for_completion(build_id)
    status = build["buildStatus"]
    if status != "SUCCEEDED":
        error = RuntimeError(f"Deployment build failed with status {status}")
        error.build = build  # type: ignore[attr-defined]
        raise error

    logs = build.get("logs", {})

    return {
        "upstream_version": upstream_version,
        "artifact_id": artifact_id,
        "execution_id": build_id,
        "log_group": logs.get("groupName"),
        "log_stream": logs.get("streamName"),
    }
