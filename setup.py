import ast
import tokenize

from setupext import setup


# We cannot directly import matplotlib if `MPLINORM` is set because `sys.path`
# is not correctly set yet.
#
# The loading of `matplotlib.figure` does not go through the path entry finder
# because it is a submodule, so we must use a metapath finder instead.

@setup.register_pth_hook("mplinorm.pth")
def _pth_hook():
    import os
    if os.environ.get("MPLINORM"):
        from importlib.machinery import PathFinder
        import sys
        class MplinormMetaPathFinder(PathFinder):
            def find_spec(self, fullname, path=None, target=None):
                spec = super().find_spec(fullname, path, target)
                if fullname == "matplotlib.figure":
                    def exec_module(module):
                        type(spec.loader).exec_module(spec.loader, module)
                        # The pth file does not get properly uninstalled from
                        # a develop install.  See pypa/pip#4176.
                        try:
                            import mplinorm
                        except ImportError:
                            return
                        import functools
                        import weakref
                        # Ensure that when the cursor is removed(), or gets
                        # GC'd because its referents artists are GC'd, the
                        # entry also disappears.
                        figs = weakref.WeakSet()
                        @functools.wraps(module.Figure.draw)
                        def wrapper(self, *args, **kwargs):
                            if self not in figs:
                                figs.add(self)
                                mplinorm.install(self)
                            return wrapper.__wrapped__(self, *args, **kwargs)
                        module.Figure.draw = wrapper
                    spec.loader.exec_module = exec_module
                    sys.meta_path.remove(self)
                return spec
        sys.meta_path.insert(0, MplinormMetaPathFinder())


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
