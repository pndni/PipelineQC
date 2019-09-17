import json
from pathlib import Path
import pandas as pd


def make_tsv(list_of_files, outputfile):

    df = pd.DataFrame()
    for f in list_of_files:
        data = json.loads(Path(f).read_text())
        df = df.append(data, ignore_index=True)
    df.set_index('title')
    df.to_csv(outputfile, sep='\t')
