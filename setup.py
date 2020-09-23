__author__ = "Markus Pichler"
__credits__ = ["Markus Pichler"]
__maintainer__ = "Markus Pichler"
__email__ = "markus.pichler@tugraz.at"
__version__ = "0.1"
__license__ = "MIT"

from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='swmm-api',
    version='0.1.alpha14',
    packages=['swmm_api',
              'swmm_api.report_file',
              'swmm_api.output_file',
              'swmm_api.input_file',
              'swmm_api.input_file.helpers',
              'swmm_api.input_file.misc'],
    url='https://gitlab.com/markuspichler/swmm_api',
    license='MIT',
    author='Markus Pichler',
    author_email='markus.pichler@tugraz.at',
    description='US-EPA-SWMM python interface',
    # scripts=['bin/idf_analysis'],
    install_requires=requirements,
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
