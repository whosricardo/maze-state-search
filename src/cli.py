import argparse


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Projeto Final de grafos"
    )
    
    parser.add_argument("map_path", help="Caminho para o arquivo do mapa")
    
    return parser.parse_args(argv)
