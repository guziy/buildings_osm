import osmnx as ox

# Retrieve OSM data
from cartopy.feature import NaturalEarthFeature
from matplotlib.gridspec import GridSpec

import matplotlib.pyplot as plt

from cartopy import crs as ccrs
from cartopy import feature

def main():


    ox.config(log_console=True)
    cities = [
        "Toronto", "Montreal", "Ottawa,CA", "Winnipeg", "Saskatoon", "Halifax,CA"
    ]


    # cities = ["city of Calgary, Alberta, Canada"]

    ncols = 3
    nrows = len(cities) // 3 + int(len(cities) % ncols > 0)

    gs = GridSpec(nrows=nrows, ncols=ncols, width_ratios=[1,] * ncols, wspace=0, hspace=0)
    fig = plt.figure(figsize=(6, 6), frameon=False)

    # Define the CartoPy CRS object.
    crs = ccrs.Miller()
    # This can be converted into a `proj4` string/dict compatible with GeoPandas
    crs_proj4 = crs.proj4_init

    for ci, city in enumerate(cities):
        row = ci // ncols
        col = ci % ncols

        ax = fig.add_subplot(gs[row, col], projection=crs)


        print(f"Downloading {city}")
        try:
            blds = ox.buildings_from_place(city)
        except TypeError:
            continue

        # Plot
        print(f"Plotting {city}")
        # blds.plot(facecolor="indigo", ax=ax)

        blds = blds.to_crs(crs_proj4)

        minx, miny, maxx, maxy = blds.total_bounds


        ax.add_geometries(blds['geometry'], crs=crs, facecolor="indigo")
        ax.set_extent([minx, maxx, miny, maxy], crs=crs)

        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.outline_patch.set_visible(False)

        # ax.add_feature(NaturalEarthFeature("physical", "rivers_lake_centerlines", "10m"),
        #                linewidth=0.5, facecolor=feature.COLORS["water"],
        #                edgecolor=feature.COLORS["water"])

        ax.set_title(city, fontsize=10)

    fig.savefig("buildings.png", dpi=300, bbox_inches="tight")

if __name__ == '__main__':
    main()