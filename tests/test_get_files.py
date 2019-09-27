import pytest
from collections import defaultdict
from pathlib import Path
from PipelineQC import get_files
from PipelineQC import configure as conf


@pytest.fixture()
def input_files_conf1(tmp_path_factory):
    out = defaultdict(dict)
    out['global']['model'] = Path('model.nii')
    for subnum in [1, 2]:
        out[(str(subnum), '10', '11', '12', None)]['normalized'] = Path(
            f'sub-{subnum}/anat/sub-{subnum}_acq-10_rec-11_run-12_skullstripped-true_desc-normalized_T1w.nii'
        )
        out[(str(subnum), '10', '11', '12', None)]['nu_bet'] = Path(
            f'sub-{subnum}/anat/sub-{subnum}_acq-10_rec-11_run-12_skullstripped-true_desc-nucor_T1w.nii'
        )
        out[(str(subnum), '10', '11', '12', None)]['transformed_atlas'] = Path(
            f'sub-{subnum}/anat/sub-{subnum}_acq-10_rec-11_run-12_space-T1w_desc-lobes_dseg.nii'
        )
        out[(str(subnum), '10', '11', '12', None)]['classified'] = Path(
            f'sub-{subnum}/anat/sub-{subnum}_acq-10_rec-11_run-12_space-T1w_desc-tissue_dseg.nii'
        )
        out[(str(subnum), '10', '11', '12', None)]['features'] = Path(
            f'sub-{subnum}/anat/sub-{subnum}_acq-10_rec-11_run-12_space-T1w_desc-tissue_features.txt'
        )
        out[(str(subnum), '10', '11', '12', None)]['features_label'] = Path(
            f'sub-{subnum}/anat/sub-{subnum}_acq-10_rec-11_run-12_space-T1w_desc-tissue_features_labels.tsv'
        )
        out[(str(subnum), '10', '11', '12', None)]['warped_model'] = Path(
            f'sub-{subnum}/anat/sub-{subnum}_acq-10_rec-11_run-12_space-T1w_map-test_T1w.nii'
        )
        out[(str(subnum), '2', None, None, None)]['normalized'] = Path(
            f'sub-{subnum}/anat/sub-{subnum}_acq-2_skullstripped-true_desc-normalized_T1w.nii'
        )
        out[(str(subnum), '2', None, None, None)]['nu_bet'] = Path(
            f'sub-{subnum}/anat/sub-{subnum}_acq-2_skullstripped-true_desc-nucor_T1w.nii'
        )
        out[(str(subnum), '2', None, None, None)]['transformed_atlas'] = Path(
            f'sub-{subnum}/anat/sub-{subnum}_acq-2_space-T1w_desc-lobes_dseg.nii'
        )
        out[(str(subnum), '2', None, None, None)]['classified'] = Path(
            f'sub-{subnum}/anat/sub-{subnum}_acq-2_space-T1w_desc-tissue_dseg.nii'
        )
        out[(str(subnum), '2', None, None, None)]['features'] = Path(
            f'sub-{subnum}/anat/sub-{subnum}_acq-2_space-T1w_desc-tissue_features.txt'
        )
        out[(str(subnum), '2', None, None, None)]['warped_model'] = Path(
            f'sub-{subnum}/anat/sub-{subnum}_acq-2_space-T1w_map-test_T1w.nii')
        out[(str(subnum), None, None, None, None)]['normalized'] = Path(
            f'sub-{subnum}/anat/sub-{subnum}_skullstripped-true_desc-normalized_T1w.nii'
        )
        out[(str(subnum), None, None, None, None)]['nu_bet'] = Path(
            f'sub-{subnum}/anat/sub-{subnum}_skullstripped-true_desc-nucor_T1w.nii'
        )
        out[(str(subnum), None, None, None, None)]['transformed_atlas'] = Path(
            f'sub-{subnum}/anat/sub-{subnum}_space-T1w_desc-lobes_dseg.nii')
        out[(str(subnum), None, None, None, None)]['classified'] = Path(
            f'sub-{subnum}/anat/sub-{subnum}_space-T1w_desc-tissue_dseg.nii')
        out[(str(subnum), None, None, None, None)]['features'] = Path(
            f'sub-{subnum}/anat/sub-{subnum}_space-T1w_desc-tissue_features.txt'
        )
        out[(str(subnum), None, None, None, None)]['warped_model'] = Path(
            f'sub-{subnum}/anat/sub-{subnum}_space-T1w_map-test_T1w.nii')
        out[(str(subnum), None, None, None, 'a')]['normalized'] = Path(
            f'sub-{subnum}/ses-a/anat/sub-{subnum}_ses-a_skullstripped-true_desc-normalized_T1w.nii'
        )
        out[(str(subnum), None, None, None, 'a')]['nu_bet'] = Path(
            f'sub-{subnum}/ses-a/anat/sub-{subnum}_ses-a_skullstripped-true_desc-nucor_T1w.nii'
        )
        out[(str(subnum), None, None, None, 'a')]['transformed_atlas'] = Path(
            f'sub-{subnum}/ses-a/anat/sub-{subnum}_ses-a_space-T1w_desc-lobes_dseg.nii'
        )
        out[(str(subnum), None, None, None, 'a')]['classified'] = Path(
            f'sub-{subnum}/ses-a/anat/sub-{subnum}_ses-a_space-T1w_desc-tissue_dseg.nii'
        )
        out[(str(subnum), None, None, None, 'a')]['features'] = Path(
            f'sub-{subnum}/ses-a/anat/sub-{subnum}_ses-a_space-T1w_desc-tissue_features.txt'
        )
        out[(str(subnum), None, None, None, 'a')]['warped_model'] = Path(
            f'sub-{subnum}/ses-a/anat/sub-{subnum}_ses-a_space-T1w_map-test_T1w.nii'
        )
        out[(str(subnum), None, None, None, 'a')]['crashfiles'] = [
            Path(f'sub-{subnum}/ses-a/logs/sub-{subnum}_ses-a/crash1.pklz'),
            Path(f'sub-{subnum}/ses-a/logs/sub-{subnum}_ses-a/crash2.pklz')
        ]
    return out


@pytest.fixture()
def input_files_conf2(tmp_path_factory):
    out = defaultdict(dict)
    out['global'] = {}
    for subnum in ['sub1234_1234', 'sub5678_5678']:
        out[(subnum, )]['T1w'] = Path(f'orig/{subnum}_12345_125_mri.mnc')
        out[(subnum, )]['normalized'] = Path(
            f'NORM/{subnum}_12345_125_mri_normalized.mnc')
        out[(subnum, )]['bet'] = Path(f'BET/{subnum}_12345_125_mri_bet.mnc')
        out[(subnum, )]['transformed_atlas'] = Path(
            f'transformed/{subnum}_12345_125_mri_atlasRes.mnc')
        out[(subnum, )]['classified'] = Path(
            f'classify/{subnum}_12345_125_mri_classify.mnc')
        out[(subnum, )]['features'] = Path(
            f'classify/{subnum}_12345_125_mri_custom_priors.tag')
    return out


def _make_files(tmp, files):
    outfull = {}
    for key1, val1 in files.items():
        outfull[key1] = {}
        for key2, val2 in val1.items():
            if isinstance(val2, list):
                outfull[key1][key2] = []
                for val2t in val2:
                    ftmp = tmp / val2t
                    ftmp.parent.mkdir(parents=True, exist_ok=True)
                    ftmp.write_text(str(val2t))
                    outfull[key1][key2].append(ftmp)
            else:
                ftmp = tmp / val2
                ftmp.parent.mkdir(parents=True, exist_ok=True)
                ftmp.write_text(str(val2))
                outfull[key1][key2] = ftmp
    return outfull


def compare(x, y):
    assert x.keys() == y.keys()
    for k in x.keys():
        assert x[k].keys() == y[k].keys()
        for k2 in x[k].keys():
            if isinstance(x[k][k2], list):
                assert isinstance(y[k][k2], list)
                assert list(sorted(x[k][k2])) == list(sorted(y[k][k2]))
            else:
                assert x[k][k2] == y[k][k2]


@pytest.mark.parametrize(
    'conffilename',
    ['testconf1.json', 'testconf1bids.json', 'testconf1bids2.json'])
def test_conf1(tmp_path, input_files_conf1, conffilename):
    infull = _make_files(tmp_path, input_files_conf1)
    conffile = Path(__file__).parent / conffilename
    out = get_files.get_files([tmp_path], conf.load_config(conffile))
    compare(out, infull)


@pytest.mark.parametrize('conffilename',
                         ['testconf1.json', 'testconf1bids.json'])
def test_conf1_multfiles(tmp_path, input_files_conf1, conffilename):
    input_files_conf1[('1', None, None, None, None)]['nu_bet2'] = Path(
        f'sub-1/anat/sub-1_skullstripped-false_desc-nucor_T1w.nii')
    _make_files(tmp_path, input_files_conf1)
    conffile = Path(__file__).parent / conffilename
    with pytest.raises(get_files.MultipleFilesFoundError):
        get_files.get_files([tmp_path], conf.load_config(conffile))


def test_conf1_multfilt(tmp_path, input_files_conf1):
    input_files_conf1[('1', None, None, None, None)]['anotherfile'] = Path(
        f'sub-1/anat/sub-1_skullstripped-true_desc-nucor_features.nii')
    _make_files(tmp_path, input_files_conf1)
    conffile = Path(__file__).parent / 'testconf1.json'
    with pytest.raises(get_files.MultipleFilterResultsError):
        get_files.get_files([tmp_path], conf.load_config(conffile))


def test_conf1_multfiles2(tmp_path, input_files_conf1):
    input_files_conf1[('1', None, None, None, None)]['anotherfile'] = Path(
        f'sub-1/anat/sub-1_skullstripped-true_desc-nucor_features.nii')
    _make_files(tmp_path, input_files_conf1)
    conffile = Path(__file__).parent / 'testconf1bids.json'
    with pytest.raises(get_files.MultipleFilesFoundError):
        get_files.get_files([tmp_path], conf.load_config(conffile))


def test_conf2(tmp_path, input_files_conf2):
    infull = _make_files(tmp_path, input_files_conf2)
    conffile = Path(__file__).parent / 'testconf2.json'
    out = get_files.get_files([tmp_path], conf.load_config(conffile))
    compare(out, infull)


@pytest.mark.parametrize('conffile,bids_p,re_p',
                         [('testconf1.json', False, True),
                          ('testconf2.json', False, True),
                          ('testconf1bids.json', True, True),
                          ('testconf1bidsonly.json', True, False)])
def test_search_types(conffile, bids_p, re_p):
    c = conf.load_config(Path(__file__).parent / conffile)
    assert get_files._search_types(c) == (bids_p, re_p)


def test_search_types2(tmp_path, input_files_conf1):
    _make_files(tmp_path, input_files_conf1)
    c = conf.load_config(Path(__file__).parent / 'testconf1bids.json')
    layouts = get_files._get_bids_layouts([tmp_path], c)
