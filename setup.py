import ast
import tokenize

from setupext import setup


setup(
    name="mplinorm",
    description="Interactive contrast adjustment for Matplotlib images",
    long_description=ast.get_docstring(
        ast.parse(tokenize.open("lib/mplinorm.py").read())),
    author="Antony Lee",
    author_email="",
    url="",
    license="zlib",
    classifiers=[],
    py_modules=["mplinorm"],
    package_dir={"": "lib"},
    package_data={},
    python_requires="",
    setup_requires=["setuptools_scm"],
    use_scm_version=lambda: {
        "version_scheme": "post-release",
        "local_scheme": "node-and-date",
    },
    install_requires=[
        "matplotlib",
    ],
)
