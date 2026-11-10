"""Sube el pack a R2 y verifica la descarga publica. --dry-run no usa red ni claves."""
import argparse
import hashlib
from pathlib import Path
from urllib.request import Request, urlopen

from credenciales_locales import fields, require, LocalError

PUBLIC_URL = 'https://pub-5e0d1c63a1554ba7b8e33b038e1a06fe.r2.dev/AstralRPG-Textures.zip'
DEFAULT_ZIP = Path(__file__).resolve().parents[1] / 'build/AstralRPG-Textures.zip'


def sha1_stream(stream):
    digest = hashlib.sha1()
    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
        digest.update(chunk)
    return digest.hexdigest()


def upload(path, dry_run=False):
    import zipfile
    if not zipfile.is_zipfile(path):
        raise LocalError('El archivo indicado no es un ZIP valido.')
    with path.open('rb') as stream:
        expected = sha1_stream(stream)
    if not dry_run:
        import boto3
        data = fields('Cloudflare R2 (pack)')
        client = boto3.client('s3', endpoint_url=require(data, 'Endpoint S3'),
                              aws_access_key_id=require(data, 'Access Key ID'),
                              aws_secret_access_key=require(data, 'Secret Access Key'), region_name='auto')
        client.upload_file(str(path), 'astralrpg-pack', 'AstralRPG-Textures.zip',
                           ExtraArgs={'ContentType': 'application/zip'})
        request = Request(PUBLIC_URL + '?sha1=' + expected, headers={'Cache-Control': 'no-cache'})
        with urlopen(request, timeout=120) as stream:
            actual = sha1_stream(stream)
        if actual != expected:
            raise LocalError('El SHA-1 publico no coincide; no actualizar el servidor.')
    return expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('zip', nargs='?', type=Path, default=DEFAULT_ZIP)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        digest = upload(args.zip, args.dry_run)
    except LocalError as error:
        parser.exit(1, str(error) + '\n')
    except Exception:
        parser.exit(1, 'Fallo la subida o verificacion de R2; detalles privados omitidos.\n')
    print(PUBLIC_URL)
    print(digest)


if __name__ == '__main__':
    main()
