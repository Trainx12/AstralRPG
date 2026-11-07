# Claude dirige, Codex implementa

El puente local `tools/invoke-codex-plan.mjs` permite que Claude Code invoque Codex sin que el usuario copie planes entre chats. Usa el Codex CLI ya instalado y su sesion de ChatGPT. Inicia una ejecucion independiente: no envia mensajes al chat de Codex que este abierto.

## Flujo

1. Claude analiza el pedido y guarda un plan concreto en `.local/coordination/plan.md`, con objetivo, alcance, archivos, criterios de aceptacion y pruebas necesarias.
2. Claude ejecuta desde la raiz del proyecto:

   ```text
   node tools/invoke-codex-plan.mjs --plan .local/coordination/plan.md --publish
   ```

3. Claude espera el proceso hasta que termine. Si su terminal devuelve un identificador de proceso/sesion, sigue consultandolo; no inicia otro implementador ni modifica archivos al mismo tiempo.
4. Claude lee `.local/coordination/latest-result.md`, revisa los resultados y pide una correccion por el mismo puente si hace falta. Cada ejecucion debe recibir un plan actualizado con el contexto necesario.
5. Claude continua el despliegue en el panel de Empower (https://gp.empowerservers.com/server/44d1ad66) con sus herramientas de navegador, si estan disponibles, siguiendo `docs/GUIA.md`. El usuario inicia sesion si el panel la solicita. Si no hay navegador o aparece un bloqueo, informa que el despliegue sigue pendiente. No simula una subida.

`--publish` transmite la autorizacion del dueno para commit/push de esa tarea. Sin esa opcion el trabajo queda local. La revision automatica de aprobaciones puede detener acciones; el puente no la desactiva ni garantiza una ejecucion sin intervencion.

## Estado y limites

- Codex CLI fue detectado y tiene sesion iniciada con ChatGPT.
- El remoto es `https://github.com/Trainx12/AstralRPG.git`.
- `gh auth status` informo un token invalido en esta comprobacion. Esto no demuestra que las credenciales de `git push` fallen: hay que verificar el push real de la tarea. Si falla la autenticacion, el dueno debe iniciar sesion por la herramienta correspondiente.
- Hay trabajo local previo. Codex debe conservarlo y evitar publicarlo como parte de otra tarea.
- El puente no contiene un despliegue automatico al panel (Empower tiene SFTP, pero la clave es del dueno). Esa parte depende de las herramientas de navegador de Claude y de una sesion valida.
- Los planes y resultados se guardan en `.local/`, ya ignorada por Git. Se conserva el historial de cada invocacion.
- El bloqueo impide dos invocaciones simultaneas de este puente; no bloquea otros chats o editores. No trabajar simultaneamente en los mismos archivos.
- La preparacion se valida con `--dry-run`. Una ejecucion real consume el uso disponible de Codex; no se lanza hasta que Claude tenga una tarea concreta.

Referencias: [Codex no interactivo](https://learn.chatgpt.com/docs/non-interactive-mode), [Autenticacion de Codex](https://learn.chatgpt.com/docs/auth), [Archivos y FTP en Aternos](https://support.aternos.org/hc/en-us/articles/360027235831-Uploading-files-and-FTP-access).
