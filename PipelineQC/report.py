from nipype.pipeline import engine as pe
from nipype import Merge
from pndniworkflows.interfaces.reports import (ReportletSingle,
                                               ReportletContour,
                                               ReportletCompare,
                                               ReportletDistributions,
                                               ReportletCrash,
                                               AssembleReport,
                                               IndexReport)
from pathlib import Path

from .configure import format_output


class InvalidReportletTypeError(Exception):
    pass


def report_workflow(page_dict, page_key, conf, global_dict, output_dir):
    out_file = Path(output_dir).resolve() / format_output(conf, page_key)
    out_file.parent.mkdir(exist_ok=True, parents=True)
    title = '_'.join((f'{k}-{v}' for k, v in zip(conf['page_keys'], page_key) if v is not None))
    wf = pe.Workflow('page_' + title)
    reportlets = pe.Node(Merge(len(conf['reportlets'])), 'reportlets')
    for reportletnum, rpspec in enumerate(conf['reportlets'], start=1):
        if rpspec['type'] == 'single':
            node = pe.Node(ReportletSingle(), f'single{reportletnum}')
        elif rpspec['type'] == 'contour':
            node = pe.Node(ReportletContour(), f'contour{reportletnum}')
        elif rpspec['type'] == 'compare':
            node = pe.Node(ReportletCompare(), f'compare{reportletnum}')
        elif rpspec['type'] == 'distributions':
            node = pe.Node(ReportletDistributions(), f'distributions{reportletnum}')
        elif rpspec['type'] == 'crash':
            node = pe.Node(ReportletCrash(), f'crash{reportletnum}')
        else:
            raise InvalidReportletTypeError(f'{rpspec["type"]} is not a recognized reportlet')
        for rpkey, rpval in rpspec.items():
            if rpkey == 'type':
                continue
            elif rpkey in ['image', 'image1', 'image2', 'labelimage', 'distsfile', 'labelfile', 'crashfiles']:
                if conf['files'][rpval].get('allow_multiple', False):
                    no_entry_val = []
                else:
                    no_entry_val = None
                if conf['files'][rpval].get('global', False):
                    setattr(node.inputs, rpkey, global_dict.get(rpval, no_entry_val))
                else:
                    setattr(node.inputs, rpkey, page_dict.get(rpval, no_entry_val))
            else:
                setattr(node.inputs, rpkey, rpval)
        node.inputs.relative_dir = out_file.parent
        wf.connect(node, 'out_file', reportlets, f'in{reportletnum}')
    assemble_node = pe.Node(AssembleReport(), 'assemble')
    assemble_node.inputs.title = title
    assemble_node.inputs.out_file = out_file
    wf.connect(reportlets, 'out', assemble_node, 'in_files')
    return wf


def all_workflow(file_dict, output_dir, conf):
    wf = pe.Workflow('report')
    merge_pages = pe.Node(Merge(len(file_dict)), 'merge_pages')
    page_key_set = set(file_dict.keys()) - {'global'}
    for i, page_key in enumerate(page_key_set, start=1):
        page_wf = report_workflow(file_dict[page_key], page_key, conf, file_dict['global'], output_dir)
        wf.connect(page_wf, 'assemble.out_file', merge_pages, f'in{i}')
    index_pages = pe.Node(IndexReport(), 'index_pages')
    out_file = Path(output_dir).resolve() / conf['index_filename']
    out_file.parent.mkdir(exist_ok=True, parents=True)
    index_pages.inputs.out_file = out_file
    wf.connect(merge_pages, 'out', index_pages, 'in_files')
    return wf
