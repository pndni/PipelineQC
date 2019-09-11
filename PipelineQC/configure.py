import json
from pathlib import Path
import re


class InvalidFormatError(Exception):
    pass


def load_config(conffile):
    return json.loads(Path(conffile).read_text())


def format_output(conf, page_key):
    """Inspired by the pybids string specification"""
    if not isinstance(page_key, tuple):
        raise ValueError('page_key must be a tuple')
    pars = {k: v for k, v in zip(conf['page_keys'], page_key)}
    outfmt = conf['page_filename_template']
    pattern = r'\[[^]}{]*\{(' + '|'.join(conf['page_keys']) + r')\}[^]}{]*\]'
    m = re.search(pattern, outfmt)
    while m is not None:
        if pars[m.group(1)] is None:
            substr = ''
        else:
            substr = m.group(0)[1:-1]
            substr = substr.format(**pars)
        outfmt = outfmt[:m.start()] + substr + outfmt[m.end():]
        m = re.search(pattern, outfmt)
    outfmt = outfmt.format(**pars)
    if ']' in outfmt or '[' in outfmt:
        raise InvalidFormatError('Formatted string still contained "]" or "[", indicating a bad template')
    return outfmt
