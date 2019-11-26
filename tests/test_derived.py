import numpy as np
import nibabel
from PipelineQC import configure, get_files, derived
from pathlib import Path
import os


def test_derived(tmp_path):
    aT1w = np.arange(10 * 11 * 12).reshape(10, 11, 12)
    amask = np.zeros_like(aT1w)
    amask[5:8, 2:9, 3:4] = 1.0
    bT1w = np.arange(10 * 11 * 13).reshape(10, 11, 13)
    bmask = np.zeros_like(bT1w)
    bmask[5:8, 2:9, 3:10] = 1.0
    aff = np.eye(4)
    aT1wfile = tmp_path / 'a_T1w.nii'
    amaskfile = tmp_path / 'a_mask.nii'
    bT1wfile = tmp_path / 'b_T1w.nii'
    bmaskfile = tmp_path / 'b_mask.nii'
    nibabel.Nifti1Image(aT1w, aff).to_filename(str(aT1wfile))
    nibabel.Nifti1Image(amask, aff).to_filename(str(amaskfile))
    nibabel.Nifti1Image(bT1w, aff).to_filename(str(bT1wfile))
    nibabel.Nifti1Image(bmask, aff).to_filename(str(bmaskfile))
    conf = configure.load_config(Path(__file__).parent / 'testconfderived.json')
    filesdict = get_files.get_files([tmp_path], conf)
    assert filesdict[('a',)]['T1w'] == aT1wfile
    assert filesdict[('a',)]['mask'] == amaskfile
    assert filesdict[('b',)]['T1w'] == bT1wfile
    assert filesdict[('b',)]['mask'] == bmaskfile
    derived.procderived(conf, filesdict)
    assert filesdict[('a',)]['T1w'] == aT1wfile
    assert filesdict[('a',)]['mask'] == amaskfile
    assert filesdict[('b',)]['T1w'] == bT1wfile
    assert filesdict[('b',)]['mask'] == bmaskfile
    aoutmask = nibabel.load(filesdict[('a',)]['T1wmask']).get_fdata()
    assert np.all(aoutmask == aT1w * amask)
    boutmask = nibabel.load(filesdict[('b',)]['T1wmask']).get_fdata()
    assert np.all(boutmask == bT1w * bmask)
    derived.removederived(conf, filesdict)
    assert not os.path.exists(filesdict[('a',)]['T1wmask'])
    assert not os.path.exists(filesdict[('b',)]['T1wmask'])
