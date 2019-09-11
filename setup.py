from setuptools import setup, find_packages


setup(
    name='PipelineQC',
    version='dev',
    install_requires=[
        'nipype',
        'pndniworkflows',
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
