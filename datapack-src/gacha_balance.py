"""Pesos y suerte compartidos por CrazyCrates y los mensajes del runtime."""
RARITY_WEIGHT = {"common": 60, "uncommon": 25, "rare": 11, "epic": 3.5, "legendary": 0.5}
FACTOR_SUERTE = 1.5
RAREZAS_SUERTE = ('rare', 'epic', 'legendary')


def luck_data():
    boosted = {r: w * (FACTOR_SUERTE if r in RAREZAS_SUERTE else 1) for r, w in RARITY_WEIGHT.items()}
    def pct(value):
        return f'{value:.1f}'.removesuffix('.0').replace('.', ',') + '%'
    labels = dict(rare='Raro', epic='Epico', legendary='Legendario')
    return {'suerte_factor': str(FACTOR_SUERTE).replace('.', ','),
            'suerte_porcentajes': {r: {'normal': 100 * RARITY_WEIGHT[r] / sum(RARITY_WEIGHT.values()),
                                     'suerte': 100 * boosted[r] / sum(boosted.values())} for r in RAREZAS_SUERTE},
            'suerte_detalle': '  ·  '.join(f'{labels[r]} {pct(100 * RARITY_WEIGHT[r] / sum(RARITY_WEIGHT.values()))} → {pct(100 * boosted[r] / sum(boosted.values()))}' for r in RAREZAS_SUERTE)}
