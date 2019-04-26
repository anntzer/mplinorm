try:
    from ._version import version as __version__
except ImportError:
    try:
        import setuptools_scm
        __version__ = setuptools_scm.get_version(
            root="../../", relative_to=__file__,
            version_scheme="post-release", local_scheme="node-and-date")
    except (ImportError, LookupError):
        pass


from ._mplinorm import install


__all__ = ["install"]
