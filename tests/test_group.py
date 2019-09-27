import json
from PipelineQC.group import make_tsv
import csv
import subprocess


def test_make_tsv(tmp_path):
    d1 = {'title': '1', 'a': '2', 'b': '3'}
    d2 = {'title': '2', 'a': '4', 'c': '6'}
    (tmp_path / 'd1.json').write_text(json.dumps(d1))
    (tmp_path / 'd2.json').write_text(json.dumps(d2))
    make_tsv([(tmp_path / 'd1.json'), (tmp_path / 'd2.json')],
             (tmp_path / 'out.tsv'))
    subprocess.check_call([
        'PipelineQC',
        'combine',
        str(tmp_path / 'out2.tsv'),
        str(tmp_path / 'd1.json'),
        str(tmp_path / 'd2.json')
    ])
    for outname in ['out.tsv', 'out2.tsv']:
        with open(tmp_path / outname, 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            r1 = next(reader)
            r2 = next(reader)
            assert r1['title'] == '1'
            assert r1['a'] == '2'
            assert r1['b'] == '3'
            assert r1['c'] == ''
            assert r2['title'] == '2'
            assert r2['a'] == '4'
            assert r2['b'] == ''
            assert r2['c'] == '6'
