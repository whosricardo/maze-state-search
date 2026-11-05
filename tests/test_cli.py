import unittest
from src.cli import parse_args


class TestCli(unittest.TestCase):
    
    def test_parse_valid_map_path(self):
        args = parse_args(["mapa.txt"])
        self.assertEqual(args.map_path, "mapa.txt")
        

    def test_missing_map_path(self):
        with self.assertRaises(SystemExit) as context:
            parse_args([])
        
        self.assertEqual(context.exception.code, 2)
    
    
    def test_parse_default_graph(self):
        args = parse_args(["mapa.txt"])
        self.assertEqual(args.graph, "pos")


    def test_parse_valid_graph_choice(self):
        args = parse_args(["mapa.txt", "--graph", "est"])
        self.assertEqual(args.graph, "est")


    def test_parse_invalid_graph_choice(self):
        with self.assertRaises(SystemExit) as context:
            parse_args(["mapa.txt", "--graph", "invalid"])
        self.assertEqual(context.exception.code, 2)


    def test_default_output_location_is_none(self):
        args = parse_args(["mapa.txt"])
        self.assertIsNone(args.output_location)


    def test_parse_valid_output_location(self):
        args = parse_args(["mapa.txt", "--output_location", "resultado/output.txt"])
        self.assertEqual(args.output_location, "resultado/output.txt")


    def test_visualizar_default_false(self):
        args = parse_args(["mapa.txt"])
        self.assertFalse(args.visualizar)


    def test_visualizar_flag_active(self):
        args = parse_args(["mapa.txt", "--visualizar"])
        self.assertTrue(args.visualizar)
if __name__ == "__main__":
    unittest.main()