from setuptools import setup, find_packages
from os import path
working_directory = path.abspath(path.dirname(__file__))

with open(path.join(working_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='tempfil', # name of packe which will be package dir below project
    version='0.0.1',
    url='https://github.com/yourname/yourproject',
    author='Adeniran Ibrahim',
    author_email='smartstudypatners@gmail.com',
    description='reconstruct missing LST pixels',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=["numpy", "scipy", "gdal", "pandas",
    ],
    extras_require= {
        "dev": ["pytest>=7.0", "twine>=4.0.2"]},
    keywords="Image processing, Landsat, Satellite images",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.9",
)