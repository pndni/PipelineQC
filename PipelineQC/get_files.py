from pathlib import Path
from collections import defaultdict, namedtuple
import re
from functools import lru_cache
import os


FileMatch = namedtuple('FileMatch', ['name', 'page_key'])


class MultipleFilterResultsError(Exception):
    pass


class MultipleFilesFoundError(Exception):
    pass


@lru_cache(maxsize=16)
def match(pattern, fname):
    return re.match(pattern, fname)


def parse_file(fname, conf):
    out = set()
    for to_match_name, to_match in conf['files'].items():
        pattern = conf['patterns'][to_match['pattern']]
        m = match(pattern, fname)
        if m is None:
            continue
        for filtkey, filtval in to_match['filter'].items():
            if m.group(filtkey) != filtval:
                break
        else:
            if to_match.get('global', False):
                page_key = 'global'
            else:
                page_key = tuple((m.group(k) for k in conf['page_keys']))
            out.add(FileMatch(to_match_name, page_key))
    if len(out) > 1:
        errstr = f'{fname} matches multiple files in configuration file. '
        errstr += 'Matching file names: {}. '.format(', '.join((outmatch.name for outmatch in out)))
        errstr += ' Add more elements to "filter" to uniquely identify files.'
        raise MultipleFilterResultsError(errstr)
    if len(out) == 1:
        return list(out)[0]


def strip_common(fname, basepath):
    pref = os.path.commonprefix([basepath, fname])
    out = str(fname)[len(pref):]
    if out[0] == '/' and len(pref) > 0:
        out = out[1:]
    return out


def get_files(dirs, conf):
    out = defaultdict(dict)
    for d in dirs:
        dfull = d.resolve()
        for fname in Path(dfull).glob('**/*'):
            if not fname.is_file():
                continue
            parse_result = parse_file(strip_common(fname, dfull), conf)
            if parse_result is not None:
                if conf['files'][parse_result.name].get('allow_multiple', False):
                    if parse_result.name not in out[parse_result.page_key]:
                        out[parse_result.page_key][parse_result.name] = []
                    out[parse_result.page_key][parse_result.name].append(fname)
                else:
                    if parse_result.name in out[parse_result.page_key]:
                        raise MultipleFilesFoundError('Multiple files found for {} with key {}'.format(parse_result.name, parse_result.page_key))
                    out[parse_result.page_key][parse_result.name] = fname
    out = dict(out)
    if 'global' not in out:
        out['global'] = {}
    return out
