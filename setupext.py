"""
setuptools helper.

The following decorators are provided::

    # Define an extension module with the possibility to import setup_requires.
    @setup.add_extension
    def make_extension():
        import some_setup_requires.
        return Extension(...)

    # Add a pth hook.
    @setup.register_pth_hook("hook_name.pth")
    def _hook():
        # hook contents.
"""

from distutils.version import LooseVersion
from functools import partial
import inspect
import re
from pathlib import Path
import traceback

import setuptools
from setuptools import Extension, find_namespace_packages, find_packages
from setuptools.command.build_ext import build_ext
from setuptools.command.develop import develop
from setuptools.command.install_lib import install_lib


if LooseVersion(setuptools.__version__) < "40.1":  # find_namespace_packages
    raise ImportError("setuptools>=40.1 is required")


__all__ = ["Extension", "find_namespace_packages", "find_packages", "setup"]


_ext_makers = []
_pth_hooks = []


class build_ext_mixin:
    def finalize_options(self):
        # This is called once by egg_info (to get the source files for the
        # MANIFEST) and once to really prepare building the extensions.  The
        # first time, install_requires have not been installed yet, so we still
        # can't generate the extension objects.
        if setuptools.command.egg_info.__file__ not in [
                fs.filename for fs in traceback.extract_stack()]:
            self.distribution.ext_modules[:] = [
                ext_maker() for ext_maker in _ext_makers]
        super().finalize_options()

    def build_extensions(self):
        try:
            self.compiler.compiler_so.remove("-Wstrict-prototypes")
        except (AttributeError, ValueError):
            pass
        super().build_extensions()


class pth_hook_mixin:
    def run(self):
        super().run()
        for fname, name, source in _pth_hooks:
            with Path(self.install_dir, fname).open("w") as file:
                file.write("import os; exec({!r}); {}()"
                           .format(source, name))

    def get_outputs(self):
        return (super().get_outputs()
                + [str(Path(self.install_dir, fname))
                   for fname, _, _ in _pth_hooks])


def setup(**kwargs):
    cmdclass = kwargs.setdefault("cmdclass", {})
    cmdclass["build_ext"] = type(
        "build_ext_with_extensions",
        (build_ext_mixin, cmdclass.get("build_ext", build_ext)),
        {})
    cmdclass["develop"] = type(
        "develop_with_pth_hook",
        (pth_hook_mixin, cmdclass.get("develop", develop)),
        {})
    cmdclass["install_lib"] = type(
        "install_lib_with_pth_hook",
        (pth_hook_mixin, cmdclass.get("install_lib", install_lib)),
        {})
    kwargs.setdefault(
        # Don't tag wheels as dist-specific if no extension.
        "ext_modules", [Extension("", [])] if _ext_makers else [])
    setuptools.setup(**kwargs)


def add_extension(func):
    _ext_makers.append(func)


def register_pth_hook(fname, func=None):
    if func is None:
        return partial(register_pth_hook, fname)
    source = inspect.getsource(func)
    if not re.match(r"\A@setup\.register_pth_hook.*\ndef ", source):
        raise SyntaxError("register_pth_hook must be used as a toplevel "
                          "decorator to a function")
    _, source = source.split("\n", 1)
    d = {}
    exec(source, {}, d)
    if set(d) != {func.__name__}:
        raise SyntaxError(
            "register_pth_hook should define a single function")
    _pth_hooks.append((fname, func.__name__, source))


setup.add_extension = add_extension
setup.register_pth_hook = register_pth_hook
