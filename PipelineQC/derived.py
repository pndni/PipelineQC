import nibabel
import tempfile
import os


def procderived(conf, filesdict):
    if 'derived' not in conf:
        return
    for key, files in filesdict.items():
        for derivedkey, derivedval in conf['derived'].items():
            if all([r in files for r in derivedval['requires']]):
                images = [nibabel.load(str(files[r])) for r in derivedval['requires']]
                inputs = [image.get_fdata() for image in images]
                expr = derivedval['expr']
                varmap = {r: inputs[i] for i, r in enumerate(derivedval['requires'])}
                tmp = eval(expr, None, varmap)
                _, outfile = tempfile.mkstemp(suffix='.nii', prefix='PipelineQCderived')
                nibabel.Nifti1Image(tmp, images[0].affine).to_filename(outfile)
                filesdict[key][derivedkey] = outfile


def removederived(conf, filesdict):
    if 'derived' not in conf:
        return
    for key in filesdict.keys():
        for derivedkey in conf['derived'].keys():
            if derivedkey in filesdict[key]:
                os.remove(filesdict[key][derivedkey])
