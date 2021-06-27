# Automatically created by: scrapydd
from setuptools import setup, find_packages

def read_requirements():
    with open('requirements.txt', 'r') as f:
        return f.readlines()

setup(
    name='freedb',
    version='0.2.1',
    packages=find_packages(),
    package_data = {
        'frontend': [
            'templates/frontend/*',
            'static/frontend/*',
        ],
        'freedb_site': ['staticfiles/*', 'staticfiles/**/*'],
    },
    install_requires=read_requirements(),
)
