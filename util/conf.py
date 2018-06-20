"""
Contains code related to program configuration.
See readme for more information.
"""
import json
from enum import Enum

__author__ = 'michal.toporowski'


class Configuration:
    """
    Configuration object
    """
    comments = False
    """Should the converter add comments?"""
    multiple_xmls_in_file = False
    """Are multiple XML's in a single file allowed?"""

    def __init__(self, _xpaths: {}) -> None:
        self.xpaths = _xpaths


class SubstGenPolicy(Enum):
    ALWAYS = 1
    """Generator expression evaluated for each element"""
    CACHED = 2
    """Generator expression evaluated once"""


class SubstitutionDef:
    """
    Definition, how the values are substituted
    """

    def __init__(self, gen_value: str, policy: SubstGenPolicy = SubstGenPolicy.ALWAYS) -> None:
        self.gen_value = gen_value
        """Generator expression"""
        self.policy = policy

    def __repr__(self) -> str:
        return '[{0}] "{1}"'.format(self.policy, self.gen_value)


def parse_conf(filename: str, override_conf_param: str) -> Configuration:
    """
    Parses the configuration from input file.
    :param filename: name of a file containing the configuration in JSON format
    :param override_conf_param: string containing JSON overriding the configuration from file (optional - may be None)
    :return: a Configuration object
    """
    with open(filename) as conf_file:
        conf = json.load(conf_file)
    if override_conf_param:
        override_conf = json.loads(override_conf_param)
        for main_key in ['predef', 'conf']:
            if main_key in override_conf:
                conf[main_key].update(override_conf[main_key])
    predefs = {}
    if 'predef' in conf:
        for predef_key, subst_def in conf['predef'].items():
            predefs[predef_key] = __parse_substitution_def(subst_def)
    xpaths = {}
    if 'xpaths' in conf:
        for xpath, subst_def in conf['xpaths'].items():
            xpaths[xpath] = __parse_substitution_def(subst_def, predefs)
    c = Configuration(xpaths)
    if 'conf' in conf:
        if 'comments' in conf['conf']:
            c.comments = bool(conf['conf']['comments'])
        if 'multiple_xmls_in_file' in conf['conf']:
            c.multiple_xmls_in_file = bool(conf['conf']['multiple_xmls_in_file'])
    return c


def __parse_substitution_def(json_elem, predefs: dict = None) -> SubstitutionDef:
    if isinstance(json_elem, dict):
        if predefs and 'predef' in json_elem:
            predef_key = json_elem['predef']
            if predef_key in predefs:
                return predefs[predef_key]
            else:
                raise ValueError("Invalid predef key: " + predef_key)
        else:
            return SubstitutionDef(json_elem['gen_value'], SubstGenPolicy[json_elem['policy'].upper()])
    elif isinstance(json_elem, str):
        return SubstitutionDef(json_elem)
    else:
        raise ValueError("Invalid element: {0}. Expected dict or str.".format(json_elem))
