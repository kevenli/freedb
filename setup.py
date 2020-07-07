# Automatically created by: scrapydd
from setuptools import setup, find_packages

setup(
    name='freedb',
    version='0.0.1',
    packages=find_packages(),
    package_data = {
        'frontend': ['templates/frontend/*'],
        'freedb_site': ['staticfiles/*', 'staticfiles/**/*'],
    },
    install_requires=[
        'django',
        'pymongo',
        'djangorestframework',
        'django-cors-headers',
    ],
)
