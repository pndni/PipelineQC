from nipype.interfaces.base import (File,
                                    Directory,
                                    TraitedSpec,
                                    traits,
                                    isdefined,
                                    SimpleInterface,
                                    BaseInterfaceInputSpec,
                                    InputMultiPath)
import os
from pathlib import Path
from . import reportlets


class ReportletInputSpec(BaseInterfaceInputSpec):
    qcform = traits.Bool(False,
                         usedefault=True,
                         desc='Include qc form beneath each reportlet.')
    relative_dir = traits.Either(Directory(
        exists=True,
        desc='Create links to filenames relative to this directory'),
                                 None,
                                 default=None,
                                 usedefault=True)


class ReportletOutputSpec(TraitedSpec):
    out_file = File(exists=True)


class ImageGridReportletInputSpec(ReportletInputSpec):
    image_width = traits.Float(1.5,
                               usedefault=True,
                               desc='Image width (in inches)')
    image_height = traits.Float(1.5,
                                usedefault=True,
                                desc='Image height (in inches)')
    nslices = traits.Int(7, usedefault=True, desc='Number of slices to plot')


class Reportlet(SimpleInterface):
    output_spec = ReportletOutputSpec

    def _run_interface(self, runtime):
        out_file = str(Path('out_reportlet.txt').resolve())
        kwargs = {
            t: getattr(self.inputs, t)
            for t in self.inputs.visible_traits()
        }
        kwargs['out_file'] = out_file
        self._func(**kwargs)
        self._results['out_file'] = out_file
        return runtime


class CompareInputSpec(ImageGridReportletInputSpec):
    name1 = traits.Str(mandatory=True, desc='Name of first image')
    name2 = traits.Str(mandatory=True, desc='Name of second image')
    image1 = traits.Either(
        File(exists=True, mandatory=True, desc='First image file'), None)
    image2 = traits.Either(
        File(exists=True, mandatory=True, desc='Second image file'), None)
    slice_to_image2 = traits.Bool(False, usedefault=True,
                                  desc='If true, calculated slices based on '
                                  'non zero extent of image2')


class Compare(Reportlet):
    input_spec = CompareInputSpec
    _func = staticmethod(reportlets.compare)


class ContourInputSpec(ImageGridReportletInputSpec):
    name = traits.Str(mandatory=True, desc='Name of image')
    image = traits.Either(File(exists=True, mandatory=True, desc='Image file'),
                          None)
    labelimage = traits.Either(
        File(exists=True,
             mandatory=True,
             desc='Label image to calculate contours'),
        None)
    contour_width = traits.Float(1,
                                 usedefault=True,
                                 desc='Contour line width (in pts)')
    slice_to_label = traits.Bool(False, usedefault=True,
                                 desc='If true, calculated slices based on '
                                 'non zero extent of labelimage')


class Contour(Reportlet):
    input_spec = ContourInputSpec
    _func = staticmethod(reportlets.contours)


class SingleInputSpec(ImageGridReportletInputSpec):
    name = traits.Str(mandatory=True, desc='Name of image')
    image = traits.Either(File(exists=True, mandatory=True, desc='Image file'),
                          None)


class Single(Reportlet):
    input_spec = SingleInputSpec
    _func = staticmethod(reportlets.single)


class DistributionsInputSpec(ReportletInputSpec):
    name = traits.Str(mandatory=True, desc='Name of distributions')
    distsfile = traits.Either(
        File(exists=True,
             mandatory=True,
             desc='File containing distributions. '
             'Must be a comma-separated file with two columns and no heading. '
             'The first column is a point in distribution, and the second '
             'is an integer indicating which distribution it belongs to.'),
        None)
    labelfile = traits.Either(
        File(exists=True,
             desc='TSV file with "index" and "name" columns. '
             'Used to label distributions '
             '("index" corresponds to the second column in distsfile)'),
        None)


class Distributions(Reportlet):
    input_spec = DistributionsInputSpec
    _func = staticmethod(reportlets.distributions)


class CrashInputSpec(BaseInterfaceInputSpec):
    name = traits.Str(mandatory=True, desc='Name of reportlet')
    crashfiles = traits.List(File(exists=True, mandatory=True),
                             desc='List of nipype crash files (can be empty)')
    relative_dir = traits.Either(Directory(
        exists=True,
        desc='Create links to filenames relative to this directory'),
                                 None,
                                 default=None,
                                 usedefault=True)


class Crash(Reportlet):
    input_spec = CrashInputSpec
    _func = staticmethod(reportlets.crash)


class RatingInputSpec(BaseInterfaceInputSpec):
    name = traits.Str(mandatory=True, desc='Name of first image')
    radio = traits.Either(
        traits.Dict(),
        None,
        default=None,
        usedefault=True,
        desc='Description of the radio buttons for the reportlet. '
        'The dictionary must have "name" and "options" keys, '
        'where the value of name is a string and the value of '
        'options is a list of dictionaries, each with "name" '
        'and "value"')
    checkbox = traits.Either(
        traits.Dict(),
        None,
        default=None,
        usedefault=True,
        desc='Description of the checkboxes for the reportlet. '
        'Must have "name" and "fields" keys, where "fields" '
        'is a list of names for different checkboxes.')
    text = traits.Either(traits.Dict(),
                         None,
                         default=None,
                         usedefault=True,
                         desc='Description of the text field. '
                         'Only requires "name"')


class Rating(Reportlet):
    input_spec = RatingInputSpec
    _func = staticmethod(reportlets.rating)


class AssembleReportInputSpec(ReportletInputSpec):
    in_files = InputMultiPath(File(exists=True),
                              mandatory=True,
                              desc='Reportlet files')
    title = traits.Str(mandatory=True, desc='Title of final report')
    out_file = File(desc='Output file')
    next_ = File(desc='File name of next QC page')
    prev_ = File(desc='File name of previous QC page')


class AssembleReportOutputSpec(TraitedSpec):
    out_file = File(exists=True)


class AssembleReport(SimpleInterface):
    input_spec = AssembleReportInputSpec
    output_spec = AssembleReportOutputSpec

    def _run_interface(self, runtime):
        if isdefined(self.inputs.out_file):
            out_file = str(Path(self.inputs.out_file).resolve())
        else:
            out_file = str(Path('report.html').resolve())
        next_ = self.inputs.next_ if isdefined(self.inputs.next_) else None
        prev = self.inputs.prev if isdefined(self.inputs.prev) else None
        reldir = self.inputs.relative_dir if isdefined(
            self.inputs.relative_dir) else None
        reportlets.assemble(out_file=out_file,
                            in_files=self.inputs.in_files,
                            title=self.inputs.title,
                            qcform=self.inputs.qcform,
                            next_=next_,
                            prev=prev,
                            relative_dir=reldir)
        self._results['out_file'] = out_file
        return runtime


class IndexReportInputSpec(BaseInterfaceInputSpec):
    in_files = InputMultiPath(File(exists=True),
                              mandatory=True,
                              desc='QC pages')
    out_file = File(mandatory=True, desc='Name of output index file')


class IndexReportOutputSpec(TraitedSpec):
    out_file = File(exists=True)


class IndexReport(SimpleInterface):
    input_spec = IndexReportInputSpec
    output_spec = IndexReportOutputSpec

    def _run_interface(self, runtime):
        # https://stackoverflow.com/questions/38083555/using-pathlibs-relative-to-for-directories-on-the-same-level
        out_dir = Path(self.inputs.out_file).parent
        in_files = [
            str(os.path.relpath(in_file, out_dir))
            for in_file in self.inputs.in_files
        ]
        reportlets.index(out_file=self.inputs.out_file, in_files=in_files)
        self._results['out_file'] = self.inputs.out_file
        return runtime
