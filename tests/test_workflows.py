from PipelineQC import workflows
from PipelineQC.configure import load_config
import pytest
from collections import defaultdict
from pathlib import Path
from PipelineQC import get_files
from nipype.interfaces.base import isdefined


@pytest.fixture()
def input_files_conf1():
    out = defaultdict(dict)
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
        out[(str(subnum), '10', '11', '12', None)]['features'] = Path(
            f'sub-{subnum}/anat/sub-{subnum}_acq-10_rec-11_run-12_space-T1w_desc-tissue_features.txt'
        )
        out[(str(subnum), '10', '11', '12', None)]['features_label'] = Path(
            f'sub-{subnum}/anat/sub-{subnum}_acq-10_rec-11_run-12_space-T1w_desc-tissue_features_labels.tsv'
        )
        out[(str(subnum), '10', '11', '12', None)]['crashfiles'] = Path(
            f'sub-{subnum}/logs/sub-{subnum}_acq-10_rec-11_run-12/crash.pklz')
    return out


def _make_files(tmp, files):
    outfull = defaultdict(dict)
    for key1, val1 in files.items():
        for key2, val2 in val1.items():
            ftmp = tmp / val2
            ftmp.parent.mkdir(parents=True, exist_ok=True)
            if key2 == 'features_label':
                ftmp.write_text('index\tname\n1\tGM\n2\tWM\n')
            else:
                ftmp.write_text(str(val2))
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
    wf = workflows.all_workflow(out, tmp_path, conf, filter_keys_dict=filter_dict)

    defaultnslices = 7
    defaultqcform = True

    truth = {
        'report.page_sub-1_acq-10_rec-11_run-12.compare1': {
            'name1': 'Non-uniformity corrected',
            'image1': str(infull[('1', '10', '11', '12', None)]['nu_bet']),
            'name2': 'Inormalized',
            'image2': str(infull[('1', '10', '11', '12', None)]['normalized']),
            'nslices': defaultnslices,
            'qcform': defaultqcform,
            'relative_dir': str(tmp_path.resolve() / 'sub-1'),
            'slice_to_image2': False,
            'max_intensity_fraction_image1': 0.99,
            'max_intensity_fraction_image2': 0.99,
            'affine_absolute_tolerance': 1e-3,
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-1_acq-10_rec-11_run-12.compare2': {
            'name1': 'Non-uniformity corrected',
            'image1': str(infull[('1', '10', '11', '12', None)]['nu_bet']),
            'name2': 'Inormalized',
            'image2': str(infull[('1', '10', '11', '12', None)]['normalized']),
            'nslices': 3,
            'qcform': defaultqcform,
            'relative_dir': str(tmp_path.resolve() / 'sub-1'),
            'slice_to_image2': False,
            'max_intensity_fraction_image1': 0.91,
            'max_intensity_fraction_image2': 0.92,
            'affine_absolute_tolerance': 1e-3,
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-1_acq-10_rec-11_run-12.compare3': {
            'name1': 'Non-uniformity corrected',
            'image1': str(infull[('1', '10', '11', '12', None)]['nu_bet']),
            'name2': 'Inormalized',
            'image2': str(infull[('1', '10', '11', '12', None)]['normalized']),
            'nslices': defaultnslices,
            'qcform': False,
            'relative_dir': str(tmp_path.resolve() / 'sub-1'),
            'slice_to_image2': True,
            'max_intensity_fraction_image1': 0.99,
            'max_intensity_fraction_image2': 0.99,
            'affine_absolute_tolerance': 1e-3,
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-1_acq-10_rec-11_run-12.single4': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('1', '10', '11', '12', None)]['nu_bet']),
            'nslices': defaultnslices,
            'qcform': defaultqcform,
            'relative_dir': str(tmp_path.resolve() / 'sub-1'),
            'max_intensity_fraction': 0.99,
            'affine_absolute_tolerance': 1e-3,
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-1_acq-10_rec-11_run-12.single5': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('1', '10', '11', '12', None)]['nu_bet']),
            'nslices': 3,
            'qcform': defaultqcform,
            'relative_dir': str(tmp_path.resolve() / 'sub-1'),
            'max_intensity_fraction': 0.99,
            'affine_absolute_tolerance': 1e-3,
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-1_acq-10_rec-11_run-12.single6': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('1', '10', '11', '12', None)]['nu_bet']),
            'nslices': defaultnslices,
            'qcform': False,
            'relative_dir': str(tmp_path.resolve() / 'sub-1'),
            'max_intensity_fraction': 0.99,
            'affine_absolute_tolerance': 1e-3,
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-1_acq-10_rec-11_run-12.contour7': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('1', '10', '11', '12', None)]['nu_bet']),
            'labelimage': str(infull[('1', '10', '11', '12',
                                      None)]['transformed_atlas']),
            'nslices': defaultnslices,
            'qcform': defaultqcform,
            'relative_dir': str(tmp_path.resolve() / 'sub-1'),
            'contour_width': 5,
            'slice_to_label': True,
            'max_intensity_fraction': 0.99,
            'affine_absolute_tolerance': 1e-2,
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-1_acq-10_rec-11_run-12.contour8': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('1', '10', '11', '12', None)]['nu_bet']),
            'labelimage': str(infull[('1', '10', '11', '12',
                                      None)]['transformed_atlas']),
            'nslices': 3,
            'qcform': defaultqcform,
            'relative_dir': str(tmp_path.resolve() / 'sub-1'),
            'contour_width': 5,
            'slice_to_label': False,
            'max_intensity_fraction': 0.99,
            'affine_absolute_tolerance': 1e-3,
            'affine_relative_tolerance': 1e-3
        },
        'report.page_sub-1_acq-10_rec-11_run-12.contour9': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('1', '10', '11', '12', None)]['nu_bet']),
            'labelimage': str(infull[('1', '10', '11', '12',
                                      None)]['transformed_atlas']),
            'nslices': defaultnslices,
            'qcform': False,
            'relative_dir': str(tmp_path.resolve() / 'sub-1'),
            'contour_width': 2.2,
            'slice_to_label': False,
            'max_intensity_fraction': 0.95,
            'affine_absolute_tolerance': 1e-3,
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-1_acq-10_rec-11_run-12.distributions10': {
            'name': 'features',
            'distsfile': str(infull[('1', '10', '11', '12',
                                     None)]['features']),
            'labelfile': str(infull[('1', '10', '11', '12',
                                     None)]['features_label']),
            'qcform': defaultqcform,
            'relative_dir': str(tmp_path.resolve() / 'sub-1')
        },
        'report.page_sub-1_acq-10_rec-11_run-12.distributions11': {
            'name': 'features',
            'distsfile': str(infull[('1', '10', '11', '12',
                                     None)]['features']),
            'labelfile': str(infull[('1', '10', '11', '12',
                                     None)]['features_label']),
            'qcform': False,
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
            'radio': {
                'name': 'Overall',
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
            'checkbox': {
                'name': 'Notes',
                'fields': ["Non-uniformity failed", "Registration failed"]
            },
            'text': {
                'name': 'Other'
            }
        },
        'report.page_sub-1_acq-10_rec-11_run-12.probmap14': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('1', '10', '11', '12', None)]['nu_bet']),
            'probmapimage': str(infull[('1', '10', '11', '12',
                                        None)]['transformed_atlas']),
            'nslices': defaultnslices,
            'qcform': False,
            'relative_dir': str(tmp_path.resolve() / 'sub-1'),
            'slice_to_probmap': False,
            'max_intensity_fraction': 0.95,
            'affine_absolute_tolerance': 1e-3,
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-2_acq-10_rec-11_run-12.compare1': {
            'name1': 'Non-uniformity corrected',
            'image1': str(infull[('2', '10', '11', '12', None)]['nu_bet']),
            'name2': 'Inormalized',
            'image2': str(infull[('2', '10', '11', '12', None)]['normalized']),
            'nslices': defaultnslices,
            'qcform': defaultqcform,
            'relative_dir': str(tmp_path.resolve() / 'sub-2'),
            'slice_to_image2': False,
            'max_intensity_fraction_image1': 0.99,
            'max_intensity_fraction_image2': 0.99,
            'affine_absolute_tolerance': 1e-3,
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-2_acq-10_rec-11_run-12.compare2': {
            'name1': 'Non-uniformity corrected',
            'image1': str(infull[('2', '10', '11', '12', None)]['nu_bet']),
            'name2': 'Inormalized',
            'image2': str(infull[('2', '10', '11', '12', None)]['normalized']),
            'nslices': 3,
            'qcform': defaultqcform,
            'relative_dir': str(tmp_path.resolve() / 'sub-2'),
            'slice_to_image2': False,
            'max_intensity_fraction_image1': 0.91,
            'max_intensity_fraction_image2': 0.92,
            'affine_absolute_tolerance': 1e-3,
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-2_acq-10_rec-11_run-12.compare3': {
            'name1': 'Non-uniformity corrected',
            'image1': str(infull[('2', '10', '11', '12', None)]['nu_bet']),
            'name2': 'Inormalized',
            'image2': str(infull[('2', '10', '11', '12', None)]['normalized']),
            'nslices': defaultnslices,
            'qcform': False,
            'relative_dir': str(tmp_path.resolve() / 'sub-2'),
            'slice_to_image2': True,
            'max_intensity_fraction_image1': 0.99,
            'max_intensity_fraction_image2': 0.99,
            'affine_absolute_tolerance': 1e-3,
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-2_acq-10_rec-11_run-12.single4': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('2', '10', '11', '12', None)]['nu_bet']),
            'nslices': defaultnslices,
            'qcform': defaultqcform,
            'relative_dir': str(tmp_path.resolve() / 'sub-2'),
            'max_intensity_fraction': 0.99,
            'affine_absolute_tolerance': 1e-3,
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-2_acq-10_rec-11_run-12.single5': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('2', '10', '11', '12', None)]['nu_bet']),
            'nslices': 3,
            'qcform': defaultqcform,
            'relative_dir': str(tmp_path.resolve() / 'sub-2'),
            'max_intensity_fraction': 0.99,
            'affine_absolute_tolerance': 1e-3,
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-2_acq-10_rec-11_run-12.single6': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('2', '10', '11', '12', None)]['nu_bet']),
            'nslices': defaultnslices,
            'qcform': False,
            'relative_dir': str(tmp_path.resolve() / 'sub-2'),
            'max_intensity_fraction': 0.99,
            'affine_absolute_tolerance': 1e-3,
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-2_acq-10_rec-11_run-12.contour7': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('2', '10', '11', '12', None)]['nu_bet']),
            'labelimage': str(infull[('2', '10', '11', '12',
                                      None)]['transformed_atlas']),
            'nslices': defaultnslices,
            'qcform': defaultqcform,
            'relative_dir': str(tmp_path.resolve() / 'sub-2'),
            'contour_width': 5,
            'slice_to_label': True,
            'max_intensity_fraction': 0.99,
            'affine_absolute_tolerance': 1e-2,
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-2_acq-10_rec-11_run-12.contour8': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('2', '10', '11', '12', None)]['nu_bet']),
            'labelimage': str(infull[('2', '10', '11', '12',
                                      None)]['transformed_atlas']),
            'nslices': 3,
            'qcform': defaultqcform,
            'relative_dir': str(tmp_path.resolve() / 'sub-2'),
            'contour_width': 5,
            'slice_to_label': False,
            'max_intensity_fraction': 0.99,
            'affine_absolute_tolerance': 1e-3,
            'affine_relative_tolerance': 1e-3
        },
        'report.page_sub-2_acq-10_rec-11_run-12.contour9': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('2', '10', '11', '12', None)]['nu_bet']),
            'labelimage': str(infull[('2', '10', '11', '12',
                                      None)]['transformed_atlas']),
            'nslices': defaultnslices,
            'qcform': False,
            'relative_dir': str(tmp_path.resolve() / 'sub-2'),
            'contour_width': 2.2,
            'slice_to_label': False,
            'max_intensity_fraction': 0.95,
            'affine_absolute_tolerance': 1e-3,
            'affine_relative_tolerance': 1e-5
        },
        'report.page_sub-2_acq-10_rec-11_run-12.distributions10': {
            'name': 'features',
            'distsfile': str(infull[('2', '10', '11', '12',
                                     None)]['features']),
            'labelfile': str(infull[('2', '10', '11', '12',
                                     None)]['features_label']),
            'qcform': defaultqcform,
            'relative_dir': str(tmp_path.resolve() / 'sub-2')
        },
        'report.page_sub-2_acq-10_rec-11_run-12.distributions11': {
            'name': 'features',
            'distsfile': str(infull[('2', '10', '11', '12',
                                     None)]['features']),
            'labelfile': str(infull[('2', '10', '11', '12',
                                     None)]['features_label']),
            'qcform': False,
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
            'radio': {
                'name': 'Overall',
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
            'checkbox': {
                'name': 'Notes',
                'fields': ["Non-uniformity failed", "Registration failed"]
            },
            'text': {
                'name': 'Other'
            }
        },
        'report.page_sub-2_acq-10_rec-11_run-12.probmap14': {
            'name': 'Non-uniformity corrected',
            'image': str(infull[('2', '10', '11', '12', None)]['nu_bet']),
            'probmapimage': str(infull[('2', '10', '11', '12',
                                        None)]['transformed_atlas']),
            'nslices': defaultnslices,
            'qcform': False,
            'relative_dir': str(tmp_path.resolve() / 'sub-2'),
            'slice_to_probmap': False,
            'max_intensity_fraction': 0.95,
            'affine_absolute_tolerance': 1e-3,
            'affine_relative_tolerance': 1e-5
        },
    }

    settings = {'image_width': 2, 'image_height': 1.75}

    def callable(node, graph):
        if node.fullname in truth.keys():
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

    wf.run(plugin='Debug', plugin_args={'callable': callable})
