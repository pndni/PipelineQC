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


class CompareInputSpec(BaseInterfaceInputSpec):
    name1 = traits.Str(mandatory=True, desc='Name of first image')
    name2 = traits.Str(mandatory=True, desc='Name of second image')
    image1 = traits.Either(
        File(exists=True, mandatory=True, desc='First image file'), None)
    image2 = traits.Either(
        File(exists=True, mandatory=True, desc='Second image file'), None)
    nslices = traits.Int(7, usedefault=True, desc='Number of slices to plot')
    qcform = traits.Bool(False,
                         usedefault=True,
                         desc='Include qc form in output')
    relative_dir = Directory(
        exists=True,
        desc='Create links to filenames relative to this directory')


class CompareOutputSpec(TraitedSpec):
    out_file = File(exists=True)


class Compare(SimpleInterface):
    input_spec = CompareInputSpec
    output_spec = CompareOutputSpec

    def _run_interface(self, runtime):
        out_file = str(Path('compare_{}_{}.txt'.format(self.inputs.name1,
                                                       self.inputs.name2)).resolve())
        if isdefined(self.inputs.relative_dir):
            relative_dir = self.inputs.relative_dir
        else:
            relative_dir = None
        reportlets.compare(self.inputs.name1,
                           self.inputs.image1,
                           self.inputs.name2,
                           self.inputs.image2,
                           out_file,
                           nslices=self.inputs.nslices,
                           form=self.inputs.qcform,
                           relative_dir=relative_dir)
        self._results['out_file'] = out_file
        return runtime


class ContourInputSpec(BaseInterfaceInputSpec):
    name = traits.Str(mandatory=True, desc='Name of image')
    image = traits.Either(File(exists=True, mandatory=True, desc='Image file'),
                          None)
    labelimage = traits.Either(
        File(exists=True,
             mandatory=True,
             desc='Label image to calculate contours'),
        None)
    nslices = traits.Int(7, usedefault=True, desc='Number of slices to plot')
    qcform = traits.Bool(False,
                         usedefault=True,
                         desc='Include qc form in output')
    relative_dir = Directory(
        exists=True,
        desc='Create links to filenames relative to this directory')


class ContourOutputSpec(TraitedSpec):
    out_file = File(exists=True)


class Contour(SimpleInterface):
    input_spec = ContourInputSpec
    output_spec = ContourOutputSpec

    def _run_interface(self, runtime):
        out_file = str(Path('contour_{}.txt'.format(self.inputs.name)).resolve())
        if isdefined(self.inputs.relative_dir):
            relative_dir = self.inputs.relative_dir
        else:
            relative_dir = None
        reportlets.contours(self.inputs.name,
                            self.inputs.image,
                            self.inputs.labelimage,
                            out_file,
                            nslices=self.inputs.nslices,
                            form=self.inputs.qcform,
                            relative_dir=relative_dir)
        self._results['out_file'] = out_file
        return runtime


class SingleInputSpec(BaseInterfaceInputSpec):
    name = traits.Str(mandatory=True, desc='Name of image')
    image = traits.Either(File(exists=True, mandatory=True, desc='Image file'),
                          None)
    nslices = traits.Int(7, usedefault=True, desc='Number of slices to plot')
    qcform = traits.Bool(False,
                         usedefault=True,
                         desc='Include qc form in output')
    relative_dir = Directory(
        exists=True,
        desc='Create links to filenames relative to this directory')


class SingleOutputSpec(TraitedSpec):
    out_file = File(exists=True)


class Single(SimpleInterface):
    input_spec = SingleInputSpec
    output_spec = SingleOutputSpec

    def _run_interface(self, runtime):
        out_file = str(Path('single_{}.txt'.format(self.inputs.name)).resolve())
        if isdefined(self.inputs.relative_dir):
            relative_dir = self.inputs.relative_dir
        else:
            relative_dir = None
        reportlets.single(self.inputs.name,
                          self.inputs.image,
                          out_file,
                          nslices=self.inputs.nslices,
                          form=self.inputs.qcform,
                          relative_dir=relative_dir)
        self._results['out_file'] = out_file
        return runtime


class DistributionsInputSpec(BaseInterfaceInputSpec):
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
        File(
            exists=True,
            desc=
            'TSV file with "index" and "name" columns. Used to label distributions '
            '("index" corresponds to the second column in distsfile)'),
        None)
    qcform = traits.Bool(False,
                         usedefault=True,
                         desc='Include qc form in output')
    relative_dir = Directory(
        exists=True,
        desc='Create links to filenames relative to this directory')


class DistributionsOutputSpec(TraitedSpec):
    out_file = File(exists=True)


class Distributions(SimpleInterface):
    input_spec = DistributionsInputSpec
    output_spec = DistributionsOutputSpec

    def _run_interface(self, runtime):
        out_file = str(Path('dists_{}.txt'.format(self.inputs.name)).resolve())
        if isdefined(self.inputs.relative_dir):
            relative_dir = self.inputs.relative_dir
        else:
            relative_dir = None
        reportlets.distributions(self.inputs.name,
                                 self.inputs.distsfile,
                                 out_file,
                                 self.inputs.labelfile,
                                 form=self.inputs.qcform,
                                 relative_dir=relative_dir)
        self._results['out_file'] = out_file
        return runtime


class CrashInputSpec(BaseInterfaceInputSpec):
    name = traits.Str(mandatory=True, desc='Name of reportlet')
    crashfiles = traits.List(File(exists=True, mandatory=True),
                             desc='List of nipype crash files (can be empty)')
    relative_dir = Directory(
        exists=True,
        desc='Create links to filenames relative to this directory')


class CrashOutputSpec(TraitedSpec):
    out_file = File(exists=True)


class Crash(SimpleInterface):
    input_spec = CrashInputSpec
    output_spec = CrashOutputSpec

    def _run_interface(self, runtime):
        out_file = str(Path('crash_{}.txt'.format(self.inputs.name)).resolve())
        if isdefined(self.inputs.relative_dir):
            relative_dir = self.inputs.relative_dir
        else:
            relative_dir = None
        reportlets.crash(self.inputs.name,
                         self.inputs.crashfiles,
                         out_file,
                         relative_dir=relative_dir)
        self._results['out_file'] = out_file
        return runtime


class RatingInputSpec(BaseInterfaceInputSpec):
    name = traits.Str(mandatory=True, desc='Name of first image')
    radio = traits.Either(
        traits.Dict(),
        None,
        desc='Description of the radio buttons for the reportlet. '
        'The dictionary must have "name" and "options" keys, '
        'where the value of name is a string and the value of '
        'options is a list of dictionaries, each with "name" '
        'and "value"')
    checkbox = traits.Either(
        traits.Dict(),
        None,
        desc='Description of the checkboxes for the reportlet. '
        'Must have "name" and "fields" keys, where "fields" '
        'is a list of names for different checkboxes.')
    text = traits.Either(traits.Dict(),
                         None,
                         desc='Description of the text field. '
                         'Only requires "name"')


class RatingOutputSpec(TraitedSpec):
    out_file = File(exists=True)


class Rating(SimpleInterface):
    input_spec = RatingInputSpec
    output_spec = RatingOutputSpec

    def _run_interface(self, runtime):
        out_file = str(Path('rating_{}.txt'.format(self.inputs.name)).resolve())
        reportlets.rating(self.inputs.name,
                          self.inputs.radio,
                          self.inputs.checkbox,
                          self.inputs.text,
                          out_file)
        self._results['out_file'] = out_file
        return runtime


class AssembleReportInputSpec(BaseInterfaceInputSpec):
    in_files = InputMultiPath(File(exists=True),
                              mandatory=True,
                              desc='Reportlet files')
    title = traits.Str(mandatory=True, desc='Title of final report')
    out_file = File(desc='Output file')
    qcform = traits.Bool(False,
                         usedefault=True,
                         desc='Include qc form submit button in output')
    next_ = File(desc='File name of next QC page')
    prev_ = File(desc='File name of previous QC page')
    relative_dir = Directory(
        exists=True,
        desc='Create links to filenames relative to this directory')


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
        reportlets.assemble(out_file,
                            self.inputs.in_files,
                            self.inputs.title,
                            form=self.inputs.qcform,
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
        reportlets.index(self.inputs.out_file, in_files)
        self._results['out_file'] = self.inputs.out_file
        return runtime
