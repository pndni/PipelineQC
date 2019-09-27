import io
import json
from pathlib import Path
import re
import jsonschema
from pkg_resources import resource_filename


class InvalidFormatError(Exception):
    pass


def load_config(conffile):
    if not isinstance(conffile, io.TextIOBase):
        with open(conffile, 'r') as fconf:
            conf = json.load(fconf)
    else:
        conf = json.load(conffile)
    schema = json.loads(Path(resource_filename('PipelineQC', 'schema/config.json')).read_text())
    jsonschema.validate(conf, schema)
    return conf


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
