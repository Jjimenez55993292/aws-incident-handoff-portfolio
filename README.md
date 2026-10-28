# Incident Handoff Tracker — AWS Architecture Portfolio

**Author:** Jacinto Jimenez · **Course:** CS 79C · **Region:** `us-west-2` (Oregon)  
**Status:** Starter implementation. Local unit tests pass; actual AWS deployment and evidence must be completed by the student.

A small, secure-by-default serverless API for recording fictional technical support incidents, retrieving a record by ID, and archiving an individual JSON snapshot. It demonstrates architecture, infrastructure as code (IaC), security trade-offs, performance, monitoring, cost, and operational cleanup. **Do not enter real employee, customer, ticket, or proprietary data.**

![AWS architecture showing API Gateway, Lambda, DynamoDB, S3, CloudWatch, and IAM](diagram/architecture.svg)

## AWS components and data flow

| Service | Role | Why this instead of the alternative |
| --- | --- | --- |
| Amazon API Gateway (HTTP API) | HTTPS entry point for REST-like routes; AWS IAM protects incident writes/reads | Less maintenance and typically simpler pricing than an always-running Application Load Balancer for a low-volume API |
| AWS Lambda (Python) | Validates and stores fictional incident records; serverless scaling | No EC2 server administration or hourly instance charges when idle |
| Amazon DynamoDB | Stores incidents by `incidentId`; pay-per-request mode | No RDS instance, database patching, or provisioning for sparse demo traffic |
| Amazon S3 | Private JSON archive for each created incident | Durable object storage is more appropriate than storing duplicate archive files on EC2 disk |
| Amazon CloudWatch | Logs executions and alarms on Lambda errors | Native AWS operational visibility instead of deploying a separate monitoring server |
| AWS IAM | Restricts Lambda to specific table, bucket path, and log group | Roles avoid embedding access keys in source control |
| AWS CloudFormation | Creates and deletes the entire integrated architecture | Native infrastructure-as-code tool, avoiding a local Terraform provider/plugin setup for this single-cloud lab |

**Routes:** `GET /health` (public, name visible); `POST /incidents` and `GET /incidents/{incidentId}` (IAM-signed requests required). API Gateway invokes Lambda, which writes to DynamoDB and archives a JSON record to private S3. CloudWatch records Lambda invocation logs and monitors Lambda error metrics. API Gateway applies a basic rate limit. All data must be fictional.

## Deploy from your Windows computer (no CloudShell required)

The template is **`template.yaml` at the repository root**. If you edit `src/handler.py`, run `python scripts/build_template.py` first to embed the updated source in `template.yaml`.

1. Open [AWS CloudFormation in Oregon](https://us-west-2.console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks). Select **Create stack** / **With new resources (standard)**.
2. Choose **Upload a template file**, upload `template.yaml`, and click Next.
3. Name the stack `incident-handoff-portfolio`. Keep `StudentName` as `Jacinto Jimenez` or set it to your own name.
4. Keep default rollback behavior. During Review and create, acknowledge **CAPABILITY_IAM** (the stack creates a Lambda execution role), then submit.
5. If deployment succeeds, open **Outputs**, copy **HealthURL**, and open it in a browser. It should return JSON with `"status": "ok"` and `"student": "Jacinto Jimenez"`.
6. Test **POST /incidents** using a signed request (`scripts/test_api.py`) or Lambda console test; verify that the *same incident ID* appears in the DynamoDB item and the S3 `incidents/<id>.json` object. Instructions: [docs/DEPLOY_GUIDE.md](docs/DEPLOY_GUIDE.md).
7. Capture AWS screenshots in `evidence/`, create an AWS Pricing Calculator estimate, then **empty the S3 bucket before deleting the stack**.

> **AWS costs:** A demo can cost very little at low usage, but it is not guaranteed free. The CloudWatch alarm, API requests, storage, and data transfer can incur charges. Use AWS Pricing Calculator for the exact scenario, enable a billing alert, and delete unused resources.

## Local tests (do not call AWS)

```powershell
py -m pip install boto3 botocore
py -m unittest discover -s tests -v
```

These tests exercise the local Lambda handler using mocked S3 and DynamoDB clients. Passing them is **not** evidence of a live deployment.

## Reproducible API testing

A public `GET /health` is suitable for a browser screenshot. All routes containing incident data are intentionally **AWS_IAM-protected**.

With a signed-in/credentialed AWS CLI or boto3 session that has `execute-api:Invoke` permission:

```powershell
py scripts/test_api.py --url "https://YOUR_API_ID.execute-api.us-west-2.amazonaws.com" --region us-west-2
```

Or open the Lambda console and run the POST/GET test events from [docs/DEPLOY_GUIDE.md](docs/DEPLOY_GUIDE.md). An unsigned POST intentionally returns `403`.

## Architecture concerns

- **Security:** AWS IAM on write/read routes, narrow Lambda role, HTTPS API, DynamoDB default encryption at rest, S3 SSE-S3 and full public-access block, seven-day log/archive retention. Public health route deliberately returns only project/status/author. There is no end-user identity system or multi-tenant separation: do not enter sensitive data.
- **Reliability:** Lambda, DynamoDB, API Gateway, and S3 are managed regional services. One AWS Region is a weakness; no tested restore procedure, DynamoDB PITR, or cross-Region replication is included. **Unverified design targets**: RTO within 4 hours and RPO within 1 hour if archives exist. These are goals, not measured service guarantees.
- **Performance:** Lambda and DynamoDB scale on demand. API Gateway stage throttle is 2 requests/second with burst 5 for a conservative demo limit. Potential bottlenecks include cold starts, S3 snapshot writing on every POST, and request throttling.
- **Cost:** Lambda, DynamoDB on-demand, HTTP API, and S3 charge mainly by usage. CloudWatch alarm may have a fixed monthly monitoring charge. Minimize with seven-day retention, 128 MB Lambda, low-rate demo workload, no EC2/NAT/ALB, and prompt cleanup. Complete the official calculator scenario before submission.

## Well-Architected self-review

| Pillar | Strength | Weakness / improvement |
| --- | --- | --- |
| Security | IAM auth for incident routes; scoped role; private encrypted storage | Add Cognito/JWT identity, WAF, audit reviews and explicit sensitive-data policy |
| Reliability | Regional managed services and S3 snapshot on successful POST | Non-transactional dual write; add reconciliation, PITR, restore drill, and Region DR |
| Cost Optimization | No always-on compute; on-demand resources | Add real usage budget alerts and verify calculator estimate/CloudWatch charge |

## Evidence and cleanup

`evidence/` is intentionally empty except for an evidence checklist, because live AWS screenshots must show actual account resources. Before publishing publicly, blur or crop AWS account IDs, personal IP addresses, and other unrelated details. Never commit AWS keys or configuration profiles.

**Cleanup sequence:** Capture evidence and calculator estimate → Empty S3 archive bucket **including objects** → Delete stack in CloudFormation → Verify `DELETE_COMPLETE` (or disappearance from active stacks) → Check S3, DynamoDB, Lambda, and CloudWatch for leftovers. Do not say cleanup is complete until verified.

## Repository layout

- `template.yaml` — deployable CloudFormation IaC; Python is inlined from `src/handler.py`.
- `src/handler.py` — Lambda handler.
- `diagram/architecture.svg`, `.png`, `.dot` — rendered architecture and editable Graphviz source.
- `tests/` — offline unit tests.
- `scripts/` — template builder and IAM-signed API test.
- `docs/` — Windows deployment instructions, report draft, screenshots checklist.
- `evidence/` — real AWS screenshots, to be added after deployment.

## AWS references

- [CloudFormation inline Lambda code](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-properties-lambda-function-code.html)
- [API Gateway HTTP API pricing](https://aws.amazon.com/api-gateway/pricing/)
- [Lambda pricing](https://aws.amazon.com/lambda/pricing/)
- [DynamoDB pricing](https://aws.amazon.com/dynamodb/pricing/)
- [AWS Pricing Calculator](https://aws.amazon.com/aws-cost-management/aws-pricing-calculator/)
