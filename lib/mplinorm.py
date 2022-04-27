"""
Interactive contrast adjustment for Matplotlib images
=====================================================

mplinorm provides an interactive contrast adjustment window for Matplotlib_
images, similar to ImageJ_'s Brightness/Contrast adjustment window.

Call ``mplinorm.install(image_or_axes_or_figure)`` to install a right-click
popup menu on an image (actually a ScalarMappable), all images on an axes, or
all images on a figure; or ``mplinorm.install()`` to install the popup menu on
all images on all pyplot-managed figures.

Try e.g.::

    from matplotlib import pyplot as plt
    import mplinorm
    import numpy as np

    plt.figure().add_subplot().imshow(np.random.randn(100, 100))
    mplinorm.install()

and right-click on the figure.

.. _Matplotlib: https://matplotlib.org
.. _ImageJ: https://imagej.github.io

If the ``MPLINORM`` environment variable is set to a non-empty value *when the
Python process starts*, then any mplinorm will be automatically installed on
any Figure the first time it is drawn.

-------------------------------------------------------------------------------

Copyright (c) 2019-present Antony Lee

This software is provided 'as-is', without any express or implied
warranty. In no event will the authors be held liable for any damages
arising from the use of this software.

Permission is granted to anyone to use this software for any purpose,
including commercial applications, and to alter it and redistribute it
freely, subject to the following restrictions:

1. The origin of this software must not be misrepresented; you must not
   claim that you wrote the original software. If you use this software
   in a product, an acknowledgment in the product documentation would be
   appreciated but is not required.
2. Altered source versions must be plainly marked as such, and must not be
   misrepresented as being the original software.
3. This notice may not be removed or altered from any source distribution.
"""

from weakref import WeakKeyDictionary

import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.widgets import SpanSelector
import numpy as np


_selectors = WeakKeyDictionary()


def _get_canvas(artist):
    return (artist.canvas if isinstance(artist, mpl.figure.Figure)
            else artist.figure.canvas)


def _is_normed_image(image):
    return image.get_array().ndim == 2


def _image_contains(image, event):
    return event.inaxes is image.axes and image.contains(event)[0]


def _iter_overlapping_normed_images(artist, event):
    if isinstance(artist, mpl.figure.Figure):
        for im in artist.images:
            if _is_normed_image(im) and _image_contains(im, event):
                yield im
        for ax in artist.axes:
            yield from _iter_overlapping_normed_images(ax, event)
    elif isinstance(artist, mpl.axes.Axes):
        for im in artist.images:
            if _is_normed_image(im) and _image_contains(im, event):
                yield im
    elif (isinstance(artist, mpl.image._ImageBase)
            and _is_normed_image(artist) and _image_contains(artist, event)):
        yield artist


def _hist_bins(sm):
    data = sm.get_array()
    log = isinstance(sm.norm, mpl.colors.LogNorm)
    if log:
        data = np.log(data)
    # Infer the binsize from the clim, then bin the full data range.
    bins = np.histogram_bin_edges(
        data, "auto", np.log(sm.get_clim()) if log else sm.get_clim())
    binsize = bins[1] - bins[0]
    if data.dtype.kind in "iu":  # not log.
        binsize = max(round(binsize), 1)
        bins = np.arange(data.min(), data.max() + binsize + .5, binsize) - .5
    else:
        bins = np.arange(data.min(), data.max() + binsize, binsize)
    if log:
        bins = np.exp(bins)
    return bins


def install(artist=None):
    """
    Install an mplinorm menu on a ScalarMappable, all images on an axes,
    all images on a figure, or (if *artist* is unset) all images on all
    pyplot-managed figures.
    """

    if artist is None:
        for num in plt.get_fignums():
            install(plt.figure(num))
        return

    def on_button_release(event):
        if event.button != 3:  # Right-click.
            return

        images = [*_iter_overlapping_normed_images(artist, event)]
        if not images:
            return

        def edit_norm(_arg=None):  # Only some backends pass in an argument.
            axs = plt.figure().subplots(len(images), 1, squeeze=False)[:, 0]
            for ax, image in zip(axs, images):
                array = image.get_array()
                ax.hist(array.ravel(), _hist_bins(image),
                        histtype="stepfilled")
                if isinstance(image.norm, mpl.colors.LogNorm):
                    ax.set(xscale="log")
                elif array.dtype.kind in "iu":  # not log.
                    ax.xaxis.get_major_locator().set_params(integer=True)

                def on_select(vmin, vmax, *, _image=image):
                    array = _image.get_array()
                    if vmin == vmax:
                        _image.set_clim((array.min(), array.max()))
                    else:
                        _image.set_clim((vmin, vmax))
                    _image.figure.canvas.draw()

                if hasattr(SpanSelector, "extents"):
                    ss = SpanSelector(ax, on_select, "horizontal",
                                      useblit=True, interactive=True)
                    ss.extents = (image.norm.vmin, image.norm.vmax)
                else:
                    ss = SpanSelector(ax, on_select, "horizontal",
                                      useblit=True, span_stays=True)
                    ss.stay_rect.set(x=image.norm.vmin,
                                     width=image.norm.vmax - image.norm.vmin,
                                     visible=True)
                _selectors.setdefault(ax, []).append(ss)
            plt.show(block=False)

        gui_event = event.guiEvent
        pkg = type(gui_event).__module__.split(".")[0]

        if pkg == "gi":
            from gi.repository import Gtk
            menu = Gtk.Menu()
            item = Gtk.MenuItem.new_with_label("Norm")
            menu.append(item)
            item.connect("activate", edit_norm)
            item.show()
            menu.popup_at_pointer(gui_event)
        elif pkg.startswith(("PyQt", "PySide")):
            from matplotlib.backends.qt_compat import QtCore, QtWidgets
            menu = QtWidgets.QMenu()
            menu.addAction("Norm", edit_norm)
            point = (gui_event.globalPosition().toPoint()
                     if QtCore.qVersion().split(".")[0] == "6"
                     else gui_event.globalPos())
            menu.exec(point)
        elif pkg == "tkinter":
            from tkinter import Menu
            menu = Menu(gui_event.widget, tearoff=0)
            menu.add_command(label="Norm", command=edit_norm)
            try:
                menu.tk_popup(gui_event.x_root, gui_event.y_root)
            finally:
                menu.grab_release()
        elif pkg == "wx":
            import wx
            menu = wx.Menu()
            item = menu.Append(wx.ID_ANY, "Norm")
            gui_event.EventObject.Bind(wx.EVT_MENU, edit_norm, id=item.Id)
            gui_event.EventObject.PopupMenu(menu)
        else:
            raise NotImplementedError("The current backend is not supported")

    _get_canvas(artist).mpl_connect("button_release_event", on_button_release)
