from source.lambdas.report_status.handler import _build_message


def test_build_message_success():
    event = {
        "status": "SUCCESS",
        "detail": {
            "detect": {"upstream_version": "v1.2.3"},
            "merge": {"upstream_version": "v1.2.3", "build_id": "build-123"},
            "deploy": {"upstream_version": "v1.2.3", "execution_id": "deploy-1"},
            "smoke": {"smoke_execution_arn": "arn:aws:states:..."},
        },
    }
    msg = _build_message(event)
    assert msg["status"] == "SUCCESS"
    assert msg["upstream_version"] == "v1.2.3"
    assert msg["build_id"] == "build-123"
    assert msg["smoke_execution"] == "arn:aws:states:..."
