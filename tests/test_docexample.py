from PipelineQC.configure import load_config
from PipelineQC.get_files import get_files
from PipelineQC import workflows
from pathlib import Path
from nipype.interfaces.base import isdefined
import pytest


@pytest.mark.parametrize('conffilename', ['testconfdocs.json', 'testconfdocsbids.json'])
def test_confdoc(tmp_path, conffilename):
    indir = tmp_path / 'in'
    anat1 = indir / 'sub-1' / 'anat'
    anat1.mkdir(parents=True)
    (anat1 / 'sub-1_T1w.nii').write_text('s1t1')
    (anat1 / 'sub-1_acq-fast_T1w.nii').write_text('s1aft1')
    anat2 = indir / 'sub-2' / 'anat'
    anat2.mkdir(parents=True)
    (anat2 / 'sub-2_T1w.nii').write_text('s2t1')
    (indir / 'MNI152.nii').write_text('MNI')

    outdir = tmp_path / 'out'
    for i, d1 in enumerate(['sub-1', 'sub-2'], start=1):
        betdir = outdir / d1 / 'BET'
        betdir.mkdir(parents=True)
        (betdir / f'sub-{i}_bet.nii').write_text(f's{i}b')
        if i == 1:
            (betdir / f'sub-{i}_acq-fast_bet.nii').write_text(f's{i}afb')
        classdir = outdir / d1 / 'classify'
        classdir.mkdir(parents=True)
        (classdir / f'sub-{i}_dseg.nii').write_text(f's{i}c')
        if i == 1:
            (classdir / f'sub-{i}_acq-fast_dseg.nii').write_text(f's{i}afc')
    crashdir = outdir / 'sub-1' / 'logs' / 'sub-1_acq-fast'
    crashdir.mkdir(parents=True)
    (crashdir / 'crash.pklz').write_text('crash')

    conf = load_config(Path(__file__).parent / conffilename)
    outfiles = get_files([indir, outdir], conf, Path(__file__).parent)

    assert outfiles[('1', None)]['T1'] == tmp_path / 'in' / 'sub-1' / 'anat' / 'sub-1_T1w.nii'
    assert outfiles[('1', 'fast')]['T1'] == tmp_path / 'in' / 'sub-1' / 'anat' / 'sub-1_acq-fast_T1w.nii'
    assert outfiles[('2', None)]['T1'] == tmp_path / 'in' / 'sub-2' / 'anat' / 'sub-2_T1w.nii'

    assert outfiles[('1', None)]['BET'] == tmp_path / 'out' / 'sub-1' / 'BET' / 'sub-1_bet.nii'
    assert outfiles[('1', 'fast')]['BET'] == tmp_path / 'out' / 'sub-1' / 'BET' / 'sub-1_acq-fast_bet.nii'
    assert outfiles[('2', None)]['BET'] == tmp_path / 'out' / 'sub-2' / 'BET' / 'sub-2_bet.nii'

    assert outfiles[('1', None)]['classified'] == tmp_path / 'out' / 'sub-1' / 'classify' / 'sub-1_dseg.nii'
    assert outfiles[('1', 'fast')]['classified'] == tmp_path / 'out' / 'sub-1' / 'classify' / 'sub-1_acq-fast_dseg.nii'
    assert outfiles[('2', None)]['classified'] == tmp_path / 'out' / 'sub-2' / 'classify' / 'sub-2_dseg.nii'

    assert outfiles['global']['MNI'] == tmp_path / 'in' / 'MNI152.nii'
    assert outfiles[('1', 'fast')]['crashfiles'] == [tmp_path / 'out' / 'sub-1' / 'logs' / 'sub-1_acq-fast' / 'crash.pklz']
    assert 'crashfiles' not in outfiles[('1', None)]
    assert 'crashfiles' not in outfiles[('2', None)]

    assert len(outfiles[('1', None)]) == 3
    assert len(outfiles[('1', 'fast')]) == 4
    assert len(outfiles[('2', None)]) == 3
    assert len(outfiles['global']) == 1

    out = tmp_path / 'out'
    wf = workflows.all_workflow(outfiles, out, conf)


    truth = {'report.page_sub-1.compare1':
             {'name1': 'T1w input file',
              'image1': str(tmp_path / 'in' / 'sub-1' / 'anat' / 'sub-1_T1w.nii'),
              'name2': 'Brain extracted files',
              'image2': str(tmp_path / 'out' / 'sub-1' / 'BET' / 'sub-1_bet.nii'),
              'nslices': 7,
              'qcform': True,
              'relative_dir': str(out.resolve())},
             'report.page_sub-1.contour2':
             {'name': 'Tissue classification',
              'image': str(tmp_path / 'out' / 'sub-1' / 'BET' / 'sub-1_bet.nii'),
              'labelimage': str(tmp_path / 'out' / 'sub-1' / 'classify' / 'sub-1_dseg.nii'),
              'nslices': 7,
              'qcform': True,
              'relative_dir': str(out.resolve())},
             'report.page_sub-1.crash3':
             {'name': 'Errors',
              'crashfiles': [],
              'relative_dir': str(out.resolve())},
             'report.page_sub-1_acq-fast.compare1':
             {'name1': 'T1w input file',
              'image1': str(tmp_path / 'in' / 'sub-1' / 'anat' / 'sub-1_acq-fast_T1w.nii'),
              'name2': 'Brain extracted files',
              'image2': str(tmp_path / 'out' / 'sub-1' / 'BET' / 'sub-1_acq-fast_bet.nii'),
              'nslices': 7,
              'qcform': True,
              'relative_dir': str(out.resolve())},
             'report.page_sub-1_acq-fast.contour2':
             {'name': 'Tissue classification',
              'image': str(tmp_path / 'out' / 'sub-1' / 'BET' / 'sub-1_acq-fast_bet.nii'),
              'labelimage': str(tmp_path / 'out' / 'sub-1' / 'classify' / 'sub-1_acq-fast_dseg.nii'),
              'nslices': 7,
              'qcform': True,
              'relative_dir': str(out.resolve())},
             'report.page_sub-1_acq-fast.crash3':
             {'name': 'Errors',
              'crashfiles': [str(tmp_path / 'out' / 'sub-1' / 'logs' / 'sub-1_acq-fast' / 'crash.pklz')],
              'relative_dir': str(out.resolve())},
             'report.page_sub-2.compare1':
             {'name1': 'T1w input file',
              'image1': str(tmp_path / 'in' / 'sub-2' / 'anat' / 'sub-2_T1w.nii'),
              'name2': 'Brain extracted files',
              'image2': str(tmp_path / 'out' / 'sub-2' / 'BET' / 'sub-2_bet.nii'),
              'nslices': 7,
              'qcform': True,
              'relative_dir': str(out.resolve())},
             'report.page_sub-2.contour2':
             {'name': 'Tissue classification',
              'image': str(tmp_path / 'out' / 'sub-2' / 'BET' / 'sub-2_bet.nii'),
              'labelimage': str(tmp_path / 'out' / 'sub-2' / 'classify' / 'sub-2_dseg.nii'),
              'nslices': 7,
              'qcform': True,
              'relative_dir': str(out.resolve())},
             'report.page_sub-2.crash3':
             {'name': 'Errors',
              'crashfiles': [],
              'relative_dir': str(out.resolve())},
             'report.page_sub-1.assemble':
             {'out_file': str(out / 'sub-1_QC.html'),
              'title': 'sub-1'},
             'report.page_sub-1-acq-fast.assemble':
             {'out_file': str(out / 'sub-1_acq-1_QC.html'),
              'title': 'sub-1_acq-1'},
             'report.page_sub-2.assemble':
             {'out_file': str(out / 'sub-2_QC.html'),
              'title': 'sub-2'},
             'report.index_pages':
             {'out_file': str(out / 'QC_index.html')},
             }

    def callable(node, graph):
        if node.fullname in truth.keys():
            node_traits = set(node.inputs.trait_names()) - {'trait_added', 'trait_modified'}
            for k in set(truth[node.fullname].keys()):
                assert getattr(node.inputs, k) == truth[node.fullname][k]
            for k in node_traits - set(truth[node.fullname].keys()):
                assert not isdefined(getattr(node.inputs, k))

    wf.run(plugin='Debug', plugin_args={'callable': callable})

    del conf["files"]["MNI"]["global"]
    with pytest.raises(IndexError):
        outfiles = get_files([indir, outdir], conf, Path(__file__).parent)
