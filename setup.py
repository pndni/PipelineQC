from setuptools import setup, find_packages


setup(
    name='PipelineQC',
    version='dev',
    install_requires=[
        'nipype==1.2.2',
        'matplotlib>=3',
        'Jinja2>=2.10.1',
        'nibabel>=2.4.0',
        'jsonschema',
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
