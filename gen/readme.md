# Generators

Tool for generating random values.

## Running

##### Calling from Python code:
```
from gen import generators
generators.generate(<generator parameters as list>)
# Example:
generators.generate(['alphanum', 'l', '13'])
```
The `generate` function will return the generated value as a string.

##### Executing as  a standalone script (from main folder)

```
python3 -m gen.generators <generator expression>
# Example:
python3 -m gen.generators alphanum -l 13
```
The generated value will be printed to the standard output.

## Functionalities

Following generator types are supported:
```
    const               generates a constant value
    alphanum            generates an alphanumeric string
    num                 generates a number
    iban_regenerate     replaces account in an iban number keeping the country
                        and bank
    iban_random         generates a random IBAN. Note, that the bank account
                        may not be valid, use iban_regenerate if you want only
                        to obfuscate an existing iban.
    bban_regenerate     replaces account in an bban number keeping the country
                        and bank
    namelike            generates a random "name-like" string (two capitalized
                        words with random letters)
    name_regenerate     replaces all letters in a name with random ones
    klingon             a random Klingon quote
```
See `gen.generators -h` for more information and `gen.generators <generator_type> -h` for detailed information about the given generator type.


## Bank accounts generation

The generators `iban_regenerate`, `iban_random` and `bban_regenerate` can generate random bank account numbers.

In general, the tool is able to generate any country IBAN, which will be valid according to the IBAN specifications.

However, some countries may have their own additional bank account rules, so the generated IBAN may not necessary be valid according to the country-specific rules.
Also bear in mind, that if you are using `iban_random` the generated bank part may not belong to any real bank.

Explicit support has been added for several countries:
* Finland
  * Luhn checksum support.
* Norway
  * MOD11 checksum support.
* Italy
  * Control character (CIN) support.
* Sweden
  * Several bank-specific formats supported (Danske, Nordea, ICA, SEB, Handelsbanken, Swedbank, Plusgiro)
  * Other bank accounts may be treated as invalid
  
#### Invalid bank accounts
If the input bank account to be regenerated is invalid (or not supported), the tool returns the input unmodified.