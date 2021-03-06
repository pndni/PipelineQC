from nipype.pipeline import engine as pe
from nipype import Merge
from .interfaces import (Single,
                         Contour,
                         Overlay,
                         ProbMap,
                         Compare,
                         Distributions,
                         Crash,
                         Rating,
                         AssembleReport,
                         IndexReport)
from pathlib import Path

from .configure import format_output


class InvalidReportletTypeError(Exception):
    pass


def report_workflow(page_dict,
                    page_key,
                    conf,
                    global_dict,
                    out_file,
                    next_=None,
                    prev=None):
    out_file.parent.mkdir(exist_ok=True, parents=True)
    title = '_'.join((f'{k}-{v}' for k,
                      v in zip(conf['page_keys'], page_key) if v is not None))
    wf = pe.Workflow('page_' + title)
    reportlets = pe.Node(Merge(len(conf['reportlets'])), 'reportlets')
    for reportletnum, rpspec in enumerate(conf['reportlets'], start=1):
        if rpspec['type'] == 'single':
            node = pe.Node(Single(), f'single{reportletnum}')
        elif rpspec['type'] == 'contour':
            node = pe.Node(Contour(), f'contour{reportletnum}')
        elif rpspec['type'] == 'overlay':
            node = pe.Node(Overlay(), f'overlay{reportletnum}')
        elif rpspec['type'] == 'probmap':
            node = pe.Node(ProbMap(), f'probmap{reportletnum}')
        elif rpspec['type'] == 'compare':
            node = pe.Node(Compare(), f'compare{reportletnum}')
        elif rpspec['type'] == 'distributions':
            node = pe.Node(Distributions(), f'distributions{reportletnum}')
        elif rpspec['type'] == 'crash':
            node = pe.Node(Crash(), f'crash{reportletnum}')
        elif rpspec['type'] == 'rating':
            node = pe.Node(Rating(), f'rating{reportletnum}')
        else:
            raise InvalidReportletTypeError(
                f'{rpspec["type"]} is not a recognized reportlet')
        for rpkey, rpval in rpspec.items():
            if rpkey == 'type':
                continue
            elif rpkey in [
                    'image',
                    'image1',
                    'image2',
                    'labelimage',
                    'probmapimage',
                    'distsfile',
                    'labelfile',
                    'crashfiles'
            ]:
                if conf['files'][rpval].get('allow_multiple', False):
                    no_entry_val = []
                else:
                    no_entry_val = None
                if conf['files'][rpval].get('global', False):
                    setattr(node.inputs,
                            rpkey,
                            global_dict.get(rpval, no_entry_val))
                else:
                    setattr(node.inputs,
                            rpkey,
                            page_dict.get(rpval, no_entry_val))
            else:
                setattr(node.inputs, rpkey, rpval)
        for settings_key, settings_value in conf['global_reportlet_settings'].items():
            if settings_key == 'use_relative_dir':
                settings_node_key = 'relative_dir'
                if settings_value:
                    settings_node_value = out_file.parent
                else:
                    settings_node_value = None
            else:
                settings_node_key = settings_key
                settings_node_value = settings_value
            if (settings_node_key in node.inputs.visible_traits()
                    and settings_node_key not in rpspec):
                setattr(node.inputs, settings_node_key, settings_node_value)
        wf.connect(node, 'out_file', reportlets, f'in{reportletnum}')
    assemble_node = pe.Node(AssembleReport(), 'assemble')
    assemble_node.inputs.title = title
    assemble_node.inputs.out_file = out_file
    if next_ is not None:
        assemble_node.inputs.next_ = next_
    if prev is not None:
        assemble_node.inputs.prev = prev
    assemble_node.inputs.relative_dir = out_file.parent
    wf.connect(reportlets, 'out', assemble_node, 'in_files')
    return wf


def _sort_key(intuple):
    return tuple((str(x) for x in intuple))


def all_workflow(file_dict,
                 output_dir,
                 conf,
                 filter_keys_dict=None,
                 create_index=True):
    if filter_keys_dict is None:
        filter_keys_dict = {}
    wf = pe.Workflow('report')
    merge_pages = pe.Node(Merge(len(file_dict)), 'merge_pages')
    page_key_list = list(file_dict.keys())
    page_key_list.pop(page_key_list.index('global'))
    page_key_list.sort(key=_sort_key)
    out_files = {
        page_key: Path(output_dir).resolve() / format_output(conf, page_key)
        for page_key in page_key_list
    }

    def _inc_page_key(pkl):
        for filter_i, filter_page_key in enumerate(conf['page_keys']):
            if filter_page_key in filter_keys_dict and pkl[
                    filter_i] not in filter_keys_dict[filter_page_key]:
                return False
        return True

    for i, page_key in enumerate(filter(_inc_page_key, page_key_list), start=0):
        next_ = out_files[page_key_list[
            i + 1]] if i + 1 < len(page_key_list) else None
        prev = out_files[page_key_list[i - 1]] if i > 0 else None
        page_wf = report_workflow(file_dict[page_key],
                                  page_key,
                                  conf,
                                  file_dict['global'],
                                  out_files[page_key],
                                  next_=next_,
                                  prev=prev)
        wf.connect(page_wf, 'assemble.out_file', merge_pages, f'in{i + 1}')
    if create_index:
        index_pages = pe.Node(IndexReport(), 'index_pages')
        out_file = Path(output_dir).resolve() / conf['index_filename']
        out_file.parent.mkdir(exist_ok=True, parents=True)
        index_pages.inputs.out_file = out_file
        wf.connect(merge_pages, 'out', index_pages, 'in_files')
    return wf
