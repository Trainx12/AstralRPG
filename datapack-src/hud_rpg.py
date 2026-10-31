"""HUD elegido por el usuario; barra inferior, XP y recarga heredadas de vanilla."""
from PIL import Image

E = 4


def hud(alta_resolucion=False):
    """HUD de referencia. Las barras inferiores y de jefes se heredan de vanilla."""
    from reference_style import hud as reference_hud
    sprites = reference_hud()
    if alta_resolucion:
        return {path: im.resize((im.width * E, im.height * E), Image.Resampling.NEAREST)
                for path, im in sprites.items()}
    return sprites


def preview(path, client_jar=None):
    from reference_style import preview as reference_preview
    vanilla = None
    if client_jar:
        import zipfile
        import io
        with zipfile.ZipFile(client_jar) as client:
            vanilla = {name: Image.open(io.BytesIO(client.read("assets/minecraft/textures/gui/sprites/hud/" + filename))).convert("RGBA")
                       for name, filename in (("hotbar", "hotbar.png"), ("selection", "hotbar_selection.png"))}
    reference_preview(path, vanilla)


if __name__ == "__main__":
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-jar")
    args = parser.parse_args()
    path = Path(__file__).resolve().parent.parent / "build/HUD-preview.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    preview(path, args.client_jar)
    print(path)
