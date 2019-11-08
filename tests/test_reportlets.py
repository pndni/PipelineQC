from PipelineQC import reportlets, interfaces
import nibabel
import numpy as np
import pytest
from nipype import utils as nputils
from nipype.pipeline import engine as pe
from nipype.interfaces import IdentityInterface
from pathlib import Path


def test_calc_nrow_ncol():
    assert reportlets._calc_nrows_ncols(7, 8) == (3, 7)
    assert reportlets._calc_nrows_ncols(8, 8) == (3, 8)
    assert reportlets._calc_nrows_ncols(9, 8) == (6, 8)


def test_get_row_cal():
    for i in range(3):
        for j in range(7):
            assert reportlets._get_row_col(i, j, 7, 8) == (i, j)
    for i in range(3):
        for j in range(8):
            assert reportlets._get_row_col(i, j, 12, 8) == (i * 2, j)
        for j in range(8, 12):
            assert reportlets._get_row_col(i, j, 12, 8) == (i * 2 + 1, j - 8)


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
    reportlets.distributions(name='testdist',
                             distsfile=distfile,
                             out_file=outfile,
                             labelfile=labelfile)
    i = interfaces.Distributions(name='testdist',
                                 distsfile=distfile,
                                 labelfile=labelfile)
    i.run()


def test_distributions_dne(tmp_path):
    outfile = tmp_path / 'out.txt'
    labelfile = tmp_path / 'labels.tsv'
    labelfile.write_text('index\tname\n1\tGM\n')
    reportlets.distributions(name='testdist',
                             distsfile=None,
                             out_file=outfile,
                             labelfile=labelfile)


@pytest.fixture()
def images(tmp_path):
    image1 = str(tmp_path / 'image1.nii')
    image2 = str(tmp_path / 'image2.nii')
    nibabel.Nifti1Image(
        np.array([[[1, 2, 3, 4]]]).reshape(1, 2, 2),
        np.eye(4)).to_filename(image1)
    nibabel.Nifti1Image(np.arange(8).reshape(2, 2, 2),
                        np.eye(4)).to_filename(image2)
    image3 = None
    return tmp_path, image1, image2, image3


def test_single(images):
    tmp_path, image1, image2, image3 = images
    outfile = tmp_path / 'out.txt'
    reportlets.single(name='testsingle',
                      image=image1,
                      out_file=outfile,
                      nslices=1)
    reportlets.single(name='testsingle',
                      image=image3,
                      out_file=outfile,
                      nslices=1)
    i = interfaces.Single(name='testsingle', image=image1, nslices=1)
    i.run()


@pytest.mark.parametrize('contour_levels', [None, [1e-3]])
@pytest.mark.parametrize('slice_to_label', [False, True])
def test_contour(images, slice_to_label, contour_levels):
    tmp_path, image1, image2, image3 = images
    outfile = tmp_path / 'out.txt'
    reportlets.contours(name='testcontours',
                        image=image3,
                        labelimage=image2,
                        out_file=outfile,
                        slice_to_label=slice_to_label,
                        contour_levels=contour_levels,
                        nslices=1)
    reportlets.contours(name='testcontours',
                        image=image2,
                        labelimage=image2,
                        out_file=outfile,
                        slice_to_label=slice_to_label,
                        contour_levels=contour_levels,
                        nslices=1)
    i = interfaces.Contour(name='testcontours',
                           image=image3,
                           labelimage=image2,
                           slice_to_label=slice_to_label,
                           contour_levels=contour_levels,
                           nslices=1)
    i.run()


@pytest.mark.parametrize('transparency', [0.2, 0.5])
@pytest.mark.parametrize('slice_to_label', [False, True])
def test_overlay(images, slice_to_label, transparency):
    tmp_path, image1, image2, image3 = images
    outfile = tmp_path / 'out.txt'
    reportlets.overlay(name='testoverlay',
                       image=image3,
                       labelimage=image2,
                       out_file=outfile,
                       slice_to_label=slice_to_label,
                       transparency=transparency,
                       nslices=1)
    reportlets.overlay(name='testoverlay',
                       image=image2,
                       labelimage=image2,
                       out_file=outfile,
                       slice_to_label=slice_to_label,
                       transparency=transparency,
                       nslices=1)
    i = interfaces.Overlay(name='testoverlay',
                           image=image3,
                           labelimage=image2,
                           slice_to_label=slice_to_label,
                           transparency=transparency,
                           nslices=1)
    i.run()


@pytest.mark.parametrize('slice_to_probmap', [False, True])
def test_probmap(images, slice_to_probmap):
    tmp_path, image1, image2, image3 = images
    outfile = tmp_path / 'out.txt'
    reportlets.probmap(name='testprobmap',
                       image=image3,
                       probmapimage=image2,
                       out_file=outfile,
                       slice_to_probmap=slice_to_probmap,
                       nslices=1)
    reportlets.probmap(name='testprobmap',
                       image=image2,
                       probmapimage=image2,
                       out_file=outfile,
                       slice_to_probmap=slice_to_probmap,
                       nslices=1)
    i = interfaces.ProbMap(name='testprobmap',
                           image=image3,
                           probmapimage=image2,
                           slice_to_probmap=slice_to_probmap,
                           nslices=1)
    i.run()


@pytest.mark.parametrize('slice_to_image2', [False, True])
def test_compare(images, slice_to_image2):
    tmp_path, image1, image2, image3 = images
    outfile = tmp_path / 'out.txt'
    reportlets.compare(name1='testcompare',
                       image1=image1,
                       name2='testcompare2',
                       image2=image2,
                       out_file=outfile,
                       slice_to_image2=slice_to_image2,
                       nslices=1)
    reportlets.compare(name1='testcompare',
                       image1=image3,
                       name2='testcompare2',
                       image2=image2,
                       out_file=outfile,
                       slice_to_image2=slice_to_image2,
                       nslices=1)
    reportlets.compare(name1='testcompare',
                       image1=image2,
                       name2='testcompare2',
                       image2=image3,
                       out_file=outfile,
                       slice_to_image2=slice_to_image2,
                       nslices=1)
    i = interfaces.Compare(name1='testcompare',
                           image1=image1,
                           name2='testcompare2',
                           image2=image2,
                           slice_to_image2=slice_to_image2,
                           nslices=1)
    i.run()


def test_crash(tmp_path):
    fakenode = pe.Node(IdentityInterface(['field1']), 'name')
    traceback = ['test\n', 'string\n']
    pklfile = tmp_path / 'test.pklz'
    outfile = tmp_path / 'out.txt'
    nputils.filemanip.savepkl(str(pklfile), {
        'node': fakenode, 'traceback': traceback
    },
                              versioning=True)
    reportlets.crash(name='testcrash',
                     crashfiles=[str(pklfile)],
                     out_file=str(outfile))
    outstr = outfile.read_text()
    assert 'class="crash"' in outstr
    assert 'class="success"' not in outstr
    reportlets.crash(name='testcrash', crashfiles=[], out_file=str(outfile))
    outstr = outfile.read_text()
    assert 'class="crash"' not in outstr
    assert 'class="success"' in outstr
    i = interfaces.Crash(name='testcrash', crashfiles=[str(pklfile)])
    r = i.run()
    outstr = Path(r.outputs.out_file).read_text()
    assert 'class="crash"' in outstr
    assert 'class="success"' not in outstr


def test_doublemap():
    mylist = [[1, 2, 3], [4, 5]]
    assert reportlets.doublemap(lambda x: 2 * x, mylist) == [[2, 4, 6],
                                                             [8, 10]]


def test_doublezip():
    mylist = [[1, 2, 3], [4, 5]]
    mylist2 = [[6, 7, 8], [9, 10]]
    assert reportlets.doublezip(mylist, mylist2) == [[(1, 6), (2, 7), (3, 8)],
                                                     [(4, 9), (5, 10)]]
