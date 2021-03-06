from PipelineQC import workflows
from PipelineQC.configure import load_config
import pytest
from collections import defaultdict
from pathlib import Path
from PipelineQC import get_files
from nipype.interfaces.base import isdefined
import numpy as np
import nibabel


@pytest.fixture()
def input_files_conf1():
    array = np.zeros((100, 101, 102))
    array[2:8, 2:8, 2:8] = 1.0
    aff = np.eye(4)
    niimage = nibabel.Nifti1Image(array, affine=aff)
    out = defaultdict(dict)
    for subnum in [1, 2]:
        out[(str(subnum), '10', '11', '12', None)]['normalized'] = (Path(
            f'sub-{subnum}/anat/sub-{subnum}_acq-10_rec-11_run-12_skullstripped-true_desc-normalized_T1w.nii'
        ), niimage)
        out[(str(subnum), '10', '11', '12', None)]['nu_bet'] = (Path(
            f'sub-{subnum}/anat/sub-{subnum}_acq-10_rec-11_run-12_skullstripped-true_desc-nucor_T1w.nii'
        ), niimage)
        out[(str(subnum), '10', '11', '12', None)]['transformed_atlas'] = (Path(
            f'sub-{subnum}/anat/sub-{subnum}_acq-10_rec-11_run-12_space-T1w_desc-lobes_dseg.nii'
        ), niimage)
        out[(str(subnum), '10', '11', '12', None)]['features'] = (Path(
            f'sub-{subnum}/anat/sub-{subnum}_acq-10_rec-11_run-12_space-T1w_desc-tissue_features.txt'
        ), 'index\tvalue\n1.0\t100.0\n2.0\t200.0\n')
        out[(str(subnum), '10', '11', '12', None)]['features_label'] = (Path(
            f'sub-{subnum}/anat/sub-{subnum}_acq-10_rec-11_run-12_space-T1w_desc-tissue_features_labels.tsv'
        ), 'index\tname\n1\tGM\n2\tWM\n')
        out[(str(subnum), '10', '11', '12', None)]['crashfiles'] = (Path(
            f'sub-{subnum}/logs/sub-{subnum}_acq-10_rec-11_run-12/crash.txt'), None)
    return out


def _make_files(tmp, files):
    outfull = defaultdict(dict)
    for key1, val1 in files.items():
        for key2, (val2, val2towrite) in val1.items():
            ftmp = tmp / val2
            ftmp.parent.mkdir(parents=True, exist_ok=True)
            if val2towrite is None:
                ftmp.write_text(str(val2))
            elif isinstance(val2towrite, nibabel.Nifti1Image):
                val2towrite.to_filename(str(ftmp))
            else:
                ftmp.write_text(val2towrite)
            outfull[key1][key2] = ftmp
    return outfull


@pytest.mark.parametrize('filter_sub1', [False, True])
def test_all_wf(tmp_path, input_files_conf1, filter_sub1):
    infull = _make_files(tmp_path, input_files_conf1)
    conffile = Path(__file__).parent / 'testconf1.json'
    conf = load_config(conffile)
    out = get_files.get_files([tmp_path], conf)
    if filter_sub1:
        filter_dict = {'sub': ['1']}
    else:
        filter_dict = None
    wf = workflows.all_workflow(out,
                                tmp_path,
                                conf,
                                filter_keys_dict=filter_dict)

    defaultnslices = 7

    truth = {
        'report.page_sub-1_acq-10_rec-11_run-12.compare1': {
            'name1': 'Non-uniformity corrected',
            'image1': str(infull[('1', '10', '11', '12', None)]['nu_bet']),
            'name2': 'Inormalized',
            'image2': str(infull[('1', '10', '11', '12', None)]['normalized']),
            'nslices': defaultnslices,
            'relative_dir': str(tmp_path.resolve() / 'sub-1'),
            'slice_to_image2': False,
            'max_intensity_fraction_image1': 0.99,
            'max_intensity_fraction_image2': 0.99,
            'affine_absolute_tolerance': 1e-3,
            'affine_relative_tolerance': 1e-5,
            'description': '',
        },
        'report.page_sub-1_acq-10_rec-11_run-12.compare2': {
            'name1': 'Non-uniformity corrected',
            'image1': str(infull[('1', '10', '11', '12', None)]['nu_bet']),
            'name2': 'Inormalized',
            'image2': str(infull[('1', '10', '11', '12', None)]['normalized']),
            'nslices': 3,
            'relative_dir': str(tmp_path.resolve() / 'sub-1'),
            'slice_to_image2': False,
            'max_intensity_fraction_image1': 0.91,
            'max_intensity_fraction_image2': 0.92,
            'affine_absolute_tolerance': 1e-3,
            'description': '',
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-1_acq-10_rec-11_run-12.compare3': {
            'name1': 'Non-uniformity corrected',
            'image1': str(infull[('1', '10', '11', '12', None)]['nu_bet']),
            'name2': 'Inormalized',
            'image2': str(infull[('1', '10', '11', '12', None)]['normalized']),
            'nslices': defaultnslices,
            'relative_dir': str(tmp_path.resolve() / 'sub-1'),
            'slice_to_image2': True,
            'max_intensity_fraction_image1': 0.99,
            'max_intensity_fraction_image2': 0.99,
            'affine_absolute_tolerance': 1e-3,
            'description': '',
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-1_acq-10_rec-11_run-12.single4': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('1', '10', '11', '12', None)]['nu_bet']),
            'nslices': defaultnslices,
            'relative_dir': str(tmp_path.resolve() / 'sub-1'),
            'max_intensity_fraction': 0.99,
            'affine_absolute_tolerance': 1e-3,
            'description': '',
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-1_acq-10_rec-11_run-12.single5': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('1', '10', '11', '12', None)]['nu_bet']),
            'nslices': 3,
            'relative_dir': str(tmp_path.resolve() / 'sub-1'),
            'max_intensity_fraction': 0.99,
            'affine_absolute_tolerance': 1e-3,
            'description': '',
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-1_acq-10_rec-11_run-12.single6': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('1', '10', '11', '12', None)]['nu_bet']),
            'nslices': defaultnslices,
            'relative_dir': str(tmp_path.resolve() / 'sub-1'),
            'max_intensity_fraction': 0.99,
            'affine_absolute_tolerance': 1e-3,
            'description': '',
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-1_acq-10_rec-11_run-12.contour7': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('1', '10', '11', '12', None)]['nu_bet']),
            'labelimage': str(infull[('1', '10', '11', '12',
                                      None)]['transformed_atlas']),
            'nslices': defaultnslices,
            'relative_dir': str(tmp_path.resolve() / 'sub-1'),
            'contour_width': 5,
            'slice_to_label': True,
            'max_intensity_fraction': 0.99,
            'affine_absolute_tolerance': 1e-2,
            'description': '',
            'affine_relative_tolerance': 1e-5,
            'contour_levels': None,
            'threshold_above_zero': False
        },
        'report.page_sub-1_acq-10_rec-11_run-12.contour8': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('1', '10', '11', '12', None)]['nu_bet']),
            'labelimage': str(infull[('1', '10', '11', '12',
                                      None)]['transformed_atlas']),
            'nslices': 3,
            'relative_dir': str(tmp_path.resolve() / 'sub-1'),
            'contour_width': 5,
            'slice_to_label': False,
            'max_intensity_fraction': 0.99,
            'affine_absolute_tolerance': 1e-3,
            'description': '',
            'affine_relative_tolerance': 1e-3,
            'contour_levels': [1e-3],
            'threshold_above_zero': False
        },
        'report.page_sub-1_acq-10_rec-11_run-12.contour9': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('1', '10', '11', '12', None)]['nu_bet']),
            'labelimage': str(infull[('1', '10', '11', '12',
                                      None)]['transformed_atlas']),
            'nslices': defaultnslices,
            'relative_dir': str(tmp_path.resolve() / 'sub-1'),
            'contour_width': 2.2,
            'slice_to_label': False,
            'max_intensity_fraction': 0.95,
            'affine_absolute_tolerance': 1e-3,
            'description': '',
            'affine_relative_tolerance': 1e-5,
            'contour_levels': None,
            'threshold_above_zero': False
        },
        'report.page_sub-1_acq-10_rec-11_run-12.distributions10': {
            'name': 'features',
            'distsfile': str(infull[('1', '10', '11', '12',
                                     None)]['features']),
            'labelfile': str(infull[('1', '10', '11', '12',
                                     None)]['features_label']),
            'description': '',
            'relative_dir': str(tmp_path.resolve() / 'sub-1')
        },
        'report.page_sub-1_acq-10_rec-11_run-12.distributions11': {
            'name': 'features',
            'distsfile': str(infull[('1', '10', '11', '12',
                                     None)]['features']),
            'labelfile': str(infull[('1', '10', '11', '12',
                                     None)]['features_label']),
            'description': '',
            'relative_dir': str(tmp_path.resolve() / 'sub-1')
        },
        'report.page_sub-1_acq-10_rec-11_run-12.crash12': {
            'name': 'error',
            'crashfiles': [
                str(infull[('1', '10', '11', '12', None)]['crashfiles'])
            ],
            'relative_dir': str(tmp_path.resolve() / 'sub-1')
        },
        'report.page_sub-1_acq-10_rec-11_run-12.rating13': {
            'name': 'Rating',
            'widgets': [
                {
                 'name': 'Overall',
                 'type': 'radio',
                 'options': [{
                     "name": "Reject", "value": 1
                 }, {
                     "name": "Poor", "value": 2
                 }, {
                     "name": "Acceptable", "value": 3
                 }, {
                     "name": "Good", "value": 4
                 }, {
                     "name": "Great", "value": 5
                 }]
                },
                {
                    'name': 'Notes',
                    'type': 'checkbox',
                    'fields': ["Non-uniformity failed", "Registration failed"]
                },
                {
                    'name': 'Other',
                    'type': 'text'
                }
            ]
        },
        'report.page_sub-1_acq-10_rec-11_run-12.probmap14': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('1', '10', '11', '12', None)]['nu_bet']),
            'probmapimage': str(infull[('1', '10', '11', '12',
                                        None)]['transformed_atlas']),
            'nslices': defaultnslices,
            'relative_dir': str(tmp_path.resolve() / 'sub-1'),
            'slice_to_probmap': False,
            'max_intensity_fraction': 0.95,
            'affine_absolute_tolerance': 1e-3,
            'description': '',
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-1_acq-10_rec-11_run-12.overlay15': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('1', '10', '11', '12', None)]['nu_bet']),
            'labelimage': str(infull[('1', '10', '11', '12',
                                      None)]['transformed_atlas']),
            'nslices': defaultnslices,
            'relative_dir': str(tmp_path.resolve() / 'sub-1'),
            'slice_to_label': False,
            'max_intensity_fraction': 0.95,
            'affine_absolute_tolerance': 1e-3,
            'description': '',
            'affine_relative_tolerance': 1e-5,
            'transparency': 0.5
        },
        'report.page_sub-2_acq-10_rec-11_run-12.compare1': {
            'name1': 'Non-uniformity corrected',
            'image1': str(infull[('2', '10', '11', '12', None)]['nu_bet']),
            'name2': 'Inormalized',
            'image2': str(infull[('2', '10', '11', '12', None)]['normalized']),
            'nslices': defaultnslices,
            'relative_dir': str(tmp_path.resolve() / 'sub-2'),
            'slice_to_image2': False,
            'max_intensity_fraction_image1': 0.99,
            'max_intensity_fraction_image2': 0.99,
            'affine_absolute_tolerance': 1e-3,
            'description': '',
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-2_acq-10_rec-11_run-12.compare2': {
            'name1': 'Non-uniformity corrected',
            'image1': str(infull[('2', '10', '11', '12', None)]['nu_bet']),
            'name2': 'Inormalized',
            'image2': str(infull[('2', '10', '11', '12', None)]['normalized']),
            'nslices': 3,
            'relative_dir': str(tmp_path.resolve() / 'sub-2'),
            'slice_to_image2': False,
            'max_intensity_fraction_image1': 0.91,
            'max_intensity_fraction_image2': 0.92,
            'affine_absolute_tolerance': 1e-3,
            'description': '',
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-2_acq-10_rec-11_run-12.compare3': {
            'name1': 'Non-uniformity corrected',
            'image1': str(infull[('2', '10', '11', '12', None)]['nu_bet']),
            'name2': 'Inormalized',
            'image2': str(infull[('2', '10', '11', '12', None)]['normalized']),
            'nslices': defaultnslices,
            'relative_dir': str(tmp_path.resolve() / 'sub-2'),
            'slice_to_image2': True,
            'max_intensity_fraction_image1': 0.99,
            'max_intensity_fraction_image2': 0.99,
            'affine_absolute_tolerance': 1e-3,
            'description': '',
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-2_acq-10_rec-11_run-12.single4': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('2', '10', '11', '12', None)]['nu_bet']),
            'nslices': defaultnslices,
            'relative_dir': str(tmp_path.resolve() / 'sub-2'),
            'max_intensity_fraction': 0.99,
            'affine_absolute_tolerance': 1e-3,
            'description': '',
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-2_acq-10_rec-11_run-12.single5': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('2', '10', '11', '12', None)]['nu_bet']),
            'nslices': 3,
            'relative_dir': str(tmp_path.resolve() / 'sub-2'),
            'max_intensity_fraction': 0.99,
            'affine_absolute_tolerance': 1e-3,
            'description': '',
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-2_acq-10_rec-11_run-12.single6': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('2', '10', '11', '12', None)]['nu_bet']),
            'nslices': defaultnslices,
            'relative_dir': str(tmp_path.resolve() / 'sub-2'),
            'max_intensity_fraction': 0.99,
            'affine_absolute_tolerance': 1e-3,
            'description': '',
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-2_acq-10_rec-11_run-12.contour7': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('2', '10', '11', '12', None)]['nu_bet']),
            'labelimage': str(infull[('2', '10', '11', '12',
                                      None)]['transformed_atlas']),
            'nslices': defaultnslices,
            'relative_dir': str(tmp_path.resolve() / 'sub-2'),
            'contour_width': 5,
            'slice_to_label': True,
            'max_intensity_fraction': 0.99,
            'affine_absolute_tolerance': 1e-2,
            'description': '',
            'affine_relative_tolerance': 1e-5,
            'contour_levels': None,
            'threshold_above_zero': False
        },
        'report.page_sub-2_acq-10_rec-11_run-12.contour8': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('2', '10', '11', '12', None)]['nu_bet']),
            'labelimage': str(infull[('2', '10', '11', '12',
                                      None)]['transformed_atlas']),
            'nslices': 3,
            'relative_dir': str(tmp_path.resolve() / 'sub-2'),
            'contour_width': 5,
            'slice_to_label': False,
            'max_intensity_fraction': 0.99,
            'affine_absolute_tolerance': 1e-3,
            'description': '',
            'affine_relative_tolerance': 1e-3,
            'contour_levels': [1e-3],
            'threshold_above_zero': False
        },
        'report.page_sub-2_acq-10_rec-11_run-12.contour9': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('2', '10', '11', '12', None)]['nu_bet']),
            'labelimage': str(infull[('2', '10', '11', '12',
                                      None)]['transformed_atlas']),
            'nslices': defaultnslices,
            'relative_dir': str(tmp_path.resolve() / 'sub-2'),
            'contour_width': 2.2,
            'slice_to_label': False,
            'max_intensity_fraction': 0.95,
            'affine_absolute_tolerance': 1e-3,
            'description': '',
            'affine_relative_tolerance': 1e-5,
            'contour_levels': None,
            'threshold_above_zero': False
        },
        'report.page_sub-2_acq-10_rec-11_run-12.distributions10': {
            'name': 'features',
            'distsfile': str(infull[('2', '10', '11', '12',
                                     None)]['features']),
            'labelfile': str(infull[('2', '10', '11', '12',
                                     None)]['features_label']),
            'description': '',
            'relative_dir': str(tmp_path.resolve() / 'sub-2')
        },
        'report.page_sub-2_acq-10_rec-11_run-12.distributions11': {
            'name': 'features',
            'distsfile': str(infull[('2', '10', '11', '12',
                                     None)]['features']),
            'labelfile': str(infull[('2', '10', '11', '12',
                                     None)]['features_label']),
            'description': '',
            'relative_dir': str(tmp_path.resolve() / 'sub-2')
        },
        'report.page_sub-2_acq-10_rec-11_run-12.crash12': {
            'name': 'error',
            'crashfiles': [
                str(infull[('2', '10', '11', '12', None)]['crashfiles'])
            ],
            'relative_dir': str(tmp_path.resolve() / 'sub-2')
        },
        'report.page_sub-2_acq-10_rec-11_run-12.rating13': {
            'name': 'Rating',
            'widgets': [
                {
                 'name': 'Overall',
                 'type': 'radio',
                 'options': [{
                     "name": "Reject", "value": 1
                 }, {
                     "name": "Poor", "value": 2
                 }, {
                     "name": "Acceptable", "value": 3
                 }, {
                     "name": "Good", "value": 4
                 }, {
                     "name": "Great", "value": 5
                 }]
                },
                {
                    'name': 'Notes',
                    'type': 'checkbox',
                    'fields': ["Non-uniformity failed", "Registration failed"]
                },
                {
                    'name': 'Other',
                    'type': 'text'
                }
            ]
        },
        'report.page_sub-2_acq-10_rec-11_run-12.probmap14': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('2', '10', '11', '12', None)]['nu_bet']),
            'probmapimage': str(infull[('2', '10', '11', '12',
                                        None)]['transformed_atlas']),
            'nslices': defaultnslices,
            'relative_dir': str(tmp_path.resolve() / 'sub-2'),
            'slice_to_probmap': False,
            'max_intensity_fraction': 0.95,
            'affine_absolute_tolerance': 1e-3,
            'description': '',
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-2_acq-10_rec-11_run-12.overlay15': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('2', '10', '11', '12', None)]['nu_bet']),
            'labelimage': str(infull[('2', '10', '11', '12',
                                      None)]['transformed_atlas']),
            'nslices': defaultnslices,
            'relative_dir': str(tmp_path.resolve() / 'sub-2'),
            'slice_to_label': False,
            'max_intensity_fraction': 0.95,
            'affine_absolute_tolerance': 1e-3,
            'description': '',
            'affine_relative_tolerance': 1e-5,
            'transparency': 0.5
        },
    }

    settings = {'image_width': 2, 'image_height': 1.75}

    class Callable(object):

        def __init__(self):
            self.nodes_seen = set()
            self.nodes_checked = set()

        def __call__(self, node, graph):
            self.nodes_seen.add(node.fullname)
            if node.fullname in truth.keys():
                self.nodes_checked.add(node.fullname)
                node_traits = set(node.inputs.visible_traits())
                for k in set(truth[node.fullname].keys()):
                    assert getattr(node.inputs, k) == truth[node.fullname][k]
                for k in node_traits - set(truth[node.fullname].keys()):
                    if k in settings:
                        assert getattr(node.inputs, k) == settings[k]
                    else:
                        assert not isdefined(getattr(node.inputs, k))
            if filter_sub1:
                assert 'sub-2' not in node.fullname

    callable = Callable()
    wf.run(plugin='Debug', plugin_args={'callable': callable})
    if filter_sub1:
        assert callable.nodes_checked == set(filter(lambda x: 'sub-2' not in x, truth.keys()))
    else:
        assert callable.nodes_checked == set(truth.keys())
    wf.run(plugin='Linear')
