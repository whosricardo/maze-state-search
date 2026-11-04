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
    
if __name__ == "__main__":
    unittest.main()