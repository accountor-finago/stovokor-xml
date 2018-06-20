#!/usr/bin/env python
"""
Class for generating or regenerating values.
May be used as standalone script or from other scripts through generate() function.
See generators.py -h for options.
"""
import logging
import random
import string
import sys
from argparse import ArgumentParser

from gen import bankaccounts
from util import randomization

__author__ = 'michal.toporowski'


def generate(arguments: []) -> str:
    parser = create_parser()
    args = parser.parse_args(arguments)
    return args.func(args)


def create_parser() -> ArgumentParser:
    parser = ArgumentParser(description='Generate a string using a generator')
    subparsers = parser.add_subparsers(help="generator name, see gen_name -h for more options", dest='gen_name')
    subparsers.required = True
    parser_const = subparsers.add_parser('const', help="generates a constant value")
    parser_const.set_defaults(func=generate_const)
    parser_const.add_argument('value', metavar='value', type=str, help='a constant value')
    parser_alphanum = subparsers.add_parser('alphanum', help='generates an alphanumeric string')
    parser_alphanum.set_defaults(func=generate_alphanum)
    parser_alphanum.add_argument('-l', type=int, help='generated string length', dest='length', required=True)
    parser_num = subparsers.add_parser('num', help='generates a number')
    parser_num.set_defaults(func=generate_num)
    parser_num.add_argument('-l', type=int, help='generated number length', dest='length')
    parser_num.add_argument('--min', type=int, help='minimal value', dest='min')
    parser_num.add_argument('--max', type=int, help='minimal value', dest='max')
    parser_iban_regenerate = subparsers.add_parser('iban_regenerate',
                                                   help='replaces account in an iban number keeping the country and bank')
    parser_iban_regenerate.set_defaults(func=regenerate_iban)
    parser_iban_regenerate.add_argument('old_iban', metavar='old_iban', type=str, help='old iban number')
    parser_iban_random = subparsers.add_parser('iban_random',
                                               help='generates a random IBAN. Note, that the bank account may not be valid, '
                                                    'use iban_regenerate if you want only to obfuscate an existing iban.')
    parser_iban_random.set_defaults(func=generate_random_iban)
    parser_iban_random.add_argument('country_code', metavar='country_code', type=str, help='2-letter country code')
    parser_bban_regenerate = subparsers.add_parser('bban_regenerate',
                                                   help='replaces account in an bban number keeping the country and bank')
    parser_bban_regenerate.set_defaults(func=regenerate_bban)
    parser_bban_regenerate.add_argument('old_bban', metavar='old_bban', type=str, help='old bban number')
    parser_bban_regenerate.add_argument('-c', metavar='country_code', dest='country_code', type=str, help='2-letter country code',
                                        required=True)
    subparsers.add_parser('namelike',
                          help='generates a random "name-like" string (two capitalized words with random letters)') \
        .set_defaults(func=random_namelike)
    parser_name_regenerate = subparsers.add_parser('name_regenerate', help='replaces all letters in a name with random ones')
    parser_name_regenerate.set_defaults(func=regenerate_name)
    parser_name_regenerate.add_argument('old_name', type=str, help='old name')
    subparsers.add_parser('klingon', help='a random Klingon quote').set_defaults(func=klingon)

    return parser


def generate_const(args) -> str:
    return args.value


def generate_alphanum(args):
    return randomization.random_with_chars(args.length, string.ascii_lowercase + string.ascii_uppercase + string.digits)


def generate_num(args):
    if args.min and args.max:
        min_val = args.min
        max_val = args.max
        if args.length:
            max_val = min(max_val, pow(10, args.length) - 1)
        num = str(random.randint(min_val, max_val))
        if args.length:
            num = num.zfill(args.length)
        return num
    elif args.length:
        return randomization.random_numeric(args.length)
    raise Exception('Invalid arguments to "num" generator - either min+max or length is required')


def regenerate_iban(args) -> str:
    """
    Regenerates an IBAN number (replaces the account number, while keeping the country and bank part)
    :param args: arguments containing old_iban
    :return: new iban as string
    """
    return bankaccounts.regenerate_iban(args.old_iban)


def generate_random_iban(args) -> str:
    """
    Generates a random iban for a given country.
    Note, that a random bank code may not belong to any bank. If you want to regenerate an existing iban, use the regenerate_iban function.
    """
    return bankaccounts.generate_random_iban(args.country_code)


def regenerate_bban(args) -> str:
    """
    Regenerates an BBAN number (replaces the account number, while keeping the country and bank part)
    :return: new bban as string
    """
    return bankaccounts.regenerate_bban(args.country_code, args.old_bban)


def klingon(args) -> str:
    """
    :return: a random Klingon quote
    """
    return random.choice(
        ['baH', 'Ghos', 'gik\'tal', "he' HImaH", "Mahk-cha", "Qapla'", "matlh! jol yIchu'", "taH pagh taHbe'", "Heh Cho'mruak tah"])


def random_namelike(args) -> str:
    """
    :return: a random "name-like" string (two capitalized words)
    """
    name = randomization.random_alpha_capitalized_varlength(5, 10)
    surname = randomization.random_alpha_capitalized_varlength(5, 10)
    return name + ' ' + surname


def regenerate_name(args) -> str:
    """
    Replaces all letters in a name with random ones
    """
    old_name = args.old_name
    return ' '.join(map(lambda name_part: randomization.random_alpha_capitalized(len(name_part)), old_name.split(' ')))


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    print(generate(sys.argv[1:]))
