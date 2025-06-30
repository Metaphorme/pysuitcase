import os
from setuptools import setup, find_packages

setup(
    name="pysuitcase",
    version="0.0.1",
    packages=find_packages(),
    author="Heqi Liu, Liming Gao",
    author_email="heqiliu@stu.cpu.edu.cn, glm@stu.cpu.edu.cn",
    description="A tool to package Python applications into standalone executables on Windows.",
    long_description=open('README.md', encoding='utf-8').read() if os.path.exists('README.md') else '',
    long_description_content_type="text/markdown",
    url="https://github.com/metaphorme/pysuitcase",
    license="MIT",
    license_file="LICENSE",
    entry_points={
        'console_scripts': [
            'pysuitcase = pysuitcase.cli:main',
        ],
    },
    install_requires=[
        'click',
        'requests',
        'Cython'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
)