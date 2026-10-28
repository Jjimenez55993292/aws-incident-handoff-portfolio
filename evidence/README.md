# Verified AWS screenshots — October 27–28, 2026

All images in this folder are **real user-captured AWS console, application, or AWS Pricing Calculator screenshots** from the `us-west-2` project. Browser chrome and account-identifying navigation were cropped where appropriate; no AWS results were fabricated or altered.

| File | Evidence / result |
|---|---|
| `01-cloudformation-create-complete.png` | `incident-handoff-portfolio` reached `CREATE_COMPLETE`. |
| `02-public-health-url.png` | Public `/health` returned `status: ok`, project, student, and `us-west-2`. |
| `03-lambda-create-201.png` | Lambda test simulated POST and returned `statusCode: 201` with UUID. |
| `04-dynamodb-item.png` | DynamoDB Scan found the fictional incident. |
| `05-s3-archive.png` | S3 `incidents/` contains `<incidentId>.json` with matching UUID. |
| `06-lambda-get-200.png` | Lambda test simulated GET and returned `statusCode: 200` with same incident. |
| `07-cloudwatch-logs.png` | Real START/END/REPORT metrics for the GET invocation. |
| `08-cloudwatch-alarm.png` | Lambda error alarm present in OK state, no notification actions configured. |
| `09-pricing-calculator.png` | Five-service projected cost: $0.46/month, $5.52/year. |

**Scope notes:** The POST/GET incident calls shown here were executed as **Lambda console test events**, not as IAM-signed client requests through API Gateway. The public health endpoint *was* executed through API Gateway. A direct SigV4 client test is available in `scripts/test_api.py`, but the screenshots do not document its execution. Cleanup has not been confirmed in these screenshots.
