"""
File contains randomization utilities.
"""
import random
import string

__author__ = 'michal.toporowski'

choice = random.choice


def random_with_chars(length: int, allowed_chars: str):
    return ''.join(random.choice(allowed_chars) for i in range(length))


def random_numeric(length: int) -> str:
    return random_with_chars(length, string.digits)


def random_alpha_capitalized_varlength(min_len: int, max_len: int) -> str:
    return random_alpha_capitalized(random.randint(min_len, max_len))


def random_alpha_capitalized(length: int) -> str:
    return random_with_chars(length, string.ascii_lowercase).capitalize()
