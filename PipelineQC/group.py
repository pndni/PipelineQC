import json
from pathlib import Path
import pandas as pd
from .reportlets import index


def make_tsv(list_of_files, outputfile):

    df = pd.DataFrame()
    for f in list_of_files:
        data = json.loads(Path(f).read_text())
        df = df.append(data, ignore_index=True)
    df.set_index('title')
    df.to_csv(outputfile, sep='\t')


def make_index(output_dir, index_filename):
    outdir = Path(output_dir)
    fnames = list(sorted(outdir.glob('**/*.html')))
    index(out_file=index_filename,
          in_files=fnames,
          relative_dir=index_filename.parent)
