# Requisito de habilidad en bastones — 17/11/2026

Despliegue pendiente. Lista conjunta vigente con SHA-256, dependencias y pruebas:
[efectos-direccion-interruptores.md](efectos-direccion-interruptores.md).

`build/gameplay/astral_armas_especiales.sk` -> `plugins/Skript/scripts/special_weapons.sk`.
Usar una sola copia activa; conservar desactivada la duplicada del 16/11.
Recarga aislada: `skript:skript reload special_weapons` (nombre real activo).
La entrega conjunta tambien actualiza datapack, menu y AstralEfectos.jar: apagar,
reemplazar los cuatro archivos, iniciar y ejecutar `dm reload`.
Nunca reemplazar mundos ni usar Worlds > Upload en la fila world.

Prueba manual: T5 con Hechiceria 20 y mana suficiente no lanza ni cobra;
con Hechiceria 32 lanza y cobra 200. Repetir con mana insuficiente, lectura
fallida, cambio de arma, espada de agua y Heroe Errante. Con Bastones=false,
seguir viendo particulas tradicionales pero no los efectos nuevos.
