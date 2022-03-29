from setuptools import find_packages, setup

from src.nakamoto_explorer import __version__

with open('requirements.in') as file:
    requirements = file.read().splitlines()

setup(
    name='nakamoto_explorer',
    version=__version__,
    description='Explosion Fear Reignhood package: cryptocurrency manager - Explorer',
    author='Carlos Pinto Pérez',
    author_email='carlosp-p@hotmail.com',
    packages=find_packages(where='src', include=['nakamoto_explorer*']),
    package_dir={'': 'src'},
    include_package_data=True,
    package_data={'': ['*.ini']},
    install_requires=requirements
)
