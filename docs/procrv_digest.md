PROCRV Digest
=============

The Ricoh PROCRV (Pre-Requirements Operating Concept Rationale and Validation) describes the Fork-update Agent for the AWS GenAI IDP accelerator. Key excerpts distilled here guide implementation.

Scope
-----

* **Project**: Automate fork updates for `idp_common` within bpodev/sandbox.
* **Sponsor**: Jeremy Jacobson.
* **Stakeholders**: Design, Product, IDP Engineering, Support, Demo teams.
* **Purpose**: Deliver predictable updates, reduce manual maintenance, maintain auditability.

Current pain points
-------------------

* Manual Git merges and validation slow demo readiness.
* Failed updates can leave the sandbox unusable without clear visibility.
* Lack of continuous monitoring/logging for the update loop.
* Need to respect least-privilege, sandbox-only operations.

Change priorities
-----------------

1. Automated detection of upstream releases.
2. Merge/test/deploy workflow with safe rollback.
3. Smoke test orchestration and log inspection.
4. Transparent reporting with links to artifacts/logs.
5. Extensible design for future enhancements (multi-branch, chaos tests, etc.).

Target concept
--------------

* Step Functions orchestrates discrete Lambda-driven stages.
* CodeBuild performs merges/tests to keep Git credentials out of Lambdas.
* Deployments update sandbox CloudFormation stacks (root + pattern).
* Smoke tests run the accelerator Step Function on fixture docs stored in S3.
* Failures trigger rollback (redeploy previous artifact), notifications, and diagnostics.
* Operational data (current version, build metadata) stored in SSM Parameter Store or DynamoDB for traceability.

Constraints
-----------

* Sandbox account only; no prod touch.
* Least privilege IAM; reuse existing CI/CD tooling where possible.
* Conservative failure posture—abort and rollback on any error.
* Logging/monitoring align with internal standards; hand-off ready.

Success measures
----------------

* Sandbox consistently mirrors latest vetted upstream release.
* Stakeholders receive timely reports with pass/fail context.
* MTTR for failed updates reduced via automated rollback and diagnostics.
* Onboarding new contributors is straightforward via docs and IaC.
