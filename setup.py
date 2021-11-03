from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text()

setup(
    name='ficapi',
    version='0.1.0',
    description='Flexible InterConnect API Access Module',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='riceball-k',
    author_email='riceball@pnw.to',
    url='https://github.com/riceball-k/ficapi',
    license='Apache License, Version 2.0',
    packages=find_packages(),
    entry_points="""
      [console_scripts]
      create_ficapi_ini = ficapi.create_ini:main
    """,
    install_requires=(here / 'requirements.txt').read_text().splitlines(),
    python_requires='>=3.7',
)
