from setuptools import setup, find_packages

setup(
    name='protect',
    version='0.1',
    python_requires='>=3.8',
    packages=find_packages(),
    package_data={'protect': ['py.typed']},
    include_package_data=True,
    install_requires=[
        'pytest',
        'pytest-mypy',
        'pyyaml',
        'colorama',
        'pid',
        'coverage',
    ],
    entry_points='''
        [console_scripts]
        protect=src.cli:entrypoint
    ''',

    author="Preston Hunt",
    author_email="me@prestonhunt.com",
    description="Protect",
    keywords="chunk chunk-based backup asymmetric public-key lockss",
    url="https://github.com/presto8/protect",
)
