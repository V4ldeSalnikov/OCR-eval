"""Guard the boundary between private runs and public prediction reports."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from export_all_results import check_public, write


class PublicResultsTests(unittest.TestCase):
    def test_nested_private_fields_and_paths_are_rejected(self):
        for value in ({'settings': {'api_key': 'private'}},
                      {'cases': [{'metadata': {'source_image_path': 'private'}}]},
                      {'prompt': 'Read C:\\Users\\someone\\private.png'},
                      {'metadata': {'path': r'\\server\private\image.png'}}):
            with self.assertRaises(AssertionError):
                check_public(value)

    def test_public_urls_and_verbatim_transcriptions_are_preserved(self):
        check_public({'source_url': 'https://huggingface.co/datasets/example',
                      'prediction': 'A printed path: C:\\Documents\\example',
                      'inference_settings': None})

    def test_credentials_block_write_without_leaking_value(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'report.json'
            secret = 'mstrl' + '_' + 'A' * 40
            with self.assertRaises(AssertionError) as error:
                write(path, {'cases': [{'prediction': secret}]})
            self.assertNotIn(secret, str(error.exception))
            self.assertFalse(path.exists())


if __name__ == '__main__':
    unittest.main()
