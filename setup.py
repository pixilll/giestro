from setuptools import setup, find_packages

setup(
    name='giestro',
    version='1.0',
    author='dae',
    author_email='pixilreal@gmail.com',
    description='light-weight version control.',
    long_description='',
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
    install_requires=[],
    entry_points={
        'console_scripts': [
            'giestro=giestro.core:main'
        ]
    },
)
