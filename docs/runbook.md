Fork-Update Agent Runbook
=========================

## Prerequisites

* AWS sandbox credentials with permissions for Lambda, Step Functions, EventBridge, CodeBuild, CodePipeline, CloudFormation, SSM Parameter Store, SNS, and CloudWatch.
* GitHub token stored in SSM for accessing the upstream `idp_common` repository.
* Fixture document(s) in the sandbox S3 input bucket for smoke testing.

## Deploying the agent

1. `cd infrastructure/cdk`
2. Create/activate Python virtual environment.
3. `pip install -r requirements.txt`
4. Export `CDK_DEFAULT_ACCOUNT` and `CDK_DEFAULT_REGION` or set them in `cdk.context.json`.
5. `cdk bootstrap` (first time per account/region).
6. `cdk synth`
7. `cdk deploy ForkUpdateAgentStack`

## Parameters and secrets

* `/fork-update-agent/github/token` – GitHub personal access token (repo read scope).
* `/fork-update-agent/state/latest-version` – populated automatically after first successful run.
* `/fork-update-agent/notifications/slack` – optional webhook URL.

## Day-2 operations

* **Monitor** – CloudWatch dashboard + Step Functions execution history.
* **Manually trigger** – Start execution in Step Functions console or run `aws stepfunctions start-execution`.
* **Force rollback** – Update the `desired_version` parameter or redeploy stack with previous artifact.
* **Disable automation** – Remove/suspend EventBridge rule `ForkUpdateAgentSchedule`.

## Failure handling

* **Detection failure** – Check GitHub token validity and repository permissions.
* **Merge/test failure** – Inspect CodeBuild logs (link provided in notification payload).
* **Deploy failure** – Review CloudFormation stack events; stack rolls back automatically.
* **Smoke test failure** – Open Step Functions execution for the IDP workflow and view CloudWatch logs for Lambda tasks within the accelerator.
* **Notification failure** – Verify SNS topic subscriptions or Slack webhook parameter.

## Extensibility tips

* Additional validations can be inserted into the Step Functions definition.
* Multi-branch support can be achieved by passing `branch` in the execution input and parameterizing SSM keys/evaluations.
* Replace GitHub polling with upstream webhooks routed through API Gateway + EventBridge if instant updates are needed.
