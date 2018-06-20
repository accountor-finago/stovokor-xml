"""
Contains code related to XML files conversion.
"""

import logging

from lxml import etree
from lxml.etree import ElementTree

from gen import generators
from util.conf import Configuration, SubstitutionDef, SubstGenPolicy

__author__ = 'michal.toporowski'

logger = logging.getLogger(__name__)


def convert(input_file: str, output_file: str, conf: Configuration):
    """
    Converts an input file into an output file using a given configuration.
    if conf.multiple_xmls_in_file is true, then the file may contain multiple XML-s.
    """
    logger.info('>> Converting file {0}'.format(input_file))
    if conf.multiple_xmls_in_file:
        # Allow multiple XML-s in one file
        xmlstrs = __extract_xmls_from_file(input_file)
        with open(output_file, 'w+b') as output:
            for i, xmlstr in enumerate(xmlstrs):
                logger.info('<> Converting XML {0}/{1} from file {2}.'.format(i + 1, len(xmlstrs), input_file))
                xml = etree.fromstring(xmlstr)
                __convert_xml(xml, conf)
                outxml = etree.tostring(xml, xml_declaration=True, encoding="utf-8")
                output.write(outxml)
    else:
        # Single XML in file mode
        xml = etree.parse(input_file)
        __convert_xml(xml, conf)
        xml.write(output_file, xml_declaration=True, encoding="utf-8")
    logger.info('<< Converted file {0} into {1}'.format(input_file, output_file))


def __convert_xml(xml: ElementTree, conf: Configuration):
    """
    Replaces elements in a XML element tree using a given configuration.
    """
    for xpath, subst_def in conf.xpaths.items():
        substitutor = Substitutor(subst_def)
        found_elements = xml.xpath(xpath)
        if found_elements:
            logger.debug('<> Found {0} element(s) for xpath: {1}; Replacing with {2}'.format(len(found_elements), xpath, subst_def))
            for idx, elem in enumerate(found_elements):
                prev = elem.text
                substitutor.substitute_next(elem)
                if conf.comments:
                    # Configuration parameter allows to add comments informing, which XML elements have been processed by this program.
                    if prev == elem.text:
                        # Generators may sometimes return the same value, e.g. if an invalid IBAN is passed to iban_regenerate
                        # We don't need to obfuscate invalid values, but someone may still want to test it, therefore leaving unmodified
                        # Note, that this happens only for such situations, if an exception is thrown, the script will be stopped.
                        _append_comment_before(elem, 'Cannot obfuscate, leaving unmodified. See logs.')
                    else:
                        _append_comment_before(elem, 'Obfuscated')
                logger.debug('<> Replaced element {0} with: {1}'.format(idx, elem.text))
        else:
            logger.debug('No elements found for xpath: ' + xpath + ', ignoring...')


def _escape_special_params(elem, gen_param: str) -> str:
    """
    Handles special parameters in a generator expression:
        - #text : current element text
        - #len : current element text length
        - ## : # sing
    :param elem: XML element
    :param gen_param: unprocessed generator expression
    :return: processed generator expression
    """
    if gen_param == '#text':
        return elem.text
    elif gen_param == '#len':
        return str(len(elem.text))
    elif gen_param.startswith("##"):
        return gen_param[1:]
    else:
        return gen_param


class Substitutor:
    """
    Class performing the value substitution.
    Contains cache, so generator expressions with SubstGenPolicy.CACHED will not be generated twice.
    """

    def __init__(self, sd: SubstitutionDef):
        self.sd = sd
        self.cache = {}

    def substitute_next(self, elem):
        elem.text = self.get_next(elem)

    def get_next(self, elem) -> str:
        if self.sd.policy == SubstGenPolicy.CACHED and elem.text in self.cache:
            return self.cache[elem.text]
        else:
            gen_value = self.sd.gen_value
            gen_params = gen_value.split()
            final_gen_params = list(map(lambda par: _escape_special_params(elem, par), gen_params))
            new_value = generators.generate(final_gen_params)
            self.cache[elem.text] = new_value
            return new_value


def _append_element_before(elem, new_elem):
    parent = elem.getparent()
    new_elem.tail = elem.tail
    parent.insert(parent.index(elem), new_elem)


def _append_comment_before(elem, text: str):
    comment = etree.Comment(text)
    _append_element_before(elem, comment)


def __extract_xmls_from_file(filename: str) -> list:
    """
    Reads a given file and extract all XML-s from it by <?xml... declaration.
    Used to support inputs, which may contain multiple XML-s in a single file.

    :param filename: input file name
    :return: read files as list of byte arrays.
    """
    result = []
    with open(filename, 'r+b') as file:
        content = file.read()
    startidx = 0
    while True:
        nextidx = content.find(b'<?xml', startidx + 1)
        if nextidx >= 0:
            result.append(content[startidx:nextidx])
            startidx = nextidx
        else:
            result.append(content[startidx:])
            break
    return result
