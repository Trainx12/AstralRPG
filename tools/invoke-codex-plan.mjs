import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// Codex CLI: CODEX_BIN, el del PATH, o el que trae la app de Codex de Windows (cambia de carpeta en cada actualizacion).
function findCodex() {
  if (process.env.CODEX_BIN) return process.env.CODEX_BIN;
  if (spawnSync('codex', ['--version'], { windowsHide: true }).status === 0) return 'codex';
  if (process.platform === 'win32') {
    const ps = spawnSync('powershell.exe', ['-NoProfile', '-Command',
      "(Get-AppxPackage OpenAI.Codex | Select-Object -First 1).InstallLocation"], { encoding: 'utf8', windowsHide: true });
    const dir = (ps.stdout || '').trim();
    const exe = dir && path.join(dir, 'app', 'resources', 'codex.exe');
    if (exe && fs.existsSync(exe)) return exe;
  }
  throw new Error('No se encontro Codex CLI. Instala Codex o define CODEX_BIN con la ruta a codex.exe.');
}

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const planIndex = args.indexOf('--plan');
if (planIndex < 0 || !args[planIndex + 1]) throw new Error('Uso: node tools/invoke-codex-plan.mjs --plan archivo.md [--publish] [--dry-run]');
const plan = fs.readFileSync(path.resolve(args[planIndex + 1]), 'utf8');
if (!plan.trim()) throw new Error('El plan esta vacio.');
const initial = spawnSync('git', ['-C', root, 'status', '--short'], { encoding: 'utf8', windowsHide: true });
if (initial.error || initial.status !== 0) throw new Error('No se pudo leer el estado de Git.');
const publish = args.includes('--publish')
  ? 'El dueno autoriza commit y push de ESTA tarea tras pasar las verificaciones. Agrega rutas explicitas. No publiques trabajo previo ajeno. Si no podes separar cambios previos, informa el bloqueo. No fuerces push ni cambies credenciales.'
  : 'Implementa y verifica localmente. No hagas commit ni push.';
const prompt = `Trabajas en AstralRPG como implementador. Claude Code es el arquitecto. Responde en espanol.
Lee CLAUDE.md, docs/GUIA.md y docs/SERVIDOR.md. Edita generadores y regenera salidas cuando corresponda.
Estas siendo invocado POR el puente: no vuelvas a invocar el puente ni delegues en Claude. Completa la implementacion aqui.
Conserva todo trabajo previo del usuario. No uses reset, clean, stash ni descartes cambios. El estado inicial esta abajo.
${publish}
No publiques credenciales, archivos privados, .local, logs ni mapas de terceros.
No intentes subir a Aternos por APIs privadas ni eludir restricciones. No tenes garantizado acceso al navegador. Prepara la lista exacta de archivos locales, destinos y comandos de recarga, y si requiere apagar o reiniciar. Claude continuara esa parte si tiene navegador.
Nunca sustituyas mundos ni uses Worlds > Upload en la fila world.
Informa resultado, archivos, verificaciones, commit/push con hash, despliegue pendiente y bloqueos. No afirmes despliegues sin verificar.

ESTADO GIT INICIAL:
${initial.stdout}
PLAN DE CLAUDE:
${plan}`;
if (args.includes('--dry-run')) {
  process.stdout.write(prompt);
} else {
  const runRoot = path.join(root, '.local', 'coordination');
  fs.mkdirSync(runRoot, { recursive: true });
  const lock = path.join(runRoot, 'codex.lock');
  // No borra bloqueos automaticamente: una interrupcion requiere verificar el proceso anterior.
  let lockHandle;
  try { lockHandle = fs.openSync(lock, 'wx'); }
  catch { throw new Error('Existe codex.lock. Espera la otra ejecucion; si hubo una interrupcion, verifica que termino antes de retirar el bloqueo.'); }
  try {
    fs.writeFileSync(lockHandle, String(process.pid));
    const runId = new Date().toISOString().replace(/[:.]/g, '-');
    const resultPath = path.join(runRoot, `${runId}-result.md`);
    fs.writeFileSync(path.join(runRoot, `${runId}-prompt.md`), prompt);
    const run = spawnSync(findCodex(), ['exec', '--cd', root, '--approve-for-me', '--color', 'never', '--output-last-message', resultPath, '-'], {
      input: prompt, stdio: ['pipe', 'inherit', 'inherit'], windowsHide: true,
    });
    if (fs.existsSync(resultPath)) {
      fs.copyFileSync(resultPath, path.join(runRoot, 'latest-result.md'));
      console.log(`\nRESULTADO: ${resultPath}\n${fs.readFileSync(resultPath, 'utf8')}`);
    }
    if (run.error) throw run.error;
    if (run.status !== 0) throw new Error(`Codex termino con codigo ${run.status}; no se reintento automaticamente.`);
  } finally {
    fs.closeSync(lockHandle);
    fs.unlinkSync(lock);
  }
}
