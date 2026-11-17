# CrazyCrates: retirar Menu de las vitrinas

Aplicar solo `gui.toggle: false` sobre el config vigente del servidor.
Conservar todas las demas claves y las flechas de paginacion.

Desde la raiz: `python tools/configurar_crazycrates.py <copia-config-vigente> --output .local/crazycrates-server/config-sin-menu.yml`.
Subir esa copia a `plugins/CrazyCrates/config.yml` y ejecutar `crates reload`.
El config completo y el JAR de terceros permanecen privados.
