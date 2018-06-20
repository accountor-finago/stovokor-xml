**Sto-vo-kor** - a tool for replacing values in XML files.

Example use cases:
* obfuscating production files to allow developers use production data without compromising the customers' privacy
* replacing arbitrary values in files for testing

The project has been named after the Klingon afterlife, as it may give a second life to the old XML files.

Original creator: \
Michał Toporowski, Accountor Finago Oy

## Requirements
You will need :
* Python 3.x 
* the required packages. \
Installation:
`pip install -r requirements.txt`

Used libraries:
* LXML: http://lxml.de
* Schwifty: https://pythonhosted.org/schwifty/


## Usage
```
python3 sto_vo_kor.py [-h] -i INPUT [-o OUTPUT] -c CONF [--override OVERRIDE]
```

* `-i`: input file or directory \
    If the input is a directory, all files from the given directory are processed
* `-o`: output file or directory (optional) \
    If not specified, the output will be stored in `<input_file>.out.xml` if the input is a file or `<input_dir>.out/` if input is a directory.
* `-c`: configuration file (see Configuration section)

Check ```python3 sto_vo_kor.py -h``` for documentation on options.
 
 
## Configuration
Configuration is read from a JSON file.

Format:
```
{
    "predef": {
        "<predefined_generator_name>": "<generator expression>"
      },
    "xpaths": {
        "/some/xpath/for/element/to/be/replaced": "<generator expression>",
        "//*[name()='AnotherXpath']": "<generator expression>",
        "/some/xpath/foo/bar": {
            "predef". "<predefined_generator_name>"
        },
        "/xpath/for/value/that/should/be/cached": {
            "gen_value": "<generator expression>",
            "policy": "cached"
         }
    },
    "conf" : {
        "comments": true,
        "multiple_xmls_in_file": true
    }
}

``` 
* **XPaths** are evaluated the standard way according to the XPath specification. 
* A **Generator expression** is an expression accepted by the Generator module (`gen.generators`), e.g. `num --min 1 --max 14` or `iban_regenerate <some_iban>`. \
See `gen/readme.md` for more options. 
    * Supported placeholders in generator expressions:
      * `#text` - old XML element text
      * `#len` - old XML element length
      * `##` - hash sign
* `comments` parameter specifies, whether additional comments are to be placed in the output files:
    * `<!--Obfuscated-->` before each converted element
    * `<!--Cannot obfuscate, leaving unmodified. See logs.-->` before each element failed to convert (i.e. when the generator returned the input value). 
* `multiple_xmls_in_file` parameter enables the support of files containing multiple XML document.
    * If `true`, such files will be split by XML header (`<?xml(...)?>`), parsed separately and joined in the end.

## Example
Input file:
```
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Document>
    <foo>
        <!-- Some data to be replaced -->
        <author>
            <name>Very Secret Name</name>
            <personalId>123456</personalId>
        </author>
        <customers>
            <customer>
                <name>Jean-Luc Picard</name>
                <personalId>1234567</personalId>
                <bankAccount>FI10 4725 0961 0005 73</bankAccount>
                <motto>To boldly go, where no one has gone before</motto>
            </customer>
            <customer>
                <name>Worf</name>
                <personalId>1234568</personalId>
                <bankAccount>FI3647763216000644</bankAccount>
                <motto>Qapla'</motto>
            </customer>
        </customers>
        <!-- Some data to be kept -->
        <bar>
            <doNotChange>Some values, which should not be changed</doNotChange>
            <localizations>
                <!-- To check, that special chars will not be broken -->
                <localization lang="FI">Joku hyvin tärkeä teksti suomeksi</localization>
                <localization lang="PL">Jakiś bardzo ważny tekst po polsku</localization>
            </localizations>
        </bar>
    </foo>
</Document>
```
Configuration:
```
{
  "predef": {
    "iban": {
      "gen_value": "iban_regenerate #text",
      "policy": "cached"
    }
  },
  "xpaths": {
    "/*[name()='Document']/*[local-name()='foo']/*[name()='author']/*[local-name()='name']": "name_regenerate #text",
    "//*[name()='personalId']": "num -l #len",
    "/*[name()='Document']/*[local-name()='foo']/*[name()='customers']/*[name()='customer']/*[local-name()='name']": "name_regenerate #text",
    "/*[name()='Document']/*[local-name()='foo']/*[name()='customers']/*[name()='customer']/*[name()='bankAccount']": {
      "predef": "iban"
    }
  },
  "conf": {
    "comments": false,
    "multiple_xmls_in_file": true
  }
}
```
Example output (the generators are randomization-based, so the output may differ every time)
```
<?xml version='1.0' encoding='utf-8'?>
<Document>
	<foo>
		<!-- Some data to be replaced -->
		<author>
			<name>Idga Wupliq Rwoh</name>
			<personalId>553308</personalId>
		</author>
		<customers>
			<customer>
				<name>Sdahdfia Mgfxoo</name>
				<personalId>3510159</personalId>
				<bankAccount>FI0847200035286883</bankAccount>
				<motto>To boldly go, where no one has gone before</motto>
			</customer>
			<customer>
				<name>Izat</name>
				<personalId>1438623</personalId>
				<bankAccount>FI8447700049683782</bankAccount>
				<motto>Qapla'</motto>
			</customer>
		</customers>
		<!-- Some data to be kept -->
		<bar>
			<doNotChange>Some values, which should not be changed</doNotChange>
			<localizations>
				<!-- To check, that special chars will not be broken -->
				<localization lang="FI">Joku hyvin tärkeä teksti suomeksi</localization>
				<localization lang="PL">Jakiś bardzo ważny tekst po polsku</localization>
			</localizations>
		</bar>
	</foo>
</Document>
```

## FAQ

**What are the differences between this tool and other popular XML processing mechanisms, e.g. XSLT?**

XSLT is a generic mechanism for processing any XML documents.

This project has a more narrow use case - it replaces the content of XML elements while leaving the document structure unmodified. \
On the other hand, it provides several features useful for this purpose, e.g. replacing the values with random strings, numbers, "personal names" or bank accounts.


**What about bank account number replacing, what accounts are supported?**

The account numbers generated by IBAN generators are valid according to the general IBAN specification. \
However, some countries and banks may have additional custom restrictions, which may not be fully supported. \
See `gen/readme.md` for more information.

**What is the development process of this project?**

The project was created in 2017-2018 for Procountor development and operations teams. \
It isn't currently actively developed, however if you have some improvement suggestions or find an issue, feel free to contact us.

#### Disclaimer
Please note, that when using this tool to obfuscate sensitive data, one should always verify, that the output does not contain them. 
For example, an incorrect XPath in the configuration or a non-supported bank account format in the input may result in leaving the original value unmodified.

Accountor Finago and the authors do not take responsibility for possible breaches caused by passing output of this tool to unauthorized persons.