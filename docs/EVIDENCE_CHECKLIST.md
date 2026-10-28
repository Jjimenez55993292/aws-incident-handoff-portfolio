# Evidence checklist (real AWS output only)

Add these PNGs to the `evidence/` folder after verifying each step in **us-west-2**:

- [ ] `01-cloudformation-create-complete.png` — CloudFormation stack and status `CREATE_COMPLETE`.
- [ ] `02-public-health-url.png` — browser with real API URL and `student` visible in JSON.
- [ ] `03-lambda-create-201.png` — real Lambda test showing `statusCode: 201` and new ID.
- [ ] `04-dynamodb-item.png` — DynamoDB item with matching `incidentId`.
- [ ] `05-s3-archive.png` — private S3 object `incidents/<same-id>.json`.
- [ ] `06-cloudwatch-alarm.png` — real CloudWatch alarm monitoring Lambda Errors.
- [ ] `07-pricing-calculator.png` — actual AWS Pricing Calculator assumptions and total.
- [ ] `08-cleanup.png` — actual stack DELETE_COMPLETE, if captured.

**Never use a configuration form as proof of successful creation.** Redact AWS account numbers, unrelated IP addresses, user information, and any credentials before publishing screenshots in a PUBLIC GitHub repository.
