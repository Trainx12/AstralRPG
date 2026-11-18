"""Descarga oficial: solo mocks, sin credenciales ni red."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import empower_api


class DownloadTest(unittest.TestCase):
    def test_binary_download_keeps_exact_bytes(self):
        blob=bytes(range(256))*100
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'region/r.0.0.mca'
            with patch.object(empower_api.Client,'request',return_value=b'{"attributes":{"url":"https://example.invalid/file?token=fake"}}') as api, \
                 patch.object(empower_api,'urlopen',return_value=io.BytesIO(blob)) as download:
                empower_api.Client('fake').download('/world/region/r.0.0.mca',target)
            self.assertEqual(target.read_bytes(),blob)
            self.assertEqual(api.call_args.args[0],'GET')
            self.assertIn('/files/download?file=',api.call_args.args[1])
            self.assertIsNone(download.call_args.args[0].get_header('Authorization'))

    def test_existing_backup_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'before.mca';target.write_bytes(b'original')
            with patch.object(empower_api.Client,'request',return_value=b'{"attributes":{"url":"https://example.invalid/file"}}'), \
                 patch.object(empower_api,'urlopen',return_value=io.BytesIO(b'changed')):
                with self.assertRaises(FileExistsError):empower_api.Client('fake').download('/map',target)
            self.assertEqual(target.read_bytes(),b'original')

    def test_insecure_signed_url_is_rejected(self):
        with patch.object(empower_api.Client,'request',return_value=b'{"attributes":{"url":"http://example.invalid/file"}}'), \
             patch.object(empower_api,'urlopen',side_effect=AssertionError('Red')):
            with self.assertRaises(empower_api.LocalError):
                empower_api.Client('fake').download('/map',Path('unused'))

    def test_failed_stream_does_not_leave_a_partial_backup(self):
        class Broken(io.BytesIO):
            def read(self,*args):raise OSError('connection lost')
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'partial.mca'
            with patch.object(empower_api.Client,'request',return_value=b'{"attributes":{"url":"https://example.invalid/file"}}'), \
                 patch.object(empower_api,'urlopen',return_value=Broken(b'partial')):
                with self.assertRaises(OSError):empower_api.Client('fake').download('/map',target)
            self.assertFalse(target.exists())

    def test_dry_run_does_not_read_credentials_or_network(self):
        with patch('sys.argv',['empower_api.py','--dry-run','download','/map','.local/download.mca']), \
             patch.object(empower_api,'fields',side_effect=AssertionError('Claves')), \
             patch.object(empower_api,'urlopen',side_effect=AssertionError('Red')), \
             contextlib.redirect_stdout(io.StringIO()):
            empower_api.main()


if __name__=='__main__':unittest.main()
