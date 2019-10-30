from .get_files import get_files, filedict_to_json, json_to_filedict
from .workflows import all_workflow
from .configure import load_config
from . import group
from . import reportlets
from pathlib import Path
import argparse


def qc_all(dirs,
           output_dir,
           configfile,
           plugin='MultiProc',
           plugin_args=None,
           working_directory=None,
           filter_keys_dict=None,
           filedict=None,
           create_index=True,
           **kwargs):
    conf = load_config(configfile)
    if filedict is None:
        filedict = get_files(dirs, conf, **kwargs)
    if len(filedict) == 1:
        raise RuntimeError('No non-global files found!')
    wf = all_workflow(filedict,
                      output_dir,
                      conf,
                      filter_keys_dict=filter_keys_dict,
                      create_index=create_index)
    if working_directory is not None:
        if not Path(working_directory).exists():
            raise FileNotFoundError(f'{working_directory} does not exist')
        wf.base_dir = str(working_directory.resolve())
    if plugin_args is None:
        plugin_args = {}
    wf.run(plugin=plugin, plugin_args=plugin_args)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    qcpages = subparsers.add_parser('qcpages', help='Create QC pages.')
    qcpages.set_defaults(func=run_qcpages)
    qcpages.add_argument(
        'config_file',
        type=argparse.FileType('r'),
        help='JSON configuration file. See the documentation for details',
        metavar='config_file')
    qcpages.add_argument('output_dir',
                         type=Path,
                         help='Output root for QC pages and index file')
    qcpages.add_argument('search_dirs',
                         type=Path,
                         nargs='+',
                         help='Search these directories for files')
    qcpages.add_argument(
        '--nipype_plugin',
        type=str,
        default='MultiProc',
        help='Passed directly to the nipype workflow run method')
    qcpages.add_argument(
        '--working_directory',
        type=Path,
        help='Working directory for nipype workflow (i.e., "base_dir")')
    qcpages.add_argument(
        '--validate_bids',
        action='store_true',
        help='If using bids, whether to validate the bids directories')
    qcpages.add_argument(
        '--exclude',
        action='append',
        help='If a filename matches this pattern (using re.search), '
        'ignore it. May be specified multiple times')
    qcpages.add_argument('--filter_key',
                         type=str,
                         action='append',
                         help='Only make pages for certain values of a key. '
                         'E.g., --filter_key=subject:1:2:10 will only '
                         'create qc pages for subjects 1, 2, and 10.')
    qcpages.add_argument('--files',
                         type=Path,
                         help='JSON file from the running the findfiles '
                         'subcommand')
    qcpages.add_argument('--no_index',
                         action='store_true',
                         help='Do not create an index file')
    combine = subparsers.add_parser(
        'combine',
        help='Combine json QC forms downloaded from QC pages into a TSV file.')
    combine.set_defaults(func=run_combine)
    combine.add_argument('output_file',
                         type=Path,
                         help='Output filename for tsv file')
    combine.add_argument('input_files',
                         type=Path,
                         nargs='+',
                         help='Input json files')
    contours = subparsers.add_parser(
        'image', help='Create an image of a scan and optional contours')
    contours.set_defaults(func=run_image)
    contours.add_argument('output_file', type=Path)
    contours.add_argument('image', type=Path, help='Input image')
    contours.add_argument(
        '--nslices',
        type=int,
        default=7,
        help='The number of slices to display for each anatomical plane.')
    contours.add_argument('--output_type',
                          type=str,
                          help='Output file type',
                          choices=['svg', 'png'],
                          default='svg')
    contours_mo = contours.add_mutually_exclusive_group()
    contours_mo.add_argument('--labelimage',
                             type=Path,
                             help='Label image from which to draw contours')
    contours_mo.add_argument('--probmap', type=Path, help='Probability map')
    findfiles = subparsers.add_parser(
        'findfiles',
        help='Search parse directories for input files based on config. '
        'Performs the first step of the qcpages subcommand, for use '
        'with the --files option')
    findfiles.set_defaults(func=run_findfiles)
    findfiles.add_argument(
        'config_file',
        type=argparse.FileType('r'),
        help='JSON configuration file. See the documentation for details',
        metavar='config_file')
    findfiles.add_argument('output_file', type=Path, help='Output JSON file')
    findfiles.add_argument('search_dirs',
                           type=Path,
                           nargs='+',
                           help='Search these directories for files')
    findfiles.add_argument(
        '--validate_bids',
        action='store_true',
        help='If using bids, whether to validate the bids directories')
    findfiles.add_argument(
        '--exclude',
        action='append',
        help='If a filename matches this pattern (using re.search), '
        'ignore it. May be specified multiple times')
    index = subparsers.add_parser('index', help='Create index file.')
    index.set_defaults(func=run_index)
    index.add_argument('QC_dir',
                       type=Path,
                       help='Directory with QC pages. '
                       'Corresponds to output_dir with the qcpages command')
    index.add_argument('index_filename',
                       type=Path,
                       help='Filename of output index file')
    return parser


def _parse_filter_key_string(fkstr):
    k, v = fkstr.split('=')
    vs = v.split(':')
    return k, vs


def _parse_filter_keys(filter_key_list):
    outtmp = {}
    if filter_key_list is not None:
        for fkstr in filter_key_list:
            k, vs = _parse_filter_key_string(fkstr)
            outtmp[k] = vs
    return outtmp


def run():
    parser = get_parser()
    args = parser.parse_args()
    if 'func' not in args:
        parser.print_help()
        return 1
    args.func(args)


def run_qcpages(args):
    if args.files is None:
        filedict = None
    else:
        filedict = json_to_filedict(args.files)
    qc_all(args.search_dirs,
           args.output_dir,
           args.config_file,
           plugin=args.nipype_plugin,
           working_directory=args.working_directory,
           bids_validate=args.validate_bids,
           exclude_patterns=args.exclude,
           filter_keys_dict=_parse_filter_keys(args.filter_key),
           filedict=filedict,
           create_index=not args.no_index)


def run_combine(args):
    group.make_tsv(args.input_files, args.output_file)


def run_image(args):
    if args.probmap is not None:
        labelfile = args.probmap
        labeldisplay = 'probmap'
    else:
        labelfile = args.labelimage
        labeldisplay = 'contour'
    out = reportlets.imshow_from_files(imagefile=args.image,
                                       nslices=args.nslices,
                                       labelfile=labelfile,
                                       labeldisplay=labeldisplay,
                                       outtype=args.output_type)
    if args.output_type == 'svg':
        args.output_file.write_text(out)
    else:
        args.output_file.write_bytes(out)


def run_findfiles(args):
    conf = load_config(args.config_file)
    filedict = get_files(args.search_dirs,
                         conf,
                         exclude_patterns=args.exclude,
                         bids_validate=args.validate_bids)
    filedict_to_json(filedict, args.output_file)


def run_index(args):
    group.make_index(args.QC_dir, args.index_filename)
