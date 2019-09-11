from .get_files import get_files
from .report import all_workflow
from .configure import load_config
from pathlib import Path
import argparse


def qc_all(dirs, output_dir, configfile, plugin='MultiProc', plugin_args=None,
           working_directory=None):
    conf = load_config(configfile)
    filedict = get_files(dirs, conf)
    if len(filedict) == 1 and len(filedict['global']) == 0:
        raise RuntimeError('No files found!')
    wf = all_workflow(filedict, output_dir, conf)
    if working_directory is not None:
        if not Path(working_directory).exists():
            raise FileNotFoundError(f'{working_directory} does not exist')
        wf.base_dir = str(working_directory.resolve())
    if plugin_args is None:
        plugin_args = {}
    wf.run(plugin=plugin, plugin_args=plugin_args)


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', type=Path,
                        help='JSON configuration file. See the documentation for details')
    parser.add_argument('output_dir', type=Path,
                        help='Output root for QC pages and index file')
    parser.add_argument('search_dirs', type=Path, nargs='+',
                        help='Search these directories for files')
    parser.add_argument('--nipype_plugin', type=str, default='MultiProc',
                        help='Passed directly to the nipype workflow run method')
    parser.add_argument('--working_directory', type=Path,
                        help='Working directory for nipype workflow (i.e., "base_dir")')
    return parser


def run():
    args = get_parser().parse_args()
    qc_all(args.search_dirs, args.output_dir, args.config_file, plugin=args.nipype_plugin,
           working_directory=args.working_directory)
