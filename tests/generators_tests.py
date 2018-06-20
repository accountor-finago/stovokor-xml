import unittest

from gen import generators

__author__ = 'michal.toporowski'


class GeneratorsTest(unittest.TestCase):
    """
    Unit tests for generators module
    """

    def test_const(self):
        self.assertEqual(generators.generate(["const", "foo"]), "foo")

    def test_alphanum(self):
        res = generators.generate(["alphanum", "-l", "13"])
        self.assertEqual(len(res), 13)
        self.assertTrue(res.isalnum())

    def test_numeric_length(self):
        res = generators.generate(["num", "-l", "13"])
        self.assertEqual(len(res), 13)
        self.assertTrue(res.isnumeric())

    def test_numeric_range(self):
        for i in range(1, 10):
            with self.subTest(i=i):
                res = generators.generate(["num", "--min", "123", "--max", "40000"])
                self.assertTrue(res.isnumeric())
                self.assertGreaterEqual(int(res), 123)
                self.assertLessEqual(int(res), 40000)

    def test_numeric_both(self):
        for i in range(1, 10):
            with self.subTest(i=i):
                res = generators.generate(["num", "--min", "123", "--max", "40000", "-l", "4"])
                self.assertTrue(res.isnumeric())
                self.assertGreaterEqual(int(res), 123)
                self.assertLess(int(res), 10000)
                self.assertEqual(len(res), 4)

    def test_namelike(self):
        for i in range(1, 5):
            with self.subTest(i=i):
                res = generators.generate(["namelike"])
                self.assertRegex(res, '[A-Z][a-z]* [A-Z][a-z]*')
                self.assertGreater(len(res), 10)
                self.assertLess(len(res), 22)

    def test_name_regenerate(self):
        for i in range(1, 5):
            with self.subTest(i=i):
                res = generators.generate(["name_regenerate", "Very Secret Name"])
                self.assertRegex(res, '[A-Z][a-z]{3} [A-Z][a-z]{5} [A-Z][a-z]{3}')
