import pytest
from PipelineQC import configure as conf
import json
import jsonschema


def test_format_output():
    c = {
        "page_keys": ["sub", "acq", "rec", "run", "ses"],
        "page_filename_template":
        "sub-{sub}[/ses-{ses}]/sub-{sub}[_ses-{ses}][_acq-{acq}][_rec-{rec}][_run-{run}]_QC.html"
    }
    assert conf.format_output(
        c, (1, None, None, None, None)) == 'sub-1/sub-1_QC.html'
    assert conf.format_output(
        c, (1, 'hi', None, None, None)) == 'sub-1/sub-1_acq-hi_QC.html'
    assert conf.format_output(
        c,
        (1, 'hi', 'rec', None, None)) == 'sub-1/sub-1_acq-hi_rec-rec_QC.html'
    assert conf.format_output(
        c,
        (42, None, None, None, 'BL')) == 'sub-42/ses-BL/sub-42_ses-BL_QC.html'
    assert conf.format_output(
        c, (42, None, None, 10,
            'BL')) == 'sub-42/ses-BL/sub-42_ses-BL_run-10_QC.html'


def test_format_output_invalid():
    c = {
        "page_keys": ["sub", "acq", "rec", "run", "ses"],
        "page_filename_template":
        "sub-{sub}[/ses-{ses}{sub}]/sub-{sub}[_ses-{ses}][_acq-{acq}][_rec-{rec}][_run-{run}]_QC.html"
    }
    with pytest.raises(conf.InvalidFormatError):
        conf.format_output(c, (1, None, None, None, None))


@pytest.fixture
def baseconf():
    conf = {
        'page_keys': ['sub'],
        'page_filename_template': '{sub}.html',
        'index_filename': 'index.html',
        'patterns': {
            'pattern1': '^.*$'
        },
        'files': {
            'file1': {
                'pattern': 'pattern1', 'filter': {}
            }
        },
        'reportlets': [{
            'type': 'single', 'name': 'test', 'image': 'file1'
        }]
    }
    return conf


def test_conf_succ(baseconf, tmp_path):
    with open(tmp_path / 'conf.json', 'w+') as f:
        json.dump(baseconf, f)
        f.seek(0)
        conf.load_config(f)


@pytest.mark.parametrize('key',
                         [
                             'page_keys',
                             'page_filename_template',
                             'index_filename',
                             'patterns',
                             'files',
                             'reportlets'
                         ])
def test_conf_fail1(baseconf, tmp_path, key):
    del baseconf[key]
    with open(tmp_path / 'conf.json', 'w+') as f:
        json.dump(baseconf, f)
        f.seek(0)
        with pytest.raises(jsonschema.ValidationError):
            conf.load_config(f)
