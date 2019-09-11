import pytest
from PipelineQC import configure as conf


def test_format_output():
    c = {"page_keys": ["sub", "acq", "rec", "run", "ses"],
         "page_filename_template": "sub-{sub}[/ses-{ses}]/sub-{sub}[_ses-{ses}][_acq-{acq}][_rec-{rec}][_run-{run}]_QC.html"}
    assert conf.format_output(c, (1, None, None, None, None)) == 'sub-1/sub-1_QC.html'
    assert conf.format_output(c, (1, 'hi', None, None, None)) == 'sub-1/sub-1_acq-hi_QC.html'
    assert conf.format_output(c, (1, 'hi', 'rec', None, None)) == 'sub-1/sub-1_acq-hi_rec-rec_QC.html'
    assert conf.format_output(c, (42, None, None, None, 'BL')) == 'sub-42/ses-BL/sub-42_ses-BL_QC.html'
    assert conf.format_output(c, (42, None, None, 10, 'BL')) == 'sub-42/ses-BL/sub-42_ses-BL_run-10_QC.html'


def test_format_output_invalid():
    c = {"page_keys": ["sub", "acq", "rec", "run", "ses"],
         "page_filename_template": "sub-{sub}[/ses-{ses}{sub}]/sub-{sub}[_ses-{ses}][_acq-{acq}][_rec-{rec}][_run-{run}]_QC.html"}
    with pytest.raises(conf.InvalidFormatError):
        conf.format_output(c, (1, None, None, None, None))
