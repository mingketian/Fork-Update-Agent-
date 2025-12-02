Fork-Update Agent
=================

This repository contains an implementation blueprint for the “Fork-update Agent” described in the Ricoh PROCRV. The goal is to automate consumption of upstream `idp_common` releases, validate them, deploy updates to the sandbox GenAI IDP accelerator, smoke-test, and notify stakeholders.

Repository layout
-----------------

```
.
├── docs/                         # Design notes, runbooks, diagrams
├── infrastructure/
│   └── cdk/                      # AWS CDK app that deploys automation workflow
├── source/
│   └── lambdas/                  # Lambda handlers that power the Step Functions workflow
├── state_machines/               # ASL (Amazon States Language) definitions
├── scripts/                      # Helper scripts (linting, packaging, etc.)
├── tests/                        # Unit and integration tests
└── README.md
```

High-level architecture
-----------------------

The solution is centred on an AWS Step Functions state machine orchestrating several Lambda functions:

1. **Detect Release** – polls the upstream GitHub repository for new tags/releases and compares them with the last successfully deployed version stored in SSM Parameter Store.
2. **Prepare Merge / Build** – triggers a CodeBuild project that merges upstream changes into the sandbox fork, runs tests, and produces deployable artifacts.
3. **Deploy to Sandbox** – updates CloudFormation stacks (or runs another CodeBuild job) to push the new artifact into the sandbox environment.
4. **Run Smoke Test** – invokes the existing IDP Step Functions workflow against a fixture document and inspects CloudWatch results.
5. **Report Status** – emits structured notifications (SNS, Slack, or email) summarizing success/failure and linking to logs.

EventBridge schedules periodic executions of the state machine, while failures are logged centrally and surfaced via notifications.

Next steps
----------

1. Install the AWS CDK Python dependencies under `infrastructure/cdk`.
2. Customize context values (account, region, repository names) in `infrastructure/cdk/app.py` or via `cdk.context.json`.
3. Deploy the stack: `cdk synth`, `cdk deploy`.
4. Populate any secrets/parameters referenced by the Lambdas (GitHub token, role ARNs, etc.).

See `docs/` for operational guides and the PROCRV digest.

Local development
-----------------

* Format/lint as desired (the repo currently relies on standard Python style tools).
* Run unit tests with `AWS_DEFAULT_REGION=us-east-1 python -m pytest`.
* Lambdas only depend on the Python standard library and `boto3` (already provided in AWS). When running tests locally install `pytest`/`boto3` via `pip install -r dev-requirements.txt`.
