from setuptools import setup, find_packages


setup(
    name='PipelineQC',
    version='dev',
    install_requires=[
        'nipype @ git+https://github.com/stilley2/nipype.git@ac54739effc8fdd7d89a57b5aac91b3f7cefd760',
        'pndniworkflows @ git+https://github.com/pndni/pndniworkflows.git',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    extra_require={
        'doc': ['Sphinx', 'sphinx-argparse', 'sphinx-rtd-theme']
    },
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'PipelineQC = PipelineQC.main:run',
        ]
    }
)
