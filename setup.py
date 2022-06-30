from setuptools import setup, find_packages

setup(
    name='store',
    version='0.1',
    python_requires='>=3.10',
    packages=find_packages(),
    package_data={'store': ['py.typed']},
    include_package_data=True,
    install_requires=[
        'msgpack-python',
        'attrs',
    ],
    entry_points='''
        [console_scripts]
        store=src.cli:entrypoint
    ''',

    author="Preston Hunt",
    author_email="me@prestonhunt.com",
    description="Store",
    keywords="chunk chunk-based backup asymmetric public-key lockss",
    url="https://github.com/presto8/store",
)
