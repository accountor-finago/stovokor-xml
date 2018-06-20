"""
File contains method for handling bank account numbers.

See:
https://en.wikipedia.org/wiki/International_Bank_Account_Number
https://www.ecbs.org/iban.htm
"""
import logging
import re

from schwifty import IBAN, registry
from schwifty.iban import code_length

from util import randomization

__author__ = 'michal.toporowski'

logger = logging.getLogger(__name__)


def regenerate_iban(old_iban: str) -> str:
    """
    Regenerates an IBAN number (replaces the account number, while keeping the country and bank part)
    :param old_iban: old IBAN number
    :return: new iban as string
    """
    try:
        iban = IBAN(old_iban)
    except ValueError as e:
        logger.warning('Old IBAN is invalid, leaving it unmodified. IBAN: {0}, error: {1}'.format(old_iban, e))
        return old_iban
    return __get_country_generator(iban.country_code).regenerate_iban(iban).compact


def generate_random_iban(country: str) -> str:
    """
    Generates a random iban for a given country.
    Note, that a random bank code may not belong to any bank. If you want to regenerate an existing iban, use the regenerate_iban function.
    :param country: 2 letter country code
    :return: generated iban as string.
    """
    generator = __get_country_generator(country)
    iban = generator.generate_iban()
    return iban.compact


def regenerate_bban(country_code: str, old_bban: str) -> str:
    """
    Regenerates an BBAN number (replaces the account number, while keeping the country and bank part)
    :param country_code 2-letter country code
    :param old_bban: old BBAN number
    :return: new bban as string
    """
    return __get_country_generator(country_code).regenerate_bban(old_bban)


class BankNrGenerator:
    """
    Class generating an IBAN number.
    We use schwifty library, which helps in creation of correct IBAN numbers.
    Note, that an account number may be valid according to IBAN standard, but may be still invalid according to the country-specific
    standard. For such cases, country-specific generators should be used (e.g. Finland requires a Luhn control digit at the end)
    """

    def __init__(self, country_code: str, warnings: bool = True) -> None:
        self.country_code = country_code
        self.warnings = warnings

    def generate_account_part(self, bank_code: str) -> str:
        """
        Generates a random account number.
        This generates just a random number with length taken from the IBAN standard for the given country.
        Note, that some countries may have some own restrictions.
        :param bank_code: the bank code part of IBAN.
        :return: the account number part of IBAN (without country or bank code)
        """
        if self.warnings:
            logger.warning(
                "No dedicated implementation for country {0}. We will generate a number, which is a correct IBAN, but not necessarily a "
                "correct country-specific number".format(self.country_code))
        length = self._get_account_code_length()
        return randomization.random_numeric(length)

    def generate_iban_for_bank(self, bank_code: str) -> IBAN:
        """
        Generates an iban for given bank code.
        :param bank_code: bank code
        :return: IBAN object
        """
        try:
            return IBAN.generate(self.country_code, bank_code, self.generate_account_part(bank_code))
        except ValueError as e:
            raise Exception('We generated an invalid IBAN. '
                            'This means, that probably there is a bug in the mechanism generating IBAN or the library we use. Error: {0}'
                            .format(e))

    def generate_iban(self) -> IBAN:
        """
        Generates a random iban with random bank code and random account number.
        Note, that a random bank code may not belong to any bank. If you know the bank, use generate_iban_for_bank method.
        :return: IBAN object
        """
        bank_code = randomization.random_numeric(self._get_bank_code_length())
        return self.generate_iban_for_bank(bank_code)

    def regenerate_iban(self, old_iban: IBAN) -> IBAN:
        """
        Regenerates an IBAN number (replaces the account number, while keeping the country and bank part)
        :param old_iban: old IBAN number, should be valid and belong to the appropriate country
        :return: new iban
        """
        return self.generate_iban_for_bank(old_iban.bank_code + old_iban.branch_code)

    def regenerate_bban(self, old_bban: str) -> str:
        """
        Regenerates an BBAN number (replaces the account number, while keeping the country and bank part)
        :param old_bban: old BBAN number
        :return: new bban as string
        """
        try:
            iban = self.bban_to_iban(old_bban)
        except ValueError as e:
            logger.warning(
                'Old BBAN is invalid, leaving it unmodified. BBAN: {0}, country: {1}, error: {2}'.format(old_bban, self.country_code, e))
            return old_bban
        return self.iban_to_bban(self.regenerate_iban(iban))

    def bban_to_iban(self, bban: str) -> IBAN:
        return IBAN(self.country_code + '??' + bban)

    def iban_to_bban(self, iban: IBAN) -> str:
        return iban.bban

    def _get_account_code_length(self) -> int:
        return code_length(self.__get_spec(), 'account_code')

    def _get_bank_code_length(self) -> int:
        spec = self.__get_spec()
        bank_code_length = code_length(spec, 'bank_code')
        branch_code_length = code_length(spec, 'branch_code')
        return bank_code_length + branch_code_length

    def __get_spec(self) -> str:
        return registry.get('iban')[self.country_code]


class BankNrGeneratorFI(BankNrGenerator):
    """
    Generator for Finnish bank accounts.
    The last digit is Luhn checksum.
    See:
    https://fi.wikipedia.org/wiki/Tilinumero
    https://fi.wikipedia.org/wiki/Luhnin_algoritmi

    """

    def __init__(self) -> None:
        super().__init__('FI', False)

    def generate_account_part(self, bank_code: str) -> str:
        random_part = randomization.random_numeric(7)
        control_digit = luhn_checksum(bank_code + random_part)
        return random_part + str(control_digit)


def luhn_checksum(card_number) -> int:
    def digits_of(n):
        return [int(d) for d in str(n)]

    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10


class BankNrGeneratorNO(BankNrGenerator):
    """
    Generator for Norwegian bank accounts.
    The last digit is MOD11 checksum.
    See:
    https://no.wikipedia.org/wiki/Kontonummer
    https://no.wikipedia.org/wiki/MOD11
    :return:
    """

    def __init__(self) -> None:
        super().__init__('NO', False)

    def generate_account_part(self, bank_code: str):
        random_part = randomization.random_numeric(6)
        control_digit = kid_mod11(bank_code + random_part)
        if control_digit == 10:
            # 10 not allowed
            return self.generate_account_part(bank_code)
        # logging.info('Generated: random part {0}. control digit: {1}'.format(random_part, control_digit))
        return random_part + str(control_digit)


def kid_mod11(a) -> int:
    cross = sum([int(val) * [2, 3, 4, 5, 6, 7][idx % 6] for idx, val in enumerate(list(str(a))[::-1])])
    mod = 11 - (cross % 11)
    return mod if mod != 11 else 0


class BankNrGeneratorIT(BankNrGenerator):
    """
    Generator for Italian bank accounts.
    Unlike most IBAN-s, they should have a control character (CIN) before bank code and account number.
    """

    def __init__(self):
        super().__init__('IT', False)

    def generate_iban_for_bank(self, bank_code: str):
        accnum = self.generate_account_part(bank_code)
        cin_digit = cin(accnum + bank_code)
        return IBAN('IT??' + cin_digit + bank_code + accnum)


CIN_ODD_VALUE = [1, 0, 5, 7, 9, 13, 15, 17, 19, 21, 2, 4, 18, 20, 11, 3, 6, 8, 12, 14, 16, 10, 22, 25, 24, 23, 27, 28, 26]


def cin(code: str) -> chr:
    total = 0
    for i, c in enumerate(code):
        # Assuming c is a number - CIN works also for letters, but we don't need it here.
        if i % 2 == 0:
            # Even - just add number
            total += int(c)
        else:
            # Odd - special value from table
            total += CIN_ODD_VALUE[int(c)]
    # Count mod 26
    mod = total % 26
    # return the corresponding letter
    return chr(65 + mod)


STANDARD_BBAN_PART_LENGTH_SE = 20


class BankNrGeneratorSE(BankNrGenerator):
    """
    Swedish IBAN:s look pretty standard with 20 numbers (bank code + account number).
    However the BBAN:s may have various lengths and the BBAN -> IBAN conversion depends on the bank

    According to https://sv.wikipedia.org/wiki/International_Bank_Account_Number
    Bank 	Kontonummer 	BIC-kod 	IBAN
    Danske bank 	1bbb-aaa aaaa aaaa 	DABASESX 	SEkk 1200 0000 0aaa aaaa aaaa
    Nordea 	3bbb-aaa aaaa aaaa 	NDEASESS 	SEkk 3000 0000 0aaa aaaa aaaa
    ICA-banken 	927b-aaa aaaa 	IBCASES1 	SEkk 9270 0000 0927 baaa aaaa
    SEB 	5bbb-aaa aaaa 	ESSESESS 	SEkk 5000 0000 05bb baaa aaaa
    Handelsbanken 	6bbb-aaaaa aaaa 	HANDSESS 	SEkk 6000 0000 000a aaaa aaaa
    Swedbank 	7bbb-aaaaaaa 	SWEDSESS 	SEkk 8000 0000 07bb baaa aaaa
    Swedbank 	8bbbb,aa aaaa aaaa 	SWEDSESS 	SEkk 8000 08bb bbaa aaaa aaaa
    Plusgirot 	aaaaaaa-a 	NDEASESS 	SEkk 9500 0099 60nn aaaa aaaa
    """

    bban_to_iban_regex = {
        # Danske
        '^1(\d{3})(\d{11})$': '1200' + '0000' + '0' + '\\2',
        # Nordea
        '^3(\d{3})(\d{11})$': '3000' + '0000' + '0' + '\\2',
        # ICA
        '^927(\d{1})(\d{7})$': '9270' + '0000' + '0927' + '\\1\\2',
        # SEB
        '^5(\d{3})(\d{7})$': '5000' + '0000' + '05' + '\\1\\2',
        # Handelsbanken
        '^6(\d{3})(\d{9})$': '6000' + '0000' + '000' + '\\2',
        # Swedbank
        '^7(\d{3})(\d{7})$': '8000' + '0000' + '07' + '\\1\\2',
        # also Swedbank
        '^8(\d{4})(\d{10})$': '8000' + '08' + '\\1\\2',
        # Plusgiro
        '^(\d{9})$': '9500' + '0099' + '6000' + '\\1'
    }

    iban_to_bban_regex = {
        # Danske
        '^1200' + '0000' + '0' + '(\d{11})$': '^1000\\1',
        # Nordea
        '^3000' + '0000' + '0' + '(\d{11})$': '^3000\\1',
        # ICA
        '^9270' + '0000' + '0927' + '(\d)(\d{7})$': '927\\1\\2',
        # SEB
        '^5000' + '0000' + '05' + '(\d{3})(\d{7})$': '5\\1\\2',
        # Handelsbanken
        '^6000' + '0000' + '000' + '(\d{9})$': '^6000\\1',
        # Swedbank
        '^8000' + '0000' + '07' + '(\d{3})(\d{7})$': '7\\1\\2',
        # also Swedbank
        '^8000' + '08' + '(\d{4})(\d{10})$': '8\\1\\2',
        # Plusgiro
        '^9500' + '0099' + '60' + '(\d{2})(\d{9})$': '\\2'
    }

    def __init__(self) -> None:
        super().__init__('SE', False)
        self.special_bankcode_iban = None
        self.special_bankcode_bban = None

    def regenerate_iban(self, old_iban: IBAN) -> IBAN:
        # Invoke to bban to check for special handling
        self.iban_to_bban(old_iban)
        if self.special_bankcode_iban:
            # Special bank-specific handling
            try:
                accnum = randomization.random_numeric(STANDARD_BBAN_PART_LENGTH_SE - len(self.special_bankcode_iban))
                return IBAN('SE??' + self.special_bankcode_iban + accnum)
            except ValueError as e:
                raise Exception('We generated an invalid IBAN. '
                                'This means, that probably there is a bug in the mechanism generating IBAN or the library we use. Error: '
                                '{0} '
                                .format(e))
        else:
            # Standard IBAN handling
            return super().regenerate_iban(old_iban)

    def bban_to_iban(self, bban: str) -> IBAN:
        bban_iban_part = self.__bban_to_iban_part(bban)
        return super().bban_to_iban(bban_iban_part)

    def iban_to_bban(self, iban: IBAN) -> str:
        bban_iban_part = super().iban_to_bban(iban)
        return self.__iban_part_to_bban(bban_iban_part)

    def __bban_to_iban_part(self, bban: str) -> str:
        """
        Finds if a bban is special and sets special_bankcode if so
        :param bban: national Swedish BBAN, may have various lengths
        :return: the bban modified for IBAN (should have length 20 always)
        """
        if self.special_bankcode_bban and self.special_bankcode_iban:
            # Already calculated
            return self.special_bankcode_iban + bban[len(self.special_bankcode_bban):]

        if len(bban) == STANDARD_BBAN_PART_LENGTH_SE:
            # Standard bban, nothing special
            return bban

        # Find if the BBAN has a special bank-specific conversion
        for special_bban_regex, substitution in self.bban_to_iban_regex.items():
            match = re.match(special_bban_regex, bban)
            if match:
                bban_as_iban_part = match.expand(substitution)
                accnum = match.groups()[-1]
                accnum_len = len(accnum)
                self.special_bankcode_bban = bban[:-accnum_len]
                self.special_bankcode_iban = bban_as_iban_part[:(STANDARD_BBAN_PART_LENGTH_SE - accnum_len)]
                logger.debug('Processing a Swedish BBAN with non-standard length. Special bank part: {0}, accnum len: {1}'
                             .format(self.special_bankcode_iban, accnum_len))
                return bban_as_iban_part

        logger.warning('Unrecognized Swedish BBAN format: ' + bban)
        return bban

    def __iban_part_to_bban(self, bban_iban_part: str) -> str:
        """
        Finds if a bban part of an iban is special and sets special_bankcode if so
        :param bban_iban_part: bban part of an iban, should have length 20 always
        """
        if self.special_bankcode_bban and self.special_bankcode_iban:
            # Already set
            return self.special_bankcode_bban + bban_iban_part[len(self.special_bankcode_iban):]

        # Find if the IBAN has a special bank-specific conversion
        for special_iban_regex, substitution in self.iban_to_bban_regex.items():
            match = re.match(special_iban_regex, bban_iban_part)
            if match:
                bban = match.expand(substitution)
                accnum = match.groups()[-1]
                accnum_len = len(accnum)
                self.special_bankcode_bban = bban[:-accnum_len]
                self.special_bankcode_iban = bban_iban_part[:(STANDARD_BBAN_PART_LENGTH_SE - accnum_len)]
                logger.debug('Processing a special Swedish IBAN. Special bank part: {0}, accnum len: {1}'
                             .format(self.special_bankcode_iban, accnum_len))
                return bban

        # No special handling, standard conversion
        return bban_iban_part


COUNTRY_GENERATORS = {
    'FI': lambda: BankNrGeneratorFI(),
    'NO': lambda: BankNrGeneratorNO(),
    'SE': lambda: BankNrGeneratorSE(),
    # Denmark doesn't seem to have anything special, so use the default without warnings
    'DK': lambda: BankNrGenerator('DK', warnings=False),
    'IT': lambda: BankNrGeneratorIT()
}


def __get_country_generator(country: str) -> BankNrGenerator:
    if len(country) != 2:
        raise ValueError("Country code must have 2 letters")
    return COUNTRY_GENERATORS.get(country, lambda: BankNrGenerator(country))()
