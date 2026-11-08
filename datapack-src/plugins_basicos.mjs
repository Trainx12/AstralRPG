// Exporta solo los presets revisados. No modifica el servidor ni otros plugins.
import { readdir, readFile, mkdir, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const source = resolve(dirname(fileURLToPath(import.meta.url)), 'plugin-presets');
const destination = resolve(source, '../../build/plugins-basicos');
for (const filename of await readdir(source)) {
  const [plugin, file] = filename.split('--');
  if (!plugin || !file || filename.split('--').length !== 2) {
    throw new Error(`Nombre de preset invalido: ${filename}`);
  }
  const content = await readFile(resolve(source, filename), 'utf8');
  if (file.endsWith('.json')) JSON.parse(content);
  await mkdir(resolve(destination, plugin), { recursive: true });
  await writeFile(resolve(destination, plugin, file), content, 'utf8');
  console.log(`${plugin}/${file}`);
}
