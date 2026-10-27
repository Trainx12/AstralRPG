# -*- coding: utf-8 -*-
"""
Que textura usa cada item de AstralRPG.
Las texturas salen de tu pack (carpetas assets/astral y assets/armasrpg).
Si un item no esta aca, se ve como el item vanilla parecido (no necesita textura).
"""

# Materiales: id del item -> nombre de la textura en assets/astral/textures/item
MATERIAL_TEX = {
    "netherita_fundida": "netherita_fundida",
    "netherita_reforzada": "netherita_incandescente",
    "shadowsteel": "acero_sombrio",
    "esencia_nether": "esencia_wither",
    "palo_reforzado": "palo_reforzado",
    "cuero_tratado": "cuero_tratado",
    "cristal_arcano": "cristal_arcano",
    "fragmento_umbrio": "fragmento_umbrio",
    "gema_umbria_fragmentada": "gema_umbria_fragmentada",
    "gema_umbria": "gema_umbria",
    "gema_umbria_perfecta": "gema_umbria_perfecta",
    "gema_luminica": "gema_luminica",
    "gema_luminica_perfecta": "gema_luminica_perfecta",
    "fragmento_astral": "fragmento_astral",
    "polvo_astral": "polvo_astral",
    "nucleo_astral": "nucleo_astral",
    "nucleo_furia": "nucleo_de_furia",
    "nucleo_furia_pura": "nucleo_de_furia_pura",
    "nucleo_eolico": "nucleo_eolico",
}
# La Madera Estelar usa el modelo de bloque de tu pack
BLOCK_ITEMS = {"madera_estelar": "astral:block/madera_estelar"}

# Armas: id del item -> textura en assets/armasrpg/textures/item
WEAPON_TEX = {
    "espada_1": "espada_7",
    "espada_2": "espada_2",
    "espada_3": "espada_5",
    "espada_4": "espada_4",
    "espada_5": "espada_6",
    "hacha_1": "hacha_3",
    "hacha_2": "hacha_2",
    "hacha_3": "hacha_1",
    "baston_1": "baston_8",
    "baston_2": "baston_2",
    "baston_3": "baston_19",
    "baston_4": "baston_12",
    "baston_5": "baston_9",
    "guadana_2": "scythe_3",
    "guadana_3": "scythe_2",
    "guadana_5": "scythe_1",
}
# Arcos (tienen animacion de tensado: _pulling_0, _1, _2)
BOW_TEX = {
    "arco_1": "arco_2",
    "arco_2": "arco_1",
    "arco_3": "arco_3",
    "arco_4": "arco_9",
    "arco_5": "arco_4",
}

# Lanzas
WEAPON_TEX.update({
    "lanza_1": "lanza_2",
    "lanza_2": "lanza_1",
    "lanza_3": "lanza_5",
    "lanza_4": "lanza_6",
    "lanza_5": "lanza_3",
})
