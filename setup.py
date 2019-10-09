from setuptools import setup, find_packages


setup(
    name='PipelineQC',
    version='dev',
    install_requires=[
        'nipype @ https://github.com/stilley2/nipype/archive/1.2.3-mod.zip',
        'matplotlib>=3',
        'Jinja2>=2.10.1',
        'nibabel>=2.4.0',
        'nilearn',
        'jsonschema',
        'pybids>=0.9.4',
        'scikit-learn>=0.19',
        'scipy>=0.19',
        'numpy>=1.11'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    extras_require={
        'doc': ['Sphinx', 'sphinx-argparse', 'sphinx-rtd-theme', 'pndniworkflows @ git+https://github.com/pndni/pndniworkflows.git']
    },
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'PipelineQC = PipelineQC.main:run',
        ]
    },
    package_data={
        '': ['templates/*tpl', 'schema/config.json']
    },
)
