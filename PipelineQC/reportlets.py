import numpy as np
import nibabel
from nilearn.image import resample_to_img
from matplotlib import figure
from matplotlib import gridspec
from matplotlib import style
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.backends.backend_agg import FigureCanvasAgg
from io import StringIO, BytesIO
import jinja2
import re
import csv
from collections import defaultdict
import os
from nipype import utils as nputils
from pndniworkflows import utils
from copy import deepcopy
from pathlib import Path
from scipy import ndimage
import traceback
import sys

ORIENTATION = [[2, 1], [1, 1], [0, 1]]
PLOTSIZE = 5, 4

# https://github.com/matplotlib/matplotlib/blob/master/lib/matplotlib/_cm.py
COLORLIST = ((0.89411764705882357, 0.10196078431372549, 0.10980392156862745),
             (0.21568627450980393, 0.49411764705882355, 0.72156862745098038),
             (0.30196078431372547, 0.68627450980392157, 0.29019607843137257),
             (0.59607843137254901, 0.30588235294117649,
              0.63921568627450975), (1.0, 0.49803921568627452,
                                     0.0), (1.0, 1.0, 0.2),
             (0.65098039215686276, 0.33725490196078434,
              0.15686274509803921), (0.96862745098039216,
                                     0.50588235294117645,
                                     0.74901960784313726),
             (0.4, 0.76078431372549016,
              0.6470588235294118), (0.9882352941176471,
                                    0.55294117647058827,
                                    0.3843137254901961), (0.55294117647058827,
                                                          0.62745098039215685,
                                                          0.79607843137254897),
             (0.90588235294117647, 0.54117647058823526, 0.76470588235294112),
             (0.65098039215686276, 0.84705882352941175,
              0.32941176470588235), (1.0,
                                     0.85098039215686272,
                                     0.18431372549019609),
             (0.89803921568627454, 0.7686274509803922,
              0.58039215686274515),
             (0.55294117647058827, 0.82745098039215681,
              0.7803921568627451), (1.0, 1.0, 0.70196078431372544),
             (0.74509803921568629, 0.72941176470588232,
              0.85490196078431369), (0.98431372549019602,
                                     0.50196078431372548,
                                     0.44705882352941179),
             (0.50196078431372548, 0.69411764705882351,
              0.82745098039215681), (0.99215686274509807,
                                     0.70588235294117652,
                                     0.3843137254901961),
             (0.70196078431372544, 0.87058823529411766,
              0.41176470588235292), (0.9882352941176471,
                                     0.80392156862745101,
                                     0.89803921568627454),
             (0.73725490196078436, 0.50196078431372548, 0.74117647058823533),
             (0.8, 0.92156862745098034,
              0.77254901960784317), (1.0,
                                     0.92941176470588238,
                                     0.43529411764705883))


def _load_and_orient(fname):
    x = nibabel.load(str(fname))
    orn = nibabel.orientations.io_orientation(x.affine)
    difforn = nibabel.orientations.ornt_transform(orn, ORIENTATION)
    y = x.as_reoriented(difforn)
    assert nibabel.orientations.aff2axcodes(y.affine) == ('S', 'A', 'R')
    return y


def _calcslices(s, nslices, allow_less_slices=False):
    if nslices == 1:
        return [s // 2]
    step = (s - 1) // (nslices - 1)
    if step == 0:
        if allow_less_slices:
            return list(range(s))
        else:
            raise RuntimeError('step size is 0. nslices is probably too large')
    last = (nslices - 1) * step
    offset = (s - last - 1) // 2
    last += offset
    start = offset
    return list(range(start, last + 1, step))


def _calc_all_label_slices(nilabel, nslices):
    slices = ndimage.find_objects(nilabel.get_fdata() > 0)
    assert len(slices) == 1
    slices = slices[0]
    out_slices = [
        list(
            map(lambda x: x + s.start,
                _calcslices(s.stop - s.start, nslices,
                            allow_less_slices=True))) for s in slices
    ]
    return out_slices


def _get_vlims(x, frac):
    vals = np.sort(x.ravel())
    vals = vals[vals > 0]
    ind = int(frac * len(vals))
    return 0.0, vals[ind]


def _calc_nrows_ncols(nslices, maxcols):
    nrows_per_view = int(np.ceil(nslices / maxcols))
    return nrows_per_view * 3, min(nslices, maxcols)


def _get_row_col(viewnum, slicenum, nslices, maxcols):
    nrows_per_view = int(np.ceil(nslices / maxcols))
    row = viewnum * nrows_per_view + slicenum // maxcols
    col = slicenum % maxcols
    return row, col


def _resample(img, reference, atol, rtol):
    if img.shape == reference.shape and np.allclose(
            img.affine, reference.affine, atol=atol, rtol=rtol):
        return img
    return resample_to_img(img, reference)


def imshowfig(*,
              niimg,
              nslices=7,
              image_width=1.5,
              image_height=1.5,
              maxcols=8,
              contour_width=1.5,
              nilabel=None,
              separate_figs=False,
              reference=None,
              all_slice_locations=None,
              max_intensity_fraction=0.99,
              labeldisplay='contour',
              affine_absolute_tolerance=1e-3,
              affine_relative_tolerance=1e-5,
              transparency=0.5,
              contour_levels=None):
    """Create a figure (or nested list of figures) from imgfile

    :param niimg: image
    :type niimg: :py:class:`nibabel.Nifti1Image`
    :param nslices: The number of slices per view
    :type nslices: int
    :param image_width: The width of each axes/image (in.)
    :type image_width: float
    :param image_height: The width of each axes/image (in.)
    :type image_height: float
    :param maxcols: The maximum number of columns
                         (only when spearate_figs is False)
    :type maxcols: int
    :param contour_width: The width of contour lines (pts.)
    :type contour_width: float
    :param nilabel: Image of labels readable by nibabel
    :type nilabel: :py:class:`nibabel.Nifti1Image`
    :param separate_figs: Whether to create separate figures for
                          each image
    :type separate_figs: bool
    :param reference: Resample niimg to this reference image
    :type reference: :py:class:`nibabel.Nifti1Image`
    :param all_slice_locations: where to slice each axis
    :type all_slice_locations: list of list of int
    :param max_intensity_fraction: The intensity display range is 0, max where max
                                   is calculated as:

                                   .. code-block:: python

                                      vals = np.sort(niimg.get_fdata()).ravel()
                                      vals = vals[vals > 0]
                                      max = vals[int(len(vals) * max_intensity_fraction)]

    :type max_intensity_fraction: float
    :param labeldisplay: How to display nilabel. Either contour, overlay, probmap, or contour_nonzero
    :type labeldisplay: str
    :name affine_absolute_tolerance: pass to numpy.allclose as atol
    :type affine_absolute_tolerance: float
    :name affine_relative_tolerance: pass to numpy.allclose as rtol
    :type affine_relative_tolerance: float
    :name transparency: Transparency over overlay
    :type transparency: float
    :name contour_levels: The levels at which to draw the contours.
    :type contour_levels: list
    :return: :py:obj:`matplotlib.figure.Figure` or a list of lists of
             :py:obj:`matplotlib.figure.Figure`
    """
    colorlist = COLORLIST
    if nilabel is not None:
        if labeldisplay == 'contour_nonzero' and contour_levels is not None:
            raise ValueError('If contour_levels is set contour_nonzero must be False')
        if reference is not None:
            raise ValueError(
                'Only one of labelfile and reference may be specified')
        if nilabel.shape != niimg.shape:
            raise RuntimeError('label shape does not match image shape')
        if not np.allclose(nilabel.affine,
                           niimg.affine,
                           atol=affine_absolute_tolerance,
                           rtol=affine_relative_tolerance):
            raise RuntimeError('label affine does not match image affine')
        if labeldisplay in ['contour', 'overlay'] and contour_levels is None:
            labelvals = list(np.unique(np.asarray(nilabel.dataobj)))
            if 0 in labelvals:
                labelvals.pop(labelvals.index(0))
            if len(labelvals) > len(colorlist):
                raise RuntimeError('Not enough defined colors for label image')
        elif labeldisplay == 'contour' and contour_levels is not None:
            if len(contour_levels) > len(colorlist):
                raise RuntimeError('Not enough defined colors for contour_levels')
    if reference is not None:
        niimg = _resample(niimg,
                          reference,
                          affine_absolute_tolerance,
                          affine_relative_tolerance)
    with style.context({
            'image.origin': 'lower',
            'image.cmap': 'Greys_r',
            'axes.facecolor': 'black',
            'figure.facecolor': 'black',
            'figure.dpi': int(
                np.ceil(np.max(niimg.shape) / min(image_width, image_height)))
    }):
        if separate_figs:
            fig_list = []
        else:
            nrows, ncols = _calc_nrows_ncols(nslices, maxcols)
            fig = figure.Figure(figsize=(ncols * image_width,
                                         nrows * image_height))
            gs = gridspec.GridSpec(nrows,
                                   ncols,
                                   figure=fig,
                                   hspace=0.05,
                                   wspace=0.05,
                                   left=0,
                                   right=1,
                                   top=1,
                                   bottom=0)
        vmin, vmax = _get_vlims(niimg.get_fdata(), max_intensity_fraction)
        pitch = np.sqrt(np.sum(niimg.affine[:3, :3]**2.0, axis=0))
        for rowind, ind in enumerate([2, 0, 1]):
            if separate_figs:
                fig_list_row = []
            if all_slice_locations is None:
                slice_locations = _calcslices(niimg.shape[ind], nslices)
            else:
                slice_locations = all_slice_locations[ind]
            pitchtmp = list(pitch.copy())
            pitchtmp.pop(ind)
            aspect = pitchtmp[0] / pitchtmp[1]
            for colind, sl in enumerate(slice_locations):
                slicespec = tuple(
                    slice(sl, sl + 1) if i == ind else slice(None)
                    for i in range(3))
                imgslice = np.squeeze(np.asarray(
                    niimg.slicer[slicespec].dataobj),
                                      axis=(ind, ))
                if separate_figs:
                    fig = figure.Figure(figsize=(image_width, image_height),
                                        subplotpars=figure.SubplotParams(
                                            left=0, right=1, bottom=0, top=1))
                    ax = fig.add_subplot(1, 1, 1)
                else:
                    rowind_adj, colind_adj = _get_row_col(rowind, colind, nslices, maxcols)
                    ax = fig.add_subplot(gs[rowind_adj, colind_adj])
                ax.imshow(imgslice, vmin=vmin, vmax=vmax, aspect=aspect)
                ax.set_xticks([])
                ax.set_yticks([])
                if nilabel is not None:
                    labeldata = np.squeeze(np.asarray(
                        nilabel.slicer[slicespec].dataobj),
                                           axis=(ind, ))
                    if labeldisplay == 'contour':
                        if contour_levels is None:
                            for lvind, lv in enumerate(labelvals):
                                ax.contour(labeldata == lv,
                                           levels=[0.5],
                                           colors=[colorlist[lvind]],
                                           linewidths=[contour_width],
                                           aspect=aspect)
                        else:
                            ax.contour(labeldata,
                                       levels=contour_levels,
                                       colors=colorlist[:len(contour_levels)],
                                       linewidths=[contour_width] * len(contour_levels),
                                       aspect=aspect)
                    elif labeldisplay == 'contour_nonzero':
                        ax.contour(labeldata > 0,
                                   levels=[0.5],
                                   colors=colorlist[:1],
                                   linewidths=[contour_width],
                                   aspect=aspect)
                    elif labeldisplay == 'probmap':
                        probimage = np.ones([*labeldata.shape, 4]) * np.array(
                            [0.0, 1.0, 0.0, 0.0])
                        probimage[..., 3] = labeldata
                        ax.imshow(probimage, aspect=aspect)
                    elif labeldisplay == 'overlay':
                        overlay = np.zeros([*labeldata.shape, 4])
                        for lvind, lv in enumerate(labelvals):
                            color_alpha = np.array([*colorlist[lvind], transparency])
                            overlay[labeldata == lv, :] = color_alpha
                        ax.imshow(overlay, aspect=aspect)
                    else:
                        raise ValueError(
                            f'{labeldisplay} is not a valid option for labeldisplay'
                        )
                if separate_figs:
                    fig_list_row.append(fig)
            if separate_figs:
                fig_list.append(fig_list_row)
    if separate_figs:
        return fig_list
    else:
        return fig


def _to_svg(fig):
    out = StringIO()
    FigureCanvasSVG(fig).print_svg(out)
    out.seek(0)
    return out.read()


def _to_png(fig):
    out = BytesIO()
    FigureCanvasAgg(fig).print_png(out)
    out.seek(0)
    return out.read()


def doublemap(func, iterable):
    return list(map(lambda row: list(map(func, row)), iterable))


def doublezip(iterable1, iterable2):
    return [
        list(zip(rowleft, rowright)) for rowleft,
        rowright in zip(iterable1, iterable2)
    ]


def imshow_from_files(*, imagefile, labelfile=None, **kwargs):
    niimg = _load_and_orient(imagefile)
    if labelfile is not None:
        nilabel = _load_and_orient(labelfile)
    else:
        nilabel = None
    return _imshow(niimg=niimg, nilabel=nilabel, **kwargs)


def _imshow(*, outtype='svg', separate_figs=False, **kwargs):
    fig = imshowfig(separate_figs=separate_figs, **kwargs)
    if outtype == 'svg':
        func = _to_svg
    elif outtype == 'png':
        func = _to_png
    else:
        raise ValueError('unsupported outtype')
    if separate_figs:
        out = doublemap(func, fig)
    else:
        out = func(fig)
    return out


def _set_svg_class(svgstr, classname):
    return re.sub('<svg([^>]*)>',
                  lambda m: '<svg{} class="{}">'.format(m.group(1), classname),
                  svgstr,
                  count=1)


def _dump(filename, str_):
    with open(filename, 'w') as f:
        f.write(str_)


def _load(filename):
    with open(filename, 'r') as f:
        return f.read()


def _load_template(template):
    env = jinja2.Environment(
        loader=jinja2.PackageLoader('PipelineQC', 'templates'))
    return env.get_template(template)


def _render(out_file, template, data):
    template = _load_template(template)
    rend = template.render(data)
    _dump(out_file, rend)


def _single_opt_contours(name,
                         niimage,
                         imagefilename,
                         out_file,
                         nilabel=None,
                         labelfilename=None,
                         relative_dir=None,
                         description='',
                         **kwargs):
    out = {
        'name': name, 'name_no_spaces': name.replace(' ', '_')
    }
    out['svg'] = _imshow(niimg=niimage,
                         nilabel=nilabel,
                         separate_figs=True,
                         **kwargs)
    out['filename'] = str(imagefilename)
    out['formfile'] = 'form_simple.tpl'
    if description:
        out['description'] = description
    if nilabel is not None:
        if labelfilename is None:
            raise ValueError
        out['labelfilename'] = str(labelfilename)
    if relative_dir is not None:
        out['filename'] = os.path.relpath(out['filename'], relative_dir)
        if nilabel is not None:
            out['labelfilename'] = os.path.relpath(out['labelfilename'],
                                                   relative_dir)
    _render(out_file, 'single.tpl', out)


def single(*, name, image, out_file, relative_dir=None, description='', **kwargs):
    """Write an html file to :py:obj:`out_file` showing the :py:obj:`image`
    with :py:obj:`nslices` slices in all three axial planes

    :param name: Name describing :py:obj:`image`
    :type name: str
    :param image: Image file name to show (readable by :py:mod:`nibabel`)
    :type image: path-like object or :py:obj:`None`
    :param out_file: File name
    :type out_file: path-like object
    :param relative_dir: Create links to filenames relative to this directory
    :type relative_dir: path-like object
    :param description: Description of reportlet
    :type description: str

    keyword arguments are passed to imshowfig
    """
    if image is None:
        out = {
            'name': name,
            'name_no_spaces': name.replace(' ', '_')
        }
        if description:
            out['description'] = description
        out['errormessage'] = 'No image file for this reportlet'
        _render(out_file, 'single.tpl', out)
    else:
        try:
            niimage = _load_and_orient(image)
        except ValueError:
            out = {
                'name': name,
                'name_no_spaces': name.replace(' ', '_')
            }
            if description:
                out['description'] = description
            out['errormessage'] = 'Unable to load image.'
            out['errormessageverbatim'] = '\n'.join(traceback.format_tb(sys.exc_info()[2]))
            _render(out_file, 'single.tpl', out)
        else:
            _single_opt_contours(name,
                                 niimage,
                                 image,
                                 out_file,
                                 relative_dir=relative_dir,
                                 description=description,
                                 **kwargs)


def compare(*,
            name1,
            image1,
            name2,
            image2,
            out_file,
            relative_dir=None,
            slice_to_image2=False,
            nslices=7,
            max_intensity_fraction_image1=0.99,
            max_intensity_fraction_image2=0.99,
            description='',
            **kwargs):
    """Write an html file to :py:obj:`out_file` comparing :py:obj:`image1`
    with :py:obj:`image2` with :py:obj:`nslices` slices in all three axial planes

    :param name1: Name describing :py:obj:`image1`
    :type name1: str
    :param image1: Image file name to show (readable by :py:mod:`nibabel`)
    :type image1: path-like object or :py:obj:`None`
    :param name2: Name describing :py:obj:`image2`
    :type name2: str
    :param image2: Image file name to show (readable by :py:mod:`nibabel`)
    :type image2: path-like object or :py:obj:`None`
    :param out_file: File name
    :type out_file: path-like object
    :param relative_dir: Create links to filenames relative to this directory
    :type relative_dir: path-like object
    :param slice_to_image2: Calculate slices based on non-zero extent of image2
    :type slice_to_image2: bool
    :param nslices: Number of slices to show in each plane
    :type nslices: int
    :max_intensity_fraction_image1: see :py:func:`imshowfig`
    :type max_intensity_fraction_image1: float
    :max_intensity_fraction_image2: see :py:func:`imshowfig`
    :type max_intensity_fraction_image2: float
    :param description: Description of reportlet
    :type description: str

    keyword arguments are passed to imshowfig
    """

    out = {
        'name1': name1,
        'name2': name2,
        'name_no_spaces': '_'.join(
            [nametmp.replace(' ', '_') for nametmp in [name1, name2]])
    }
    if description:
        out['description'] = description

    if image1 is None or image2 is None:
        errormessages = []
        if image1 is None:
            errormessages.append('image1')
        if image2 is None:
            errormessages.append('image2')
        out['errormessage'] = ' and '.join(
            errormessages) + ' not specified for this reportlet.'
    else:
        # https://stackoverflow.com/questions/38083555/using-pathlibs-relative-to-for-directories-on-the-same-level
        if relative_dir is not None:
            out['filename1'] = str(os.path.relpath(image1, relative_dir))
            out['filename2'] = str(os.path.relpath(image2, relative_dir))
        else:
            out['filename1'] = str(image1)
            out['filename2'] = str(image2)

        errormessages = []
        try:
            niimage1 = _load_and_orient(image1)
        except ValueError:
            errormessages.append('\n'.join(traceback.format_tb(sys.exc_info()[2])))
        try:
            niimage2 = _load_and_orient(image2)
        except ValueError:
            errormessages.append('\n'.join(traceback.format_tb(sys.exc_info()[2])))
        if len(errormessages) > 0:
            out['errormessage'] = 'Unable to load image(s)'
            out['errormessageverbatim'] = '\n'.join(errormessages)
        else:
            if slice_to_image2:
                slice_locations = _calc_all_label_slices(niimage2, nslices)
                reference1 = niimage2
                reference2 = None
            else:
                slice_locations = None
                reference2 = niimage1
                reference1 = None
            svg1list = _imshow(
                niimg=niimage1,
                separate_figs=True,
                all_slice_locations=slice_locations,
                nslices=nslices,
                reference=reference1,
                max_intensity_fraction=max_intensity_fraction_image1,
                **kwargs)
            svg2list = _imshow(
                niimg=niimage2,
                separate_figs=True,
                reference=reference2,
                all_slice_locations=slice_locations,
                nslices=nslices,
                max_intensity_fraction=max_intensity_fraction_image2,
                **kwargs)

            svg1 = doublemap(lambda svgsingle: _set_svg_class(svgsingle, 'first'),
                             svg1list)
            svg2 = doublemap(lambda svgsingle: _set_svg_class(svgsingle, 'second'),
                             svg2list)
            out['svg'] = doublezip(svg1, svg2)
    _render(out_file, 'compare.tpl', out)


def overlay(*,
            name,
            image,
            labelimage,
            out_file,
            relative_dir=None,
            slice_to_label=False,
            nslices=7,
            description='',
            **kwargs):
    """Write an html file to :py:obj:`out_file` showing the :py:obj:`image`
    with :py:obj:`nslices` slices in all three axial planes. Include an overaly
    of the areas defined by :py:obj:`labels`.

    :param name: Name describing :py:obj:`image`
    :type name: str
    :param image: Image file name to show (readable by :py:mod:`nibabel`)
    :type image: path-like object or :py:obj:`None`
    :param labelimage: Label file of overlays (readable by :py:mod:`nibabel`)
    :type labelimage: path-like object or :py:obj:`None`
    :param out_file: File name
    :type out_file: path-like object
    :param relative_dir: Create links to filenames relative to this directory
    :type relative_dir: path-like object
    :param slice_to_label: Calculate slices based on non-zero extent of labelimage
    :type slice_to_label: bool
    :param nslices: Number of slices to show in each plane
    :type nslices: int
    :param description: Description of reportlet
    :type description: str

    keyword arguments are passed to imshowfig
    """
    labeldisplay = 'overlay'
    _contours_or_probmap(name=name,
                         image=image,
                         labelimage=labelimage,
                         out_file=out_file,
                         labeldisplay=labeldisplay,
                         relative_dir=relative_dir,
                         slice_to_label=slice_to_label,
                         nslices=nslices,
                         description=description,
                         **kwargs)


def contours(*,
             name,
             image,
             labelimage,
             out_file,
             relative_dir=None,
             slice_to_label=False,
             nslices=7,
             description='',
             threshold_above_zero=False,
             **kwargs):
    """Write an html file to :py:obj:`out_file` showing the :py:obj:`image`
    with :py:obj:`nslices` slices in all three axial planes. Include contour
    lines outlining the areas defined by :py:obj:`labels`.

    :param name: Name describing :py:obj:`image`
    :type name: str
    :param image: Image file name to show (readable by :py:mod:`nibabel`)
    :type image: path-like object or :py:obj:`None`
    :param labelimage: Label file name to draw contours from (readable by :py:mod:`nibabel`)
    :type labelimage: path-like object or :py:obj:`None`
    :param out_file: File name
    :type out_file: path-like object
    :param relative_dir: Create links to filenames relative to this directory
    :type relative_dir: path-like object
    :param slice_to_label: Calculate slices based on non-zero extent of labelimage
    :type slice_to_label: bool
    :param nslices: Number of slices to show in each plane
    :type nslices: int
    :param description: Description of reportlet
    :type description: str
    :param threshold_above_zero: If true, threshold the image with >0 and draw a contour at 0.5
    :type threshold_above_zero: bool

    keyword arguments are passed to imshowfig
    """
    labeldisplay = 'contour_nonzero' if threshold_above_zero else 'contour'
    _contours_or_probmap(name=name,
                         image=image,
                         labelimage=labelimage,
                         out_file=out_file,
                         labeldisplay=labeldisplay,
                         relative_dir=relative_dir,
                         slice_to_label=slice_to_label,
                         nslices=nslices,
                         description=description,
                         **kwargs)


def probmap(*,
            name,
            image,
            probmapimage,
            out_file,
            relative_dir=None,
            slice_to_probmap=False,
            nslices=7,
            description='',
            **kwargs):
    """Write an html file to :py:obj:`out_file` showing the :py:obj:`image`
    with :py:obj:`nslices` slices in all three axial planes. Include probability
    map defined by :py:obj:`probmapimage`.

    :param name: Name describing :py:obj:`image`
    :type name: str
    :param image: Image file name to show (readable by :py:mod:`nibabel`)
    :type image: path-like object or :py:obj:`None`
    :param probmapimage: Probability map file name (readable by :py:mod:`nibabel`)
    :type probmapimage: path-like object or :py:obj:`None`
    :param out_file: File name
    :type out_file: path-like object
    :param relative_dir: Create links to filenames relative to this directory
    :type relative_dir: path-like object
    :param slice_to_probmap: Calculate slices based on non-zero extent of probmapimage
    :type slice_to_probmap: bool
    :param nslices: Number of slices to show in each plane
    :type nslices: int
    :param description: Description of reportlet
    :type description: str

    keyword arguments are passed to imshowfig
    """
    _contours_or_probmap(name=name,
                         image=image,
                         labelimage=probmapimage,
                         out_file=out_file,
                         labeldisplay='probmap',
                         relative_dir=relative_dir,
                         slice_to_label=slice_to_probmap,
                         nslices=nslices,
                         description=description,
                         **kwargs)


def _contours_or_probmap(*,
                         name,
                         image,
                         labelimage,
                         out_file,
                         labeldisplay,
                         relative_dir=None,
                         slice_to_label=False,
                         nslices=7,
                         description='',
                         **kwargs):
    if image is None or labelimage is None:
        out = {
            'name': name,
            'name_no_spaces': name.replace(' ', '_')
        }
        if description:
            out['description'] = description
        errormessages = []
        if image is None:
            errormessages.append('image')
        if labelimage is None:
            if labeldisplay == 'contour':
                errormessages.append('labelimage')
            elif labeldisplay == 'probmap':
                errormessages.append('probmap')
        out['errormessage'] = ' and '.join(
            errormessages) + ' not specified for this reportlet'
        _render(out_file, 'single.tpl', out)
    else:
        errormessages = []
        try:
            nilabel = _load_and_orient(labelimage)
        except ValueError:
            errormessages.append('\n'.join(traceback.format_tb(sys.exc_info()[2])))
        try:
            niimage = _load_and_orient(image)
        except ValueError:
            errormessages.append('\n'.join(traceback.format_tb(sys.exc_info()[2])))
        if len(errormessages) > 0:
            out = {
                'name': name,
                'name_no_spaces': name.replace(' ', '_')
            }
            if description:
                out['description'] = description
            out['errormessage'] = 'Failed to load image(s)'
            out['errormessageverbatim'] = '\n'.join(errormessages)
            _render(out_file, 'single.tpl', out)
        else:
            if slice_to_label:
                slice_locations = _calc_all_label_slices(nilabel, nslices)
            else:
                slice_locations = None
            _single_opt_contours(name,
                                 niimage,
                                 image,
                                 out_file,
                                 nilabel=nilabel,
                                 labelfilename=labelimage,
                                 relative_dir=relative_dir,
                                 all_slice_locations=slice_locations,
                                 nslices=nslices,
                                 labeldisplay=labeldisplay,
                                 description=description,
                                 **kwargs)


def _str2int(s):
    f = float(s)
    i = int(f)
    if f != i:
        raise ValueError(f'{s} is not an integer')
    return i


def _read_dists(distfile):
    dists = defaultdict(list)
    with open(distfile, 'r', newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        header = next(reader)
        valind = header.index('value')
        indexind = header.index('index')
        for row in reader:
            dists[_str2int(row[indexind])].append(float(row[valind]))
    return dists


def distributions(*,
                  name,
                  distsfile,
                  out_file,
                  labelfile,
                  relative_dir=None,
                  description=''):
    """Write an html file to :py:obj:`out_file` showing the distributions
    defined in :py:obj:`distsfile`.

    :param name: Name describing :py:obj:`distsfile`
    :type name: str
    :param distsfile: Distribution file name.
                     Must be a TSV file with two columns "value", and "index".
                     "value" is a point in distribution indexed by "index".
    :type distsfile: path-like object or :py:obj:`None`
    :param out_file: File name
    :type out_file: path-like object
    :param labelfile: TSV file containing "index" and "name" columns. Used to label
                      distributions. ("index" corresponds to the second column in
                      distsfile)
    :type labelfile: path-like object or :py:obj:`None`
    :param relative_dir: Create links to filenames relative to this directory
    :type relative_dir: path-like object
    :param description: Description of reportlet
    :type description: str
    """
    out = {
        'name': name,
        'name_no_spaces': name.replace(' ', '_'),
    }
    if description:
        out['description'] = description
    if distsfile is None or labelfile is None:
        errormessages = []
        if distsfile is None:
            errormessages.append('distsfile')
        if labelfile is None:
            errormessages.append('labelfile')
        out['errormessage'] = ' and '.join(
            errormessages) + ' not specified for this reportlet.'
    else:
        labelmap = utils.labels2dict(utils.read_labels(labelfile), 'name')
        dists = _read_dists(distsfile)
        out['svg'] = plotdists(dists, labelmap=labelmap)
        out['filename'] = str(distsfile)
        out['labelfilename'] = str(labelfile)
        if relative_dir is not None:
            out['filename'] = str(
                os.path.relpath(out['filename'], relative_dir))
            out['labelfilename'] = str(
                os.path.relpath(out['labelfilename'], relative_dir))
    _render(out_file, 'plot.tpl', out)


def plotdists(dists, labelmap=None, bins=20, alpha=0.5):
    svg = StringIO()
    fig = figure.Figure(figsize=PLOTSIZE)
    ax = fig.add_subplot(1, 1, 1)
    if labelmap is None:
        labelmap = {key: key for key in dists.keys()}
    for key, dist in dists.items():
        ax.hist(dist, bins=bins, alpha=alpha, label=labelmap[key])
    ax.legend()
    FigureCanvasSVG(fig).print_svg(svg)
    svg.seek(0)
    return svg.read()


def crash(*, name, crashfiles, out_file, relative_dir=None):
    """Write an html file to :py:obj:`out_file` with crashfile information.

    :param name: Name describing the reportlet
    :type name: str
    :param crashfiles: Files of a type readable by :py:obj:`nipype.utils.filemanip.loadcrash`
                       or a txt file.
                       An empty list indicates no crash files, and therefore success.
    :type crashfiles: list
    :param out_file: File name
    :type out_file: path-like object
    :param relative_dir: Create links to filenames relative to this directory
    :type relative_dir: path-like object
    """
    out = {
        'name': name, 'name_no_spaces': name.replace(' ', '_'), 'crashes': []
    }

    for cf in sorted(crashfiles):
        tmp = {}
        cfp = Path(cf)
        if cfp.suffix == '.txt':
            tmp['text'] = cfp.read_text()
        else:
            c = nputils.filemanip.loadcrash(cf)
            tmp['nodename'] = c['node'].name
            tmp['nodefullname'] = c['node'].fullname
            # https://stackoverflow.com/questions/510972/getting-the-class-name-of-an-instance#511059
            tmp['interface'] = type(c['node'].interface).__name__
            tmp['traceback'] = ''.join(c['traceback'])
        if relative_dir is not None:
            tmp['crashfile'] = str(os.path.relpath(cf, relative_dir))
        else:
            tmp['crashfile'] = str(cf)
        out['crashes'].append(tmp)
    _render(out_file, 'crash.tpl', out)


def rating(*, name, widgets, out_file):
    """Write an html file to :py:obj:`out_file` descripting a rating tool

    :param name: Name descripting the reportlet
    :type name: str
    :param widgets: List of dictionaries describing the different widgets
    :type widgets: list
    :param out_file: File name
    :type out_file: path-like object



    :Example:

    .. code-block:: python

       widgets = [{'type': 'radio',
                   'name': 'Overall',
                   'options': [{'name': 'Poor', 'value': 1},
                               {'name': 'Good', 'value': 2},
                               {'name': 'Excellent', 'value': 3}]},
                  {'type': 'checkbox',
                   'name': 'Notes',
                   'fields': ['Poor registration',
                              'Poor segmentation',
                              'Poor initial T1 quality']},
                  {'type': 'text',
                   'name': 'Other'}]
       rating('Rating', widgets, 'out.html')

    """
    out = {'widgets': [deepcopy(widget) for widget in widgets],
           'name': name}
    for k in range(len(out['widgets'])):
        out['widgets'][k]['name_no_spaces'] = out['widgets'][k]['name'].replace(' ', '_')
        out['widgets'][k]['name_'] = out['widgets'][k]['name']
        del out['widgets'][k]['name']
        if out['widgets'][k]['type'] == 'radio':
            for opt in out['widgets'][k]['options']:
                opt['name_'] = opt['name']
                del opt['name']
    _render(out_file, 'rating.tpl', out)


def assemble(*,
             out_file,
             in_files,
             title,
             prev=None,
             next_=None,
             relative_dir=None):
    """combine multiple html files into one file

    :param out_file: output html file
    :type out_file: path-like object
    :param in_files: list of input files to include
    :type in_files: list of path-like objects
    :param title: title of html page
    :type title: str
    :param prev: Name of previous qc page for linking
    :type prev: path-like object
    :param next: Name of next qc page for linking
    :type next: path-like object
    :param relative_dir: Create links to filenames relative to this directory
    :type relative_dir: path-like object
    """
    env = jinja2.Environment(
        loader=jinja2.PackageLoader('PipelineQC', 'templates'))
    template = env.get_template('base.tpl')
    body = '\n'.join((_load(in_f) for in_f in in_files))
    params = {'body': body, 'title': title}
    if prev is not None:
        params['prev'] = prev
        if relative_dir is not None:
            params['prev'] = os.path.relpath(params['prev'], relative_dir)
    if next_ is not None:
        params['next'] = next_
        if relative_dir is not None:
            params['next'] = os.path.relpath(params['next'], relative_dir)
    out = template.render(params)
    _dump(out_file, out)


def index(*, out_file, in_files, relative_dir=None):
    """
    Construct an html file linking all to other files

    :param out_file: output html file with links
    :type out_file: path-like object
    :param in_file: list of html files to link to from out_file
    :type in_file: list of path-like object
    :param relative_dir: Create links to filenames relative to this directory
    :type relative_dir: path-like object
    """
    env = jinja2.Environment(
        loader=jinja2.PackageLoader('PipelineQC', 'templates'))
    template = env.get_template('index.tpl')
    if relative_dir is not None:
        in_files = list(
            map(lambda in_file: os.path.relpath(in_file, relative_dir),
                in_files))
    out = template.render({'urls': in_files})
    _dump(out_file, out)
