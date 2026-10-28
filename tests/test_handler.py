"""Offline unit tests; do not require AWS credentials or AWS resources."""
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import handler as app


class HandlerTests(unittest.TestCase):
    def setUp(self):
        self.environ = patch.dict(os.environ, {
            'STUDENT_NAME': 'Jacinto Jimenez',
            'TABLE_NAME': 'test-table',
            'ARCHIVE_BUCKET': 'test-archive',
            'AWS_REGION': 'us-west-2',
        })
        self.environ.start()
        self.addCleanup(self.environ.stop)

    @staticmethod
    def invoke(method, path, body=None):
        event = {'version': '2.0', 'rawPath': path,
                 'requestContext': {'http': {'method': method}}}
        if body is not None:
            event['body'] = json.dumps(body)
        result = app.handler(event, None)
        return result['statusCode'], json.loads(result['body'])

    def test_public_health_contains_student(self):
        status, payload = self.invoke('GET', '/health')
        self.assertEqual(status, 200)
        self.assertEqual(payload['student'], 'Jacinto Jimenez')

    def test_rejects_invalid_post(self):
        status, payload = self.invoke('POST', '/incidents', {'title': '', 'severity': 'TOP'})
        self.assertEqual(status, 400)
        self.assertIn('error', payload)

    @patch('handler.boto3.client')
    @patch('handler.boto3.resource')
    def test_post_archives_and_persists(self, resource, client):
        fake_table = MagicMock()
        resource.return_value.Table.return_value = fake_table
        fake_s3 = MagicMock()
        client.return_value = fake_s3
        status, payload = self.invoke('POST', '/incidents', {
            'title': 'Example blocked channel', 'summary': 'Fictional test record', 'severity': 'LOW',
        })
        self.assertEqual(status, 201)
        self.assertEqual(payload['student'], 'Jacinto Jimenez')
        fake_table.put_item.assert_called_once()
        kwargs = fake_s3.put_object.call_args.kwargs
        self.assertEqual(kwargs['Bucket'], 'test-archive')
        self.assertEqual(kwargs['ServerSideEncryption'], 'AES256')
        self.assertIn(payload['incidentId'], kwargs['Key'])

    @patch('handler.boto3.resource')
    def test_missing_record(self, resource):
        resource.return_value.Table.return_value.get_item.return_value = {}
        status, payload = self.invoke('GET', '/incidents/123e4567-e89b-12d3-a456-426614174000')
        self.assertEqual(status, 404)


if __name__ == '__main__':
    unittest.main()
