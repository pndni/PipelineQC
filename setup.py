from setuptools import setup, find_packages


setup(
    name='PipelineQC',
    version='0.14.3',
    install_requires=[
        'nipype>=1.3.1',
        'matplotlib>=3',
        'Jinja2>=2.10.1',
        'nibabel>=2.4.0',
        'nilearn',
        'jsonschema',
        'pybids>=0.9.4',
        'scikit-learn>=0.19',
        'scipy>=0.19',
        'numpy>=1.11',
        'pndniworkflows @ git+https://github.com/pndni/pndniworkflows.git:c0b6ff33e43e49861e3e0a28409a6333028c39ee'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    extras_require={
        'doc': ['Sphinx', 'sphinx-argparse', 'sphinx-rtd-theme']
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
