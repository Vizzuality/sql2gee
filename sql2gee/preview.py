def histplot_preview(q):
    """Returns a matplotlib plot object, meant for development previews only from an instantiated SQL2GEE object.
    This needs numpy and matplotlib to be installed, which are not included in the requirements for size.
    import ee
    from sql2gee import SQL2GEE, histplot_preview
    ee.Initialize()
    sql = "SELECT ST_HISTPLOT() FROM srtm90_v4"
    q = SQL2GEE(sql)
    histplot_preview(q)
    """
    import numpy as np
    import matplotlib.pyplot as plt
    for key in q.histogram:
        if q.histogram[key]:
            bins = []
            frequency = []
            for item in q.histogram[key]:
                bin_left, val = item
                bins.append(bin_left)
                frequency.append(val)
            bins = np.array(bins)
            frequency = np.array(frequency)
            counts = [q._reduce_image[ band +'_count'] for band in q._band_names]
            counts = np.array(counts)
            plt.step(bins, frequency / counts)
            plt.title(key.capitalize())
            plt.ylabel("frequency")
            if plt:
                plt.show()
    return