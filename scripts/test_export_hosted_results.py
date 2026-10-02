from pathlib import Path
import tempfile
import unittest
from export_hosted_results import settings, write


class PublicExportTests(unittest.TestCase):
    def test_private_fields_are_not_exported(self):
        source = {'model_id': 'example', 'api_key': 'private', 'headers': {'Authorization': 'private'},
                  'per_task_settings': {'line-recognition': {'model': 'example', 'max_output_tokens': 8192,
                                        'api_key': 'private', 'base_url': 'http://private'}}}
        actual = settings(source)
        self.assertEqual(actual, {'model_id': 'example', 'per_task_settings': {
            'line-recognition': {'model': 'example', 'max_output_tokens': 8192}}})

    def test_credential_like_values_block_export_without_writing_them(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'report.json'
            for prefix in ('sk-' + 'proj-', 'mstrl' + '_'):
                with self.assertRaises(AssertionError):
                    write(target, {'prediction': prefix + 'A' * 40})
                self.assertFalse(target.exists())


if __name__ == '__main__':
    unittest.main()
