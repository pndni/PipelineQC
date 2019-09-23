from nipype.interfaces.base import (File,
                                    Directory,
                                    TraitedSpec,
                                    traits,
                                    isdefined,
                                    BaseInterface,
                                    BaseInterfaceInputSpec,
                                    InputMultiPath)
import os
from pathlib import Path
from . import reportlets


class CompareInputSpec(BaseInterfaceInputSpec):
    name1 = traits.Str(mandatory=True, desc='Name of first image')
    name2 = traits.Str(mandatory=True, desc='Name of second image')
    image1 = traits.Either(File(exists=True, mandatory=True, desc='First image file'), None)
    image2 = traits.Either(File(exists=True, mandatory=True, desc='Second image file'), None)
    nslices = traits.Int(7, usedefault=True, desc='Number of slices to plot')
    qcform = traits.Bool(True, usedefault=True, desc='Include qc form in output')
    relative_dir = Directory(exists=True, desc='Create links to filenames relative to this directory')


class CompareOutputSpec(TraitedSpec):
    out_file = File(exists=True)


class Compare(BaseInterface):
    input_spec = CompareInputSpec
    output_spec = CompareOutputSpec

    def _run_interface(self, runtime):
        if isdefined(self.inputs.relative_dir):
            relative_dir = self.inputs.relative_dir
        else:
            relative_dir = None
        reportlets.compare(self.inputs.name1,
                           self.inputs.image1,
                           self.inputs.name2,
                           self.inputs.image2,
                           self._gen_outfilename(),
                           nslices=self.inputs.nslices,
                           form=self.inputs.qcform,
                           relative_dir=relative_dir)
        return runtime

    def _gen_outfilename(self):
        p = Path('compare_{}_{}.txt'.format(self.inputs.name1, self.inputs.name2)).resolve()
        return str(p)

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['out_file'] = self._gen_outfilename()
        return outputs


class ContourInputSpec(BaseInterfaceInputSpec):
    name = traits.Str(mandatory=True, desc='Name of image')
    image = traits.Either(File(exists=True, mandatory=True, desc='Image file'), None)
    labelimage = traits.Either(File(exists=True, mandatory=True, desc='Label image to calculate contours'), None)
    nslices = traits.Int(7, usedefault=True, desc='Number of slices to plot')
    qcform = traits.Bool(True, usedefault=True, desc='Include qc form in output')
    relative_dir = Directory(exists=True, desc='Create links to filenames relative to this directory')


class ContourOutputSpec(TraitedSpec):
    out_file = File(exists=True)


class Contour(BaseInterface):
    input_spec = ContourInputSpec
    output_spec = ContourOutputSpec

    def _run_interface(self, runtime):
        if isdefined(self.inputs.relative_dir):
            relative_dir = self.inputs.relative_dir
        else:
            relative_dir = None
        reportlets.contours(self.inputs.name,
                            self.inputs.image,
                            self.inputs.labelimage,
                            self._gen_outfilename(),
                            nslices=self.inputs.nslices,
                            form=self.inputs.qcform,
                            relative_dir=relative_dir)
        return runtime

    def _gen_outfilename(self):
        p = Path('contour_{}.txt'.format(self.inputs.name)).resolve()
        return str(p)

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['out_file'] = self._gen_outfilename()
        return outputs


class SingleInputSpec(BaseInterfaceInputSpec):
    name = traits.Str(mandatory=True, desc='Name of image')
    image = traits.Either(File(exists=True, mandatory=True, desc='Image file'), None)
    nslices = traits.Int(7, usedefault=True, desc='Number of slices to plot')
    qcform = traits.Bool(True, usedefault=True, desc='Include qc form in output')
    relative_dir = Directory(exists=True, desc='Create links to filenames relative to this directory')


class SingleOutputSpec(TraitedSpec):
    out_file = File(exists=True)


class Single(BaseInterface):
    input_spec = SingleInputSpec
    output_spec = SingleOutputSpec

    def _run_interface(self, runtime):
        if isdefined(self.inputs.relative_dir):
            relative_dir = self.inputs.relative_dir
        else:
            relative_dir = None
        reportlets.single(self.inputs.name,
                          self.inputs.image,
                          self._gen_outfilename(),
                          nslices=self.inputs.nslices,
                          form=self.inputs.qcform,
                          relative_dir=relative_dir)
        return runtime

    def _gen_outfilename(self):
        p = Path('single_{}.txt'.format(self.inputs.name)).resolve()
        return str(p)

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['out_file'] = self._gen_outfilename()
        return outputs


class DistributionsInputSpec(BaseInterfaceInputSpec):
    name = traits.Str(mandatory=True, desc='Name of distributions')
    distsfile = traits.Either(
                    File(exists=True, mandatory=True,
                         desc='File containing distributions. '
                              'Must be a comma-separated file with two columns and no heading. '
                              'The first column is a point in distribution, and the second '
                              'is an integer indicating which distribution it belongs to.'),
                    None)
    labelfile = traits.Either(
                    File(exists=True,
                         desc='TSV file with "index" and "name" columns. Used to label distributions '
                              '("index" corresponds to the second column in distsfile)'),
                    None)
    qcform = traits.Bool(True, usedefault=True, desc='Include qc form in output')
    relative_dir = Directory(exists=True, desc='Create links to filenames relative to this directory')


class DistributionsOutputSpec(TraitedSpec):
    out_file = File(exists=True)


class Distributions(BaseInterface):
    input_spec = DistributionsInputSpec
    output_spec = DistributionsOutputSpec

    def _run_interface(self, runtime):
        if isdefined(self.inputs.relative_dir):
            relative_dir = self.inputs.relative_dir
        else:
            relative_dir = None
        reportlets.distributions(self.inputs.name,
                                 self.inputs.distsfile,
                                 self._gen_outfilename(),
                                 self.inputs.labelfile,
                                 form=self.inputs.qcform,
                                 relative_dir=relative_dir)
        return runtime

    def _gen_outfilename(self):
        p = Path('dists_{}.txt'.format(self.inputs.name)).resolve()
        return str(p)

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['out_file'] = self._gen_outfilename()
        return outputs


class CrashInputSpec(BaseInterfaceInputSpec):
    name = traits.Str(mandatory=True, desc='Name of reportlet')
    crashfiles = traits.List(File(exists=True, mandatory=True),
                             desc='List of nipype crash files (can be empty)')
    relative_dir = Directory(exists=True, desc='Create links to filenames relative to this directory')


class CrashOutputSpec(TraitedSpec):
    out_file = File(exists=True)


class Crash(BaseInterface):
    input_spec = CrashInputSpec
    output_spec = CrashOutputSpec

    def _run_interface(self, runtime):
        if isdefined(self.inputs.relative_dir):
            relative_dir = self.inputs.relative_dir
        else:
            relative_dir = None
        reportlets.crash(self.inputs.name,
                         self.inputs.crashfiles,
                         self._gen_outfilename(),
                         relative_dir=relative_dir)
        return runtime

    def _gen_outfilename(self):
        p = Path('crash_{}.txt'.format(self.inputs.name)).resolve()
        return str(p)

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['out_file'] = self._gen_outfilename()
        return outputs


class AssembleReportInputSpec(BaseInterfaceInputSpec):
    in_files = InputMultiPath(File(exists=True), mandatory=True,
                              desc='Reportlet files')
    title = traits.Str(mandatory=True, desc='Title of final report')
    out_file = File(desc='Output file')
    next_ = File(desc='File name of next QC page')
    prev_ = File(desc='File name of previous QC page')
    relative_dir = Directory(exists=True, desc='Create links to filenames relative to this directory')


class AssembleReportOutputSpec(TraitedSpec):
    out_file = File(exists=True)


class AssembleReport(BaseInterface):
    input_spec = AssembleReportInputSpec
    output_spec = AssembleReportOutputSpec

    def _run_interface(self, runtime):
        next_ = self.inputs.next_ if isdefined(self.inputs.next_) else None
        prev = self.inputs.prev if isdefined(self.inputs.prev) else None
        reldir = self.inputs.relative_dir if isdefined(self.inputs.relative_dir) else None
        reportlets.assemble(self._gen_outfilename(), self.inputs.in_files, self.inputs.title,
                            next_=next_, prev=prev, relative_dir=reldir)
        return runtime

    def _gen_outfilename(self):
        if isdefined(self.inputs.out_file):
            p = Path(self.inputs.out_file).resolve()
        else:
            p = Path('report.html').resolve()
        return str(p)

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['out_file'] = self._gen_outfilename()
        return outputs


class IndexReportInputSpec(BaseInterfaceInputSpec):
    in_files = InputMultiPath(File(exists=True), mandatory=True,
                              desc='QC pages')
    out_file = File(mandatory=True,
                    desc='Name of output index file')


class IndexReportOutputSpec(TraitedSpec):
    out_file = File(exists=True)


class IndexReport(BaseInterface):
    input_spec = IndexReportInputSpec
    output_spec = IndexReportOutputSpec

    def _run_interface(self, runtime):
        # https://stackoverflow.com/questions/38083555/using-pathlibs-relative-to-for-directories-on-the-same-level
        out_dir = Path(self.inputs.out_file).parent
        in_files = [str(os.path.relpath(in_file, out_dir)) for in_file in self.inputs.in_files]
        reportlets.index(self.inputs.out_file, in_files)
        return runtime

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs['out_file'] = self.inputs.out_file
        return outputs
