"""Iconos pendientes de Gemini. Catalogo explicito; desconocidos fallan en el test de menus."""
KEYS = ('info','ayuda','configuraciones','infinita','oceano','garantia','probabilidades',
        'efectos_bajo','efectos_medio','efectos_alto','pierdes','conservas','reglas',
        'arma','cosmetico','otro','personalizada','tiradas','tier','entrar','minero_info',
        'minero_set','talador_info','talador_set','proximamente','premio','tema','plata','sin_datos')


def model(key):
    if key.startswith('proximo_'):
        key='proximamente'
    elif key.startswith('premio_'):
        key='premio'
    elif key.startswith('tema_'):
        key='tema'
    return 'astral:boton_'+key if key in KEYS else None
