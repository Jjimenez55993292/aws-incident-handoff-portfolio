# Windows + AWS Console Deployment and Testing Guide

**Status: instructional steps; no claim the stack has been deployed.** Region: US West (Oregon), `us-west-2`.

## 1. Deploy through AWS console

1. In CloudFormation, choose **Create stack > With new resources (standard)**.
2. Choose **Upload a template file**, browse to `template.yaml`.
3. Stack name: `incident-handoff-portfolio`. StudentName: `Jacinto Jimenez`.
4. On Configure stack options, keep the defaults. On the Review screen, acknowledge the IAM capability because the template creates an execution role. Submit.
5. Look for `CREATE_COMPLETE`. In **Outputs**, copy `HealthURL`, `ApiBaseURL`, `IncidentTableName`, `ArchiveBucketName`, and `LambdaFunctionName`.

If creation fails, read the **Events** tab for the failing resource and error; do not invent successful screenshots. IAM permissions are required to create the Lambda role.

## 2. Show a working public API

Paste the **HealthURL** output into a browser, e.g. `https://<id>.execute-api.us-west-2.amazonaws.com/health`. It should return a JSON object like:

```json
{
  "status": "ok",
  "project": "Incident Handoff Tracker",
  "student": "Jacinto Jimenez",
  "region": "us-west-2"
}
```

This is the *expected* output. Capture the actual browser screen with the real URL/name. If it returns an error, check API Gateway routes, Lambda resource permission, and the Lambda CloudWatch log group.

## 3. Create a fictional incident: Lambda console route simulation

In the AWS Lambda console, open the function named by `LambdaFunctionName`. Click **Test > Create new event**. Paste:

```json
{
  "version": "2.0",
  "rawPath": "/incidents",
  "requestContext": {"http": {"method": "POST"}},
  "body": "{\"title\":\"Example inventory mismatch\",\"summary\":\"Fictional training incident, not actual company data\",\"severity\":\"LOW\"}"
}
```

Run the test. Expect outer Lambda invocation success and response body with `statusCode` **201** and a generated `incidentId`. This invokes the **real DynamoDB and S3** clients; unlike unit tests it can incur AWS charges. Take an actual execution screenshot.

Open DynamoDB console **Explore table items** and locate the generated `incidentId`. In the S3 console, open the `ArchiveBucketName` bucket and find `incidents/<same-id>.json`. Capture both. This demonstrates the two data stores are integrated with Lambda.

## 4. Retrieve the record

Create another Lambda test event, replacing `YOUR-INCIDENT-ID` with the actual returned value:

```json
{
  "version": "2.0",
  "rawPath": "/incidents/YOUR-INCIDENT-ID",
  "requestContext": {"http": {"method": "GET"}}
}
```

Expect `statusCode` **200** with the same title, severity, and student name. Copy only fabricated record values to the report. Do not use internal tickets, employees, IPs, or credentials.

## 5. Test the actual IAM-protected API routes (optional stronger evidence)

If you have AWS credentials from your normal desktop session with `execute-api:Invoke`, run the included IAM-signed `scripts/test_api.py` script with the `ApiBaseURL` output. The client sends a real API Gateway POST and GET, so it is stronger evidence than Lambda-only simulation. **Unsigned POST/GET requests are correctly rejected** by design.

## 6. CloudWatch evidence

Open CloudWatch **Log groups**, select `/aws/lambda/incident-handoff-portfolio-handler`, and find log streams for your test invocation. In CloudWatch **Alarms**, find the alarm created by the stack, showing it monitors `AWS/Lambda Errors`. A newly deployed alarm in OK state is expected; do not artificially force a production failure.

## 7. Official AWS Pricing Calculator estimate

Open [AWS Pricing Calculator](https://aws.amazon.com/aws-cost-management/aws-pricing-calculator/) and create a **us-west-2** estimate with these demo planning assumptions:

- API Gateway HTTP API: 1,000 requests/month.
- AWS Lambda: 1,000 invocations/month at 128 MB and 150 milliseconds average runtime.
- DynamoDB Standard on-demand: 300 new items/month, 700 reads/month, 2 MB stored.
- S3 Standard: 300 PUTs/month, 1 MB archived, no public GETs.
- CloudWatch: one standard alarm and 2 MB of logs/month.

Record the **calculator's actual monthly total and date** in the report, with a screenshot/export. Credits and Free Tier eligibility depend on your account. Don't quote an unverified dollar amount as an AWS calculator result.

## 8. Cleanup: important

1. Save ALL screenshots, the actual Pricing Calculator result, and the repo source.
2. Go to S3, open the archive bucket named in CloudFormation Outputs, and **empty all objects**. CloudFormation cannot delete a nonempty S3 bucket.
3. Go to CloudFormation → select `incident-handoff-portfolio` → **Delete** → confirm.
4. Check deletion results and whether the IAM role, DynamoDB table, Lambda, API Gateway, logs, and alarm are gone.
5. After **actual** deletion, update the report cleanup statement to say `DELETE_COMPLETE` verified, with date and console screenshot if available.

Do not delete resources from older Module 7 or 8 labs by accident. This project uses a new stack name and creates its own resources.
