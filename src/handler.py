"""Minimal demo API for fictional support handoff records.

GET /health is public. GET/POST /incidents use API Gateway AWS_IAM auth.
No real customer data should be submitted to this portfolio application.
"""
import base64
import json
import os
import uuid
from datetime import datetime, timezone

import boto3


def respond(status, payload):
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json", "cache-control": "no-store"},
        "body": json.dumps(payload),
    }


def handler(event, context):
    req = (event.get("requestContext") or {}).get("http") or {}
    method = req.get("method") or event.get("httpMethod") or ""
    path = event.get("rawPath") or event.get("path") or ""
    student = os.environ["STUDENT_NAME"]

    if method == "GET" and path == "/health":
        return respond(200, {
            "status": "ok", "project": "Incident Handoff Tracker",
            "student": student, "region": os.environ["AWS_REGION"],
        })

    if method == "POST" and path == "/incidents":
        try:
            raw = event.get("body") or "{}"
            if event.get("isBase64Encoded"):
                raw = base64.b64decode(raw).decode("utf-8")
            data = json.loads(raw)
            if not isinstance(data, dict):
                raise ValueError("Object expected")
        except (ValueError, TypeError, UnicodeDecodeError):
            return respond(400, {"error": "Invalid JSON object"})
        title = data.get("title")
        summary = data.get("summary", "")
        severity = data.get("severity", "LOW")
        if not (isinstance(title, str) and 1 <= len(title.strip()) <= 120
                and isinstance(summary, str) and len(summary) <= 500
                and severity in ("LOW", "MEDIUM", "HIGH")):
            return respond(400, {"error": "Provide title (1-120), summary (max 500), severity LOW/MEDIUM/HIGH"})

        incident_id = str(uuid.uuid4())
        item = {
            "incidentId": incident_id,
            "title": title.strip(),
            "summary": summary,
            "severity": severity,
            "createdAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "student": student,
        }
        table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])
        table.put_item(Item=item)
        boto3.client("s3").put_object(
            Bucket=os.environ["ARCHIVE_BUCKET"],
            Key=f"incidents/{incident_id}.json",
            Body=json.dumps(item).encode("utf-8"),
            ContentType="application/json",
            ServerSideEncryption="AES256",
        )
        print("Created demo record", incident_id)
        return respond(201, item)

    if method == "GET" and path.startswith("/incidents/"):
        incident_id = path.rsplit("/", 1)[-1]
        try:
            uuid.UUID(incident_id)
        except ValueError:
            return respond(400, {"error": "Invalid incident ID"})
        table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])
        record = table.get_item(Key={"incidentId": incident_id}).get("Item")
        return respond(200, record) if record else respond(404, {"error": "Not found"})

    return respond(404, {"error": "Route not found"})
