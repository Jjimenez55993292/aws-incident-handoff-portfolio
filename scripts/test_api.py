"""Run signed POST /incidents and GET /incidents/{id} from a configured Windows PC.

Prereqs: pip install boto3 botocore; AWS login/SSO credentials with execute-api:Invoke.
Usage: python scripts/test_api.py --url https://APIID.execute-api.us-west-2.amazonaws.com
"""
import argparse
import json
import urllib.error
import urllib.request

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest


def signed_request(method, url, region, payload=None):
    session = boto3.Session(region_name=region)
    credentials = session.get_credentials()
    if credentials is None:
        raise RuntimeError('AWS credentials not found. Configure AWS login or use Lambda console tests.')
    body = json.dumps(payload).encode('utf-8') if payload is not None else None
    headers = {'Content-Type': 'application/json'}
    aws_request = AWSRequest(method=method, url=url, data=body, headers=headers)
    SigV4Auth(credentials.get_frozen_credentials(), 'execute-api', region).add_auth(aws_request)
    headers = dict(aws_request.headers.items())
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.status, json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as error:
        raise RuntimeError(f'HTTP {error.code}: {error.read().decode("utf-8", "replace")}') from error


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', required=True, help='CloudFormation ApiBaseURL output')
    parser.add_argument('--region', default='us-west-2')
    args = parser.parse_args()
    base = args.url.rstrip('/')
    code, created = signed_request('POST', base + '/incidents', args.region, {
        'title': 'Demo pick-to-light interruption',
        'summary': 'Fictional incident for course portfolio validation',
        'severity': 'LOW',
    })
    print('POST /incidents', code, json.dumps(created, indent=2))
    code, read = signed_request('GET', base + '/incidents/' + created['incidentId'], args.region)
    print('GET /incidents/{id}', code, json.dumps(read, indent=2))
    print('Check DynamoDB for the same incidentId and S3 for incidents/<id>.json')


if __name__ == '__main__':
    main()
