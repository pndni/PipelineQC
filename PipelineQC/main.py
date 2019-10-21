from .get_files import get_files
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
           **kwargs):
    conf = load_config(configfile)
    filedict = get_files(dirs, conf, **kwargs)
    if len(filedict) == 1:
        raise RuntimeError('No non-global files found!')
    wf = all_workflow(filedict, output_dir, conf, filter_keys=filter_keys_dict)
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
    contours.add_argument('--labelimage',
                          type=Path,
                          help='Label image from which to draw contours')
    contours.add_argument('--output_type',
                          type=str,
                          help='Output file type',
                          choices=['svg', 'png'],
                          default='svg')
    return parser


def _parse_filter_key_string(fkstr):
    k, v = fkstr.split('=')
    vs = v.split(':')
    return k, vs


def _parse_filter_keys(args):
    if len(args.filter_key) == 0:
        args.filter_key_dict = None
    else:
        outtmp = {}
        for fkstr in args.filter_key:
            k, vs = _parse_filter_key_string(fkstr)
            outtmp[k] = vs
        args.filter_key_dict = outtmp


def run():
    args = get_parser().parse_args()
    args.func(args)


def run_qcpages(args):
    _parse_filter_keys(args)
    qc_all(args.search_dirs,
           args.output_dir,
           args.config_file,
           plugin=args.nipype_plugin,
           working_directory=args.working_directory,
           bids_validate=args.validate_bids,
           exclude_patterns=args.exclude,
           filter_keys_dict=args.filter_keys_dict)


def run_combine(args):
    group.make_tsv(args.input_files, args.output_file)


def run_image(args):
    out = reportlets._imshow(imgfile=args.image,
                             nslices=args.nslices,
                             labelfile=args.labelimage,
                             outtype=args.output_type)
    if args.output_type == 'svg':
        args.output_file.write_text(out)
    else:
        args.output_file.write_bytes(out)
