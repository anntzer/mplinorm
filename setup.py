from setupext import find_namespace_packages, setup


setup(
    name="mplinorm",
    description="",
    long_description=open("README.rst", encoding="utf-8").read(),
    author="Antony Lee",
    author_email="",
    url="",
    license="MIT",
    classifiers=[],
    cmdclass={},
    py_modules=[],
    packages=find_namespace_packages("lib"),
    package_dir={"": "lib"},
    package_data={},
    python_requires="",
    setup_requires=["setuptools_scm"],
    use_scm_version=lambda: {  # xref __init__.py
        "version_scheme": "post-release",
        "local_scheme": "node-and-date",
        "write_to": "lib/mplinorm/_version.py",
    },
    install_requires=[
    ],
    entry_points={
        "console_scripts": [],
        "gui_scripts": [],
    },
)
