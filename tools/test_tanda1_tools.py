"""Pruebas aisladas: no leen claves reales ni acceden a la red."""
import contextlib
import hashlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, Mock
import zipfile

import credenciales_locales
import empower_api
import subir_pack_r2


class ToolsTest(unittest.TestCase):
    def test_empower_identifies_api_requests(self):
        with patch.object(empower_api, 'urlopen', return_value=io.BytesIO(b'{}')) as request:
            empower_api.Client('fake').request('GET', '')
        self.assertEqual(request.call_args.args[0].get_header('User-agent'), empower_api.USER_AGENT)

    def test_empower_identifies_signed_upload(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'file.yml'
            path.write_bytes(b'test')
            connection = Mock()
            connection.getresponse.return_value.status = 204
            with patch.object(empower_api.Client, 'request', return_value=b'{"attributes":{"url":"https://example.invalid/upload?signature=fake"}}'), \
                 patch.object(empower_api.http.client, 'HTTPSConnection', return_value=connection):
                empower_api.Client('fake').upload(path, '/')
            connection.putheader.assert_any_call('User-Agent', empower_api.USER_AGENT)

    def test_parser_limits_section_and_rejects_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'test.md'
            path.write_text('## Cloudflare R2 (pack)\n- **Access Key ID:** `fake`\n'
                            '## Otra\nClave: privada\n', encoding='utf-8')
            data = credenciales_locales.fields('Cloudflare R2 (pack)', path)
            self.assertEqual(data, {'Access Key ID': 'fake'})
            with self.assertRaisesRegex(ValueError, 'Falta completar'):
                credenciales_locales.require({}, 'Clave')

    def test_r2_dry_run_no_network_or_credentials(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'pack.zip'
            with zipfile.ZipFile(path, 'w') as output:
                output.writestr('pack.mcmeta', '{}')
            with patch.object(subir_pack_r2, 'fields', side_effect=AssertionError('Credenciales')), \
                 patch.object(subir_pack_r2, 'urlopen', side_effect=AssertionError('Red')):
                self.assertEqual(subir_pack_r2.upload(path, True), hashlib.sha1(path.read_bytes()).hexdigest())

    def test_r2_upload_checks_public_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'pack.zip'
            with zipfile.ZipFile(path, 'w') as output:
                output.writestr('pack.mcmeta', '{}')
            data = {'Endpoint S3': 'https://example.invalid', 'Access Key ID': 'fake', 'Secret Access Key': 'fake'}
            client = Mock()
            with patch.object(subir_pack_r2, 'fields', return_value=data), \
                 patch('boto3.client', return_value=client), \
                 patch.object(subir_pack_r2, 'urlopen', return_value=io.BytesIO(b'wrong')):
                with self.assertRaisesRegex(ValueError, 'no coincide'):
                    subir_pack_r2.upload(path)
            self.assertEqual(client.upload_file.call_args.args[1:3], ('astralrpg-pack', 'AstralRPG-Textures.zip'))

    def test_empower_default_does_not_connect(self):
        for action in (['list', '/'], ['read', '/server.properties'], ['command', 'tab reload'], ['restart']):
            with patch('sys.argv', ['empower_api.py'] + action), \
                 patch.object(empower_api, 'fields', side_effect=AssertionError('Claves')), \
                 patch.object(empower_api, 'urlopen', side_effect=AssertionError('Red')), \
                 contextlib.redirect_stdout(io.StringIO()) as output:
                empower_api.main()
                self.assertIn('DRY-RUN', output.getvalue())

    def test_library_errors_cannot_print_credentials(self):
        with patch('sys.argv', ['empower_api.py', '--yes', 'restart']), \
             patch.object(empower_api, 'fields', return_value={'Clave': 'FAKE_PRIVATE_VALUE'}), \
             patch.object(empower_api.Client, 'request', side_effect=ValueError('FAKE_PRIVATE_VALUE')), \
             contextlib.redirect_stderr(io.StringIO()) as output:
            with self.assertRaises(SystemExit):
                empower_api.main()
            self.assertNotIn('FAKE_PRIVATE_VALUE', output.getvalue())


if __name__ == '__main__':
    unittest.main()
