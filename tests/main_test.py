import unittest
import main

RLE_TESTS = [
    ([],[]),
    ([True, False, True], [1,1,1]),
    ([True, True], [2]),
    ([True, True, False, False], [2,2]),
]

class TestRLEConversion(unittest.TestCase):
    def test_rle(self):
        for tt, want in RLE_TESTS:
            self.assertListEqual(list(main.rle_binary(tt)), want)

if __name__ == '__main__':
    unittest.main()