
import matplotlib.pyplot as plt
from cartopy import crs as ccrs

from urbansprawl.scale_bar import scale_bar

if __name__ == '__main__':

    ax = plt.axes(projection=ccrs.Mercator())
    plt.title('Cyprus')
    ax.set_extent([31, 35.5, 34, 36], ccrs.Geodetic())
    ax.stock_img()
    ax.coastlines(resolution='10m')

    scale_bar(ax, ccrs.Mercator(), 100, fontsize=20)  # 100 km scale bar
    # or to use m instead of km
    # scale_bar(ax, ccrs.Mercator(), 100000, m_per_unit=1, units='m')
    # or to use miles instead of km
    # scale_bar(ax, ccrs.Mercator(), 60, m_per_unit=1609.34, units='miles')

    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                      linewidth=2, color='gray', alpha=0.5, linestyle='--')


    plt.show()