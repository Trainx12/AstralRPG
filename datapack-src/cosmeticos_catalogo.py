"""Catalogo propio; ningun modelo ni textura licenciada se guarda aqui."""
# clave, nombre, rareza, fuente (modelo relativo del original)
HATS = [
    ('frankenstein', 'Cabeza de Frankenstein', 'epic', 'custom/318'),
    ('bruja', 'Sombrero de Bruja', 'epic', 'custom/319'),
    ('diablo', 'Cuernos de Diablo', 'epic', 'custom/320'),
]
for key, name in [('armorer','Armero'), ('butcher','Carnicero'),
                  ('cartographer','Cartografo'), ('cleric','Clerigo'),
                  ('desert','Desierto'), ('farmer','Granjero'),
                  ('fisherman','Pescador'), ('fletcher','Flechero'),
                  ('librarian','Bibliotecario'), ('savanna','Sabana'),
                  ('shepherd','Pastor'), ('snow','Nieve'),
                  ('swamp','Pantano'), ('weaponsmith','Herrero')]:
    HATS.append((key, 'Gorro de '+name, 'rare' if key in ('cleric','librarian','snow','swamp') else 'common', 'item/villager_hat_'+key))
HATS += [('illusioner','Capucha de Ilusionista','epic','item/illager_hat_illusioner'),
         ('vindicator','Capucha de Vindicador','epic','item/illager_hat_vindicator'),
         ('carnivora','Sombrero de Carnivora','epic',None)]
WINGS = []  # Retiradas por pedido del dueno; no volver a sortear permisos antiguos.


def catalog():
    return [('sombrero', key, name, rarity, 'cosmeticos/sombrero_'+key)
            for key,name,rarity,_ in HATS] + [
            ('alas',key,name,rarity,model) for key,name,rarity,model in WINGS]
