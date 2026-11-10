"""Verificacion de R2 con respuestas falsas: ninguna prueba usa red o claves."""
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch, Mock
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
spec=importlib.util.spec_from_file_location('upload_pack_tanda2',ROOT/'tools/subir_pack_r2.py')
r2=importlib.util.module_from_spec(spec); spec.loader.exec_module(r2)

class R2Tests(unittest.TestCase):
    def test_dry_run_never_reads_credentials_or_network(self):
        with patch.object(r2,'fields',side_effect=AssertionError('credenciales')), patch.object(r2,'urlopen',side_effect=AssertionError('red')):
            self.assertEqual(len(r2.upload(ROOT/'build/AstralRPG-Textures.zip',True)),40)

    def test_retry_stale_bytes_and_verify_sha_with_user_agent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'pack.zip'
            with zipfile.ZipFile(path,'w') as z: z.writestr('pack.mcmeta','{}')
            payload=path.read_bytes(); client=Mock()
            fake=SimpleNamespace(client=Mock(return_value=client))
            with patch.dict(sys.modules,{'boto3':fake}),patch.object(r2,'fields',return_value={}),patch.object(r2,'require',return_value='test'),patch.object(r2,'sleep'),patch.object(r2,'urlopen',side_effect=[io.BytesIO(b'viejo'),io.BytesIO(payload)]) as url:
                self.assertEqual(r2.upload(path),r2.hashlib.sha1(payload).hexdigest())
                self.assertEqual(url.call_count,2); client.upload_file.assert_called_once()
                first,second=[call.args[0] for call in url.call_args_list]
                self.assertNotEqual(first.full_url,second.full_url)
                self.assertEqual(first.get_header('User-agent'),'AstralRPG-pack-verifier/1.0')
                self.assertIn('no-cache',first.get_header('Cache-control'))

    def test_different_public_sha_never_passes(self):
        client=Mock()
        with patch.dict(sys.modules,{'boto3':SimpleNamespace(client=Mock(return_value=client))}),patch.object(r2,'fields',return_value={}),patch.object(r2,'require',return_value='test'),patch.object(r2,'sleep'),patch.object(r2,'urlopen',side_effect=lambda *a,**k:io.BytesIO(b'incorrecto')):
            with self.assertRaises(r2.LocalError): r2.upload(ROOT/'build/AstralRPG-Textures.zip')
