# [IA] Claude Code (Opus 5.5) – interface pygame: ponto de entrada (python -m src.frontend)
import argparse
import sys
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python -m src.frontend",
        description="Labirinto interativo (pygame) sobre o grafo de estados do grupo.",
    )
    parser.add_argument("mapas", nargs="*", help="mapas .txt extras (ex.: o mapa surpresa)")
    parser.add_argument("--mapa", action="append", default=[], help="abre este mapa ao iniciar")
    parser.add_argument("--editor", action="store_true", help="abre direto no editor de mapas")
    args = parser.parse_args(argv)

    try:
        import pygame  # noqa: F401
    except ImportError:
        print("pygame não está instalado. Rode:  pip install -r requirements.txt", file=sys.stderr)
        return 1

    extras = [Path(p) for p in args.mapas + args.mapa]
    for path in extras:
        if not path.exists():
            print(f"Mapa não encontrado: {path}", file=sys.stderr)
            return 1

    from src.frontend.app import App

    initial = extras[-1] if extras else None
    App(extra_maps=extras, initial=initial, start_in_editor=args.editor).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
