import unittest
from pollard_rho import pollard_rho


class TestFactor(unittest.TestCase):

    def test_pollard1(self):
        n = 2 ** 2 ** 11 + 1
        d = pollard_rho(n)
        self.assertEqual(n % d, 0, "d should divide n")


if __name__ == "__main__":
    unittest.main()
