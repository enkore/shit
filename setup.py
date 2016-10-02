from setuptools import setup

setup(
    name='shit',

    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    install_requires=['click'],

    description='shit utilities for git',
    long_description='shit utilities for git',

    url='https://github.com/enkore/shit',
    author='Marian Beermann',

    license='So called do-whatever-the-fuck-you-want license',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],

    py_modules=['shit'],
    entry_points = {
        'console_scripts': [
            'shit = shit:einscheißen',
        ],
    },
)
