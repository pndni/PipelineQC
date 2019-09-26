from PipelineQC import reportlets
import nibabel
import numpy as np
import pytest
from nipype import utils as nputils
from nipype.pipeline import engine as pe
from nipype.interfaces import IdentityInterface


def test_calc_nrow_ncol():
    assert reportlets._calc_nrows_ncols(7) == (3, 7)
    assert reportlets._calc_nrows_ncols(8) == (3, 8)
    assert reportlets._calc_nrows_ncols(9) == (6, 8)


def test_get_row_cal():
    for i in range(3):
        for j in range(7):
            assert reportlets._get_row_col(i, j, 7) == (i, j)
    for i in range(3):
        for j in range(8):
            assert reportlets._get_row_col(i, j, 12) == (i * 2, j)
        for j in range(8, 12):
            assert reportlets._get_row_col(i, j, 12) == (i * 2 + 1, j - 8)


def test_read_dists(tmp_path):
    distfile = tmp_path / 'dists.txt'
    distfile.write_text('value\tindex\n1.5\t1\n2.0\t1\n1.5\t2')
    dist = reportlets._read_dists(distfile)
    assert dist == {1: [1.5, 2.0], 2: [1.5]}


def test_distributions(tmp_path):
    distfile = tmp_path / 'dists.txt'
    distfile.write_text('value\tindex\n1.5\t1\n2.0\t1')
    outfile = tmp_path / 'out.txt'
    labelfile = tmp_path / 'labels.tsv'
    labelfile.write_text('index\tname\n1\tGM\n')
    reportlets.distributions('testdist', distfile, outfile, labelfile)


def test_distributions_dne(tmp_path):
    outfile = tmp_path / 'out.txt'
    labelfile = tmp_path / 'labels.tsv'
    labelfile.write_text('index\tname\n1\tGM\n')
    reportlets.distributions('testdist', None, outfile, labelfile)


@pytest.fixture()
def images(tmp_path):
    image1 = str(tmp_path / 'image1.nii')
    image2 = str(tmp_path / 'image2.nii')
    nibabel.Nifti1Image(np.array([[[1, 2, 3, 4]]]).reshape(1, 2, 2), np.eye(4)).to_filename(image1)
    nibabel.Nifti1Image(np.arange(8).reshape(2, 2, 2), np.eye(4)).to_filename(image2)
    image3 = None
    return tmp_path, image1, image2, image3


def test_single(images):
    tmp_path, image1, image2, image3 = images
    outfile = tmp_path / 'out.txt'
    reportlets.single('testsingle', image1, outfile, nslices=1)
    reportlets.single('testsingle', image3, outfile, nslices=1)


def test_contour(images):
    tmp_path, image1, image2, image3 = images
    outfile = tmp_path / 'out.txt'
    reportlets.contours('testcontours', image3, image2, outfile, nslices=1)
    reportlets.contours('testcontours', image2, image2, outfile, nslices=1)


def test_compare(images):
    tmp_path, image1, image2, image3 = images
    outfile = tmp_path / 'out.txt'
    reportlets.compare('testcompare', image1, 'testcompare2', image2, outfile, nslices=1)
    reportlets.compare('testcompare', image3, 'testcompare2', image2, outfile, nslices=1)
    reportlets.compare('testcompare', image2, 'testcompare2', image3, outfile, nslices=1)


def test_crash(tmp_path):
    fakenode = pe.Node(IdentityInterface(['field1']), 'name')
    traceback = ['test\n', 'string\n']
    pklfile = tmp_path / 'test.pklz'
    outfile = tmp_path / 'out.txt'
    nputils.filemanip.savepkl(str(pklfile), {'node': fakenode, 'traceback': traceback}, versioning=True)
    reportlets.crash('testcrash', [str(pklfile)], str(outfile))
    outstr = outfile.read_text()
    assert 'class="crash"' in outstr
    assert 'class="success"' not in outstr
    reportlets.crash('testcrash', [], str(outfile))
    outstr = outfile.read_text()
    assert 'class="crash"' not in outstr
    assert 'class="success"' in outstr


def test_doublemap():
    mylist = [[1, 2, 3], [4, 5]]
    assert reportlets.doublemap(lambda x: 2 * x, mylist) == [[2, 4, 6], [8, 10]]


def test_doublezip():
    mylist = [[1, 2, 3], [4, 5]]
    mylist2 = [[6, 7, 8], [9, 10]]
    assert reportlets.doublezip(mylist, mylist2) == [[(1, 6), (2, 7), (3, 8)], [(4, 9), (5, 10)]]
