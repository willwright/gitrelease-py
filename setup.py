from setuptools import setup

setup(
    name='gitrelease-py',
    version='0.1',
    py_modules=['main'],
    install_requires=[
        'Click'
    ],
    entry_points='''
        [console_scripts]
        gitrelease-py=main:cli
    ''',
)