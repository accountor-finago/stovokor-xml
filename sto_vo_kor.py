"""
A tool for modifying/obfuscating XML files.
"""
import logging
import os
from argparse import ArgumentParser

from util.conf import parse_conf, Configuration
from xmlconversion import convert

__author__ = 'michal.toporowski'


def run():
    """
    Runs the program for arguments given in command line.
    """
    args = parse_args()
    conf = parse_conf(args.conf, args.override)
    convert_file_or_dir(args.input, args.output, conf)
    logging.info("All files converted.\nHave a nice day // Hyvää päivän jatkoa // Miłego dnia")


def parse_args():
    """
    Passes the CLI arguments
    :return: arguments object
    """
    parser = ArgumentParser(description='A tool for modifying/obfuscating XML files.')
    parser.add_argument('-i', type=str, required=True, dest='input', help='input file or directory')
    parser.add_argument('-o', type=str, dest='output', help='output file or directory (optional)')
    parser.add_argument('-c', type=str, required=True, dest='conf', help='json configuration file')
    parser.add_argument('--override', type=str, help='json string overriding the configuration from file')
    return parser.parse_args()


def convert_file_or_dir(input_file_or_dir: str, output_file_or_dir: str, conf: Configuration):
    """
    Processes a file or directory
    :param input_file_or_dir: input file or directory path
    :param output_file_or_dir:  output file or directory path (or None if not specified)
    :param conf: configuration object
    """
    if os.path.isdir(input_file_or_dir):
        # A directory - convert all files from that directory
        files = [f for f in os.scandir(input_file_or_dir) if f.is_file() and not f.name.endswith('.out.xml')]
        count = len(files)
        if not output_file_or_dir:
            output_dir = os.path.abspath(input_file_or_dir) + '.out'
        elif os.path.isfile(output_file_or_dir):
            raise ValueError("Output cannot be a file, when input is a directory")
        else:
            output_dir = output_file_or_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        logging.info('Directory passed as input. Converting {0} files from the given directory into: {1}.'.format(count, output_dir))
        for i, f in enumerate(files):
            input_file = f.path
            output_file = os.path.join(output_dir, os.path.basename(input_file))
            __convert_single_file(input_file, output_file, conf)
            converted = i + 1
            logging.info('Converted file {0}/{1} ({2}% done)'.format(converted, count, converted * 100 / count))
    else:
        # A single file
        input_file = input_file_or_dir
        if not output_file_or_dir:
            output_file = input_file + '.out.xml'
        else:
            output_file = output_file_or_dir
        __convert_single_file(input_file, output_file, conf)


def __convert_single_file(input_file: str, output_file: str, conf: Configuration):
    """
    Converts a single file.

    :param input_file: input file path, required
    :param output_file: output file path, required
    :param conf: configuration object
    """
    if os.path.abspath(input_file) == os.path.abspath(output_file):
        raise ValueError('Output cannot be equal to input')
    if not os.path.exists(input_file):
        raise ValueError('Input file {0} does not exist'.format(input_file))
    if os.path.isdir(output_file):
        raise ValueError('Output file {0} is an existing directory. Specify another output'.format(output_file))
    convert(input_file, output_file, conf)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    run()
