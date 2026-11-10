"""Cliente Pterodactyl. Simula por defecto; --yes ejecuta la accion indicada."""
import argparse
import http.client
import json
from pathlib import Path, PurePosixPath
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen
import uuid

from credenciales_locales import fields, require, LocalError

BASE = 'https://gp.empowerservers.com/api/client/servers/44d1ad66'


class Client:
    def __init__(self, key):
        self.key = key

    def request(self, method, route, data=None, content_type='application/json'):
        request = Request(BASE + route, data=data, method=method, headers={
            'Authorization': 'Bearer ' + self.key,
            'Accept': 'application/vnd.pterodactyl.v1+json', 'Content-Type': content_type})
        with urlopen(request, timeout=120) as response:
            return response.read()

    def upload(self, local, directory):
        signed = json.loads(self.request('GET', '/files/upload'))['attributes']['url']
        url = urlsplit(signed)
        if url.scheme != 'https':
            raise LocalError('El panel devolvio una URL de subida insegura.')
        query = url.query + ('&' if url.query else '') + urlencode({'directory': directory})
        boundary = 'astral' + uuid.uuid4().hex
        filename = local.name.replace('"', '_').replace('\r', '_').replace('\n', '_')
        head = (f'--{boundary}\r\nContent-Disposition: form-data; name="files"; filename="{filename}"\r\n'
                'Content-Type: application/octet-stream\r\n\r\n').encode('utf-8')
        tail = f'\r\n--{boundary}--\r\n'.encode()
        connection = http.client.HTTPSConnection(url.hostname, url.port, timeout=300)
        try:
            connection.putrequest('POST', url.path + '?' + query)
            connection.putheader('Content-Type', 'multipart/form-data; boundary=' + boundary)
            connection.putheader('Content-Length', str(len(head) + local.stat().st_size + len(tail)))
            connection.endheaders()
            connection.send(head)
            with local.open('rb') as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                    connection.send(chunk)
            connection.send(tail)
            response = connection.getresponse()
            response.read()
            if not 200 <= response.status < 300:
                raise LocalError('El servidor rechazo la subida.')
        finally:
            connection.close()


def safe_path(value):
    path = PurePosixPath(value)
    if '..' in path.parts or not path.is_absolute():
        raise argparse.ArgumentTypeError('Usar una ruta absoluta del servidor, sin ..')
    return str(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--yes', action='store_true')
    mode.add_argument('--dry-run', action='store_true')
    sub = parser.add_subparsers(dest='action', required=True)
    for action in ('list', 'read'):
        cmd = sub.add_parser(action)
        cmd.add_argument('remote', type=safe_path)
    for action in ('write', 'upload'):
        cmd = sub.add_parser(action)
        cmd.add_argument('local', type=Path)
        cmd.add_argument('remote', type=safe_path, help='Archivo destino (write) o carpeta destino (upload)')
    sub.add_parser('command').add_argument('command')
    sub.add_parser('restart')
    args = parser.parse_args()
    try:
        if hasattr(args, 'local') and not args.local.is_file():
            raise LocalError('No existe el archivo local indicado.')
        if not args.yes:
            print('DRY-RUN: ' + args.action + ' (sin red, sin leer claves ni contenido de archivos)')
            if hasattr(args, 'remote'):
                print('Destino: ' + args.remote)
            return
        client = Client(require(fields('Clave de API del panel'), 'Clave'))
        if args.action == 'upload':
            client.upload(args.local, args.remote)
        elif args.action == 'write':
            client.request('POST', '/files/write?' + urlencode({'file': args.remote}),
                           args.local.read_bytes(), 'text/plain')
        elif args.action in ('list', 'read'):
            route, key = ('list', 'directory') if args.action == 'list' else ('contents', 'file')
            data = client.request('GET', '/files/' + route + '?' + urlencode({key: args.remote}))
            if args.action == 'list':
                for entry in json.loads(data)['data']:
                    print(entry['attributes']['name'])
            else:
                # Lectura explicita: no usar sobre credenciales ni archivos privados.
                print(data.decode('utf-8'))
        else:
            route, data = ('command', {'command': args.command}) if args.action == 'command' else ('power', {'signal': 'restart'})
            client.request('POST', '/' + route, json.dumps(data).encode())
        if args.action not in ('list', 'read'):
            print('Accion completada.')
    except LocalError as error:
        parser.exit(1, str(error) + '\n')
    except Exception:
        parser.exit(1, 'Fallo la operacion del panel; detalles privados omitidos.\n')


if __name__ == '__main__':
    main()
