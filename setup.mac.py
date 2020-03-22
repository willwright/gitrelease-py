from setuptools import setup, find_packages
import py2app

setup(
    name='gitrelease-py',
    version='0.1',
    author="Will Wright",
    author_email="will@willwright.tech",
    url="https://github.com/willwright/gitrelease-py",
    app="main.py",
    setup_requires=["py2app"],
    py_modules=['main'],
    packages=find_packages(),
    entry_points='''
        [console_scripts]
        gitrelease-py=main:cli
    ''',
)