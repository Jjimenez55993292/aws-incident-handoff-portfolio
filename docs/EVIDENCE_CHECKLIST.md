# Final portfolio evidence and outstanding checks

Verified from real October 27–28, 2026 screenshots in `evidence/`:

- [x] CloudFormation `incident-handoff-portfolio`: `CREATE_COMPLETE`.
- [x] Public API Gateway `/health`: `status = ok`, name Jacinto Jimenez.
- [x] Lambda POST **console-simulated** request: `statusCode = 201`.
- [x] DynamoDB item matching incident UUID.
- [x] S3 `incidents/<uuid>.json` archive matching incident UUID.
- [x] Lambda GET **console-simulated** request: `statusCode = 200`.
- [x] CloudWatch logs: real START, END, REPORT entries.
- [x] CloudWatch error alarm: OK state (no notifications configured).
- [x] AWS Pricing Calculator: $0.46/month, $5.52/year, five services.
- [x] Public GitHub repository created; README renders architecture diagram (user screenshot).

**Still pending, do not claim complete until confirmed:**

- [ ] Optional but recommended IAM-signed API Gateway POST+GET using `scripts/test_api.py` with authorized AWS credentials and `execute-api:Invoke` permission.
- [ ] Align Lambda pricing calculator architecture with CloudFormation `arm64` (calculator screenshot uses `x86`). Capture corrected price summary if changed.
- [ ] Empty the project S3 bucket and delete CloudFormation stack. Verify `DELETE_COMPLETE` or absence of project resources. Capture evidence screenshot if possible.
- [ ] If older lab stack `cs79c-stack` is still running, clean it up independently after saving the Module 8 evidence.
- [ ] Update the report's cleanup wording after AWS confirms deletion.
- [ ] Check the repository and final PDF are publicly readable; submit both repository URL and PDF to Canvas.

Only upload **fictional** test data. Before public push, inspect screenshots/files for credentials, sensitive content, account numbers or unrelated IDs, and redact if appropriate.
