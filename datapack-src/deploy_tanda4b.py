"""Manifiesto publico reproducible; no instala ni publica archivos."""
from terceros import ROOT, PETS, privado


def main():
    prefix='.local/terceros/AstralRPG-privado/build/'
    sha=(privado()/'build/pack.sha1').read_text().strip()
    paths=[('build/AstralRPG-Items.zip','world/datapacks/AstralRPG-Items.zip'),
           ('build/runtime/AstralDecor.jar','plugins/AstralDecor.jar'),
           (prefix+'AstralRPG-Textures.zip','Cloudflare R2: AstralRPG-Textures.zip'),
           ('build/shop/EconomyShopGUI/sections/Peluches.yml','plugins/EconomyShopGUI/sections/Peluches.yml'),
           ('build/shop/EconomyShopGUI/shops/Peluches.yml','plugins/EconomyShopGUI/shops/Peluches.yml')]
    paths += [('build/mythicmobs/'+kind+'/tanda4b.yml','plugins/MythicMobs/'+kind+'/tanda4b.yml') for kind in ('mobs','skills')]
    paths += [(prefix+'models/astral_pet_'+pid+'.bbmodel','plugins/BetterModel/models/astral_pet_'+pid+'.bbmodel') for pid,*_ in PETS]
    lines=['# Tanda 4b: preparada, sin desplegar','',
        'Generado por `python datapack-src/deploy_tanda4b.py`. Servidor activo documentado: Empower; Aternos es copia. No se realizo instalacion remota.',
        '', '## Archivos locales -> destinos', '', '| Local | Destino |','|---|---|']
    lines += [f'| `{src}` | `{dst}` |' for src,dst in paths]
    lines += ['', 'Si ASTRAL_PRIVADO apunta a otro clon, sustituir el prefijo privado. La tanda 4a es prerrequisito: si aun no esta instalada, seguir tambien `build/deploy/tanda4a.md`, usando SIEMPRE el pack FINAL y SHA-1 de esta tanda. Conservar todos los modelos propios de tandas anteriores, especialmente astral_bosque_planta y skills tanda3a.',
        '', '## Apagado y arranque', '',
        '1. Respaldar los archivos de destino y server.properties. Apagar el servidor. No sustituir ningun mundo ni usar Worlds > Upload sobre world.',
        '2. Instalar las rutas de la tabla. Paper 26.1.2 con Java 25; WorldGuard + WorldEdit para proteger muebles; MythicMobs, BetterModel y sus dependencias existentes; Vault con proveedor de economia (Essentials).',
        '3. Verificar que el slot 39 este libre en las secciones de la tienda. Si se ocupo desde la copia local, ajustar SOLO slot en Peluches.yml antes de instalar; no reemplazar configs ajenas.',
        '4. Subir el pack FINAL privado a R2 desde la raiz local:', '',
        '`python tools/subir_pack_r2.py .local/terceros/AstralRPG-privado/build/AstralRPG-Textures.zip`', '',
        '5. Solo despues de verificar descarga publica, conservar la URL fija R2 y actualizar:', '',
        f'`resource-pack-sha1={sha}`', '',
        'URL: https://pub-5e0d1c63a1554ba7b8e33b038e1a06fe.r2.dev/AstralRPG-Textures.zip', '',
        '6. Encender y revisar consola. El JAR nuevo y el datapack requieren reinicio completo; no usar PlugMan ni reload global de Bukkit.',
        '7. El arranque carga todo. Para futuras pruebas que cambien SOLO YAML: `mm reload`, `bettermodel reload`, `sreload` (EconomyShopGUI). No reemplazan el reinicio de este despliegue.',
        '', '## Tienda, contenido y limitaciones', '',
        '- EconomyShopGUI gratuito reserva componentes y compras por comandos para Premium. La seccion Peluches abre, mediante AstralDecor, un inventario propio; Vault cobra $2.500 por unidad. Sin saldo, proveedor o espacio libre no entrega. No hay reventa. Referencia: https://wiki.gpplugins.com/economyshopgui/file-configuration/shops.yml',
        '- Carnivora T3: cuatro armaduras (225 de vida cada una y 200 de defensa total), armas con componentes de sus clases T3, herramientas con Eficiencia III, cana y escudo. Martillo comparte balance del hacha. Llave y cofre no tienen uso Astral: no se crean items, recetas ni llaves de gachas para ellos.',
        '- Asura T4: espada equivalente a espada_4; alas cosmeticas; las cinco monedas entran en ambas recetas. Esmeralda comun; carta, circulo, cuadrado y triangulo comparten un 8% extra por mena. Fortuna aumenta la esmeralda; no hay drop del bloque con Toque de Seda.',
        '- Alas de ambos sets: cosmetico de pecho con item_display unido al jugador. No permiten volar ni conservan proteccion de pechera. Sin mods, el equipment asset vanilla no acepta la geometria Java de estos items como elytra.',
        '- Mena: banjo/nota24 del note_block (ambos powered). AstralDecor llama a la configured_feature del datapack en chunks NUEVOS del End a radio >=1024; 1/8 de los chunks, veta maxima 3, altura 30..75. No cambia biomas ni Stellarity y no regenera chunks explorados.',
        '- Estado reservado: sin sonido, afinacion, empuje por pistones ni destruccion por explosion. Los note_block normales banjo recorren notas 0..23 (pierden nota24); los demas instrumentos conservan las 25. Otros packs que reemplacen note_block o su loot requieren combinarse. Mantener AstralDecor instalado mientras exista esta mena.',
        '- Plantas: solo mundo world, cada 20s y alrededor de jugadores; pantano/manglar 65%, selva 70%, bambu 65%, selva dispersa 50%, roble oscuro 35%, bosques 8%. Tope 2/chunk y 6 en 48 bloques. Requieren permiso WorldGuard build en el punto; lobby, mazmorras, minas, bosque astral y arena son otros mundos. Perillas en runtime/AstralDecor.java y DROP_CHANCE en tanda4b_world.py.',
        '- Muebles: una unidad consumida tambien en creativo, item guardado en PDC de Interaction, visual enlazado por UUID. Clic izquierdo devuelve una sola vez; respeta WorldGuard build y eventos cancelados de colocacion. Sin WorldGuard falla cerrado. No retirar entidades a mano ni con limpiadores: excluir Interaction e ItemDisplay de limpiezas.',
        '- Mascotas: metadatos ocultos y contornos invertidos removidos solo en copias privadas. Originales intactos. Vistas estaticas privadas tanda4a.png y tanda4b.png; no son capturas del juego.',
        '', '## Validacion al instalar', '',
        'Comandos como jugador OP (usar un lugar de prueba autorizado):', '',
        '```text','/function astral:admin/kit_carnivora','/function astral:admin/kit_asura_peluches',
        '/trigger astral.guia','/economyshopgui:shop Peluches','```','',
        'Comprobar saldo exacto de una compra, falta de saldo e inventario lleno; colocar/recoger seis peluches y repetir clics, reconectar y reiniciar; probar denegacion con un jugador sin build en WorldGuard; ver alas y armadura desde otro jugador; tensar arco, lanzar cana y bloquear escudo. Comprobar mascotas sin cuadrados en idle y movimiento.',
        'Explorar chunks nuevos de islas del End, comprobar monedas con/sin Fortuna y sin pico; tocar mena y activar redstone/pistones. Verificar plantas por bioma y tier, limites y drops/plata. Revisar consola despues. Estas interacciones requieren jugador y siguen pendientes; las pruebas locales de carga no las certifican.',
        '', '## Reproduccion y pruebas locales', '',
        'Desde datapack-src: `python build.py` y `python build_pack.py pack-source`. Desde la raiz: `python datapack-src/build_privado.py --prepare`; copiar modelos publicos y superponer privados en un Paper local con BetterModel; arrancar y apagar tras exportar assets. Luego `python datapack-src/build_privado.py --assets <servidor-local>/plugins/BetterModel/build/assets` y `python datapack-src/preview_tanda4b.py`.',
        '`python datapack-src/build_runtime.py --jdk <JDK25>/bin --server <servidor-local>` compila solo nuestro AstralDecor.java contra las bibliotecas locales de Paper. No incluye binarios ajenos. El plugin es necesario para bloquear fisica/afinacion de mena, disparar su feature solo en chunks nuevos, poner/recoger muebles con proteccion, unir alas al jugador y cobrar la tienda gratuita via Vault.',
        'Verificado: 179 pruebas unittest, verify.py (incluye comandos exclusivamente vanilla en mcfunction), compilacion Java 25, carga Paper 26.1.2 + BetterModel 3.6.0 + MythicMobs 5.13.0 + ExcellentEnchants 5.4.3/NightCore 2.16.7; 194 mobs, planta invocada con mob/roll, feature colocada sobre end_stone de prueba y loot de espada/peluche/armadura. Sin errores de carga del datapack. Avisos previos de dialogos de ejemplo y aviso MythicMobs al apagar con un mob activo. WorldGuard, economia e interacciones de jugador pendientes en entorno completo.',
        'Antes de commit publico: agregar solo rutas de la tarea y ejecutar `python tools/verificar_terceros.py`. Todo el arte y las vistas de terceros quedan en el clon privado; los dos repositorios se publican por separado.',
        '', f'SHA-1 FINAL privado: `{sha}`. Publicacion GitHub y despliegue son pasos distintos.', '']
    target=ROOT/'build/deploy/tanda4b.md';target.parent.mkdir(exist_ok=True,parents=True)
    target.write_text('\n'.join(lines),encoding='utf8')


if __name__=='__main__': main()
