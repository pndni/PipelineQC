from pathlib import Path
from collections import defaultdict, namedtuple
import re
from functools import lru_cache
import os
from bids import layout
import json

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
        if isinstance(pattern, list):
            # bids
            continue
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
        errstr += 'Matching file names: {}. '.format(', '.join(
            (outmatch.name for outmatch in out)))
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


def _search_types(conf):
    bids_p = False
    re_p = False
    bids_patterns = {
        pk
        for pk, pv in conf['patterns'].items() if isinstance(pv, list)
    }
    re_patterns = {
        pk
        for pk, pv in conf['patterns'].items() if isinstance(pv, str)
    }
    for f in conf['files'].values():
        if f['pattern'] in bids_patterns:
            bids_p = True
        elif f['pattern'] in re_patterns:
            re_p = True
        else:
            raise RuntimeError(f"{f['pattern']} not specified")
        if bids_p and re_p:
            break
    return bids_p, re_p


def _matches_exclude_pattern(fname, exclude_patterns):
    for excl in exclude_patterns:
        if re.search(excl, fname):
            return True
    return False


def get_files(dirs, conf, bids_validate=False, exclude_patterns=None):
    if exclude_patterns is None:
        exclude_patterns = []
    out = defaultdict(dict)
    bids_search, re_search = _search_types(conf)
    matched_files = set()
    if re_search:
        for d in dirs:
            dfull = d.resolve()
            for fname in Path(dfull).glob('**/*'):
                if not fname.is_file():
                    continue
                if _matches_exclude_pattern(str(fname), exclude_patterns):
                    continue
                parse_result = parse_file(strip_common(fname, dfull), conf)
                if parse_result is not None:
                    matched_files.add(fname)
                    if conf['files'][parse_result.name].get(
                            'allow_multiple', False):
                        if parse_result.name not in out[parse_result.page_key]:
                            out[parse_result.page_key][parse_result.name] = []
                        out[parse_result.page_key][parse_result.name].append(
                            fname)
                    else:
                        if parse_result.name in out[parse_result.page_key]:
                            raise MultipleFilesFoundError(
                                'Multiple files found for {} with key {}'.
                                format(parse_result.name,
                                       parse_result.page_key))
                        out[parse_result.page_key][parse_result.name] = fname
    if bids_search:
        bids_layouts = _get_bids_layouts(dirs, conf, validate=bids_validate)
        for file_key, file_params in conf['files'].items():
            pattern = file_params['pattern']
            if not isinstance(conf['patterns'][pattern], list):
                continue
            for bl in bids_layouts[pattern]:
                for match in bl.get(**file_params['filter']):
                    fnamefull = Path(match.path)
                    if _matches_exclude_pattern(str(fnamefull),
                                                exclude_patterns):
                        continue
                    if fnamefull in matched_files:
                        raise MultipleFilterResultsError(
                            f'{fnamefull} matched multiple filters')
                    matched_files.add(fnamefull)
                    if file_params.get('global', False):
                        page_key = 'global'
                    else:
                        page_key = tuple((_str_or_none(match.entities.get(pk))
                                          for pk in conf['page_keys']))
                    if file_params.get('allow_multiple', False):
                        if file_key not in out[page_key]:
                            out[page_key][file_key] = []
                        out[page_key][file_key].append(fnamefull)
                    else:
                        if file_key in out[page_key]:
                            raise MultipleFilesFoundError(
                                'Multiple files found for {} with key {}'.
                                format(file_key, page_key))
                        out[page_key][file_key] = fnamefull
    out = dict(out)
    if 'global' not in out:
        out['global'] = {}
    return out


def _str_or_none(x):
    if x is None:
        return None
    return str(x)


def _get_bids_layouts(dirs, conf, validate=False):
    bids_layouts = {}
    for pattern_key, pattern_val in conf['patterns'].items():
        if isinstance(pattern_val, str):
            continue
        bids_layouts[pattern_key] = [
            layout.BIDSLayout(dir_, config=pattern_val, validate=validate)
            for dir_ in dirs
        ]
    return bids_layouts


def filedictmap(func, filedict):
    """
    map func to each filename/Path in filedict
    """
    out = {}
    for k1 in list(filedict.keys()):
        out[k1] = {}
        for k2 in list(filedict[k1].keys()):
            if isinstance(filedict[k1][k2], list):
                out[k1][k2] = list(map(func, filedict[k1][k2]))
            else:
                out[k1][k2] = func(filedict[k1][k2])
    return out


def _convert_to_str(x):
    assert isinstance(x, Path)
    return str(x)


def _convert_to_path(x):
    assert isinstance(x, str)
    return Path(x)


def filedict_to_json(filedict, output_file):
    outdict = filedictmap(_convert_to_str, filedict)
    outdict2 = {'filedict': {}, 'keymap': {}}
    for i, (k, v) in enumerate(outdict.items()):
        outdict2['filedict'][i] = v
        if isinstance(k, tuple):
            outdict2['keymap'][i] = list(k)
        else:
            outdict2['keymap'][i] = k
    with open(output_file, 'w') as f:
        json.dump(outdict2, f, indent=4)


def json_to_filedict(input_file):
    outdict = {}
    with open(input_file, 'r') as f:
        indict = json.load(f)
    for i in indict['filedict'].keys():
        if isinstance(indict['keymap'][i], list):
            k = tuple(indict['keymap'][i])
        else:
            k = indict['keymap'][i]
        outdict[k] = indict['filedict'][i]
    outdict2 = filedictmap(_convert_to_path, outdict)
    return outdict2
