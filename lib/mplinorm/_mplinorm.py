import functools

import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.widgets import SpanSelector
import numpy as np


def get_canvas(artist):
    return (artist.canvas if isinstance(artist, mpl.figure.Figure)
            else artist.figure.canvas)


def is_normed_image(image):
    return image.get_array().ndim == 2


def image_contains(image, event):
    return event.inaxes is image.axes and image.contains(event)[0]


def iter_overlapping_normed_images(artist, event):
    canvas = get_canvas(artist)
    if isinstance(artist, mpl.figure.Figure):
        for im in artist.images:
            if is_normed_image(im) and image_contains(im, event):
                yield im
        for ax in artist.axes:
            yield from iter_overlapping_normed_images(ax, event)
    elif isinstance(artist, mpl.axes.Axes):
        for im in artist.images:
            if is_normed_image(im) and image_contains(im, event):
                yield im
    elif (isinstance(artist, mpl.image._ImageBase)
            and is_normed_image(artist) and image_contains(artist, event)):
        yield artist


def hist_bins(sm):
    data = sm.get_array()
    log = isinstance(sm.norm, mpl.colors.LogNorm)
    if log:
        data = np.log(data)
    bins = np.histogram_bin_edges(
        data, "auto", np.log(sm.get_clim()) if log else sm.get_clim())
    if data.dtype.kind in "iu":
        db = max(round(bins[1] - bins[0]), 1)
        bins = np.arange(data.min(), data.max() + db, db)
    if log:
        bins = np.exp(bins)
    return bins


def install(artist):

    def on_button_press(event):
        if event.button != 3:  # Right-click.
            return

        images = [*iter_overlapping_normed_images(artist, event)]
        if not images:
            return

        def edit_norm():
            try:
                im, = images
            except ValueError:
                raise NotImplementedError from None
            array = im.get_array().ravel()
            clim0 = im.get_clim()
            sub_ax = plt.figure().subplots()
            h = sub_ax.hist(array, hist_bins(im), histtype="stepfilled")
            if isinstance(im.norm, mpl.colors.LogNorm):
                sub_ax.set(xscale="log")

            def on_select(vmin, vmax):
                if vmin == vmax:
                    im.set_clim(clim0)
                else:
                    im.set_clim((vmin, vmax))
                im.figure.canvas.draw()

            sub_ax.__ss = SpanSelector(
                sub_ax, on_select, "horizontal", useblit=True, span_stays=True)

            plt.show(block=False)

        menu = QtWidgets.QMenu()
        menu.addAction("Norm", edit_norm)
        menu.exec(event.guiEvent.globalPos())

    get_canvas(artist).mpl_connect("button_press_event", on_button_press)
