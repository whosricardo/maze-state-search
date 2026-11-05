import argparse


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Final graph project"
    )
    
    parser.add_argument("map_path", help="Path to the map file")
    parser.add_argument("--graph", choices=["pos", "est"], default="pos", help="Type of graph used")
    parser.add_argument("--output_location", default=None ,help="Location to save the output result")
    parser.add_argument("--visualizar", action="store_true" , help="Enables graphical visualization of the result")
    
    return parser.parse_args(argv)


if __name__ == "__main__":
    config = parse_args()
    print(config)