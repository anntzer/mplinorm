Interactive contrast adjustment for Matplotlib images
=====================================================

|GitHub|

.. |GitHub|
   image:: https://img.shields.io/badge/github-anntzer%2Fmplinorm-brightgreen
   :target: https://github.com/anntzer/mplinorm

mplinorm provides an interactive contrast adjustment window for Matplotlib_
images, similar to ImageJ_'s Brightness/Contrast adjustment window.

As usual, install using pip_, and call
``mplinorm.install(image_or_axes_or_figure)`` to install a right-click
popup menu on an image, all images on an axes, or all images on a figure;
or ``mplinorm.install()`` to install the popup menu on all images on all
pyplot-managed figures.

.. _Matplotlib: https://matplotlib.org
.. _ImageJ: https://imagej.github.io
.. _pip: https://pip.pypa.io
