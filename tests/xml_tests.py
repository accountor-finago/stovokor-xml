import os
import unittest
from unittest.mock import Mock

import xmlconversion
from gen import generators
from util import conf


class XmlTest(unittest.TestCase):
    """
    Unit tests for XML conversion module
    """

    def setUp(self):
        self.conf = conf.parse_conf('testdata' + os.sep + 'example_conf.json', None)
        # Generators are based on randomization, so let's mock them to have a deterministic result
        generators.generate = Mock(side_effect=lambda args: "Generator mock value for: " + ' '.join(args))

    def test_all(self):
        datasets = ['simple', 'namespaces']
        for dataset in datasets:
            with self.subTest(i=dataset):
                self.__assert_result_equals_expected(dataset)

    def __assert_result_equals_expected(self, data_set: str) -> None:
        """
        Asserts that the conversion results for file {data_set}.xml is equal to the {data_set}.expected.xml
        Assumes, that the input and expected output files exist in testdata/ folder.
        :param data_set: file names prefix
        """
        input_file = 'testdata' + os.sep + data_set + '.xml'
        expected_file = 'testdata' + os.sep + data_set + '.expected.xml'
        actual_output_file = 'testdata' + os.sep + data_set + '.out.xml'
        xmlconversion.convert(input_file, actual_output_file, self.conf)

        with open(actual_output_file, 'r') as actual:
            with open(expected_file, 'r') as expected:
                self.assertEqual(actual.read(), expected.read())

        os.remove(actual_output_file)
