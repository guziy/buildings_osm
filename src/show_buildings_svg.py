
import matplotlib

from show_buildings import download_buildings_cached_for, add_river_shapes

matplotlib.use("Agg")


import pickle
from collections import OrderedDict
from pathlib import Path

import osmnx as ox

# Retrieve OSM data
from cartopy.feature import NaturalEarthFeature
from cartopy.io.shapereader import Reader



from matplotlib.gridspec import GridSpec

import matplotlib.pyplot as plt


from cartopy import crs as ccrs
from cartopy import feature

from north_arrow_svg import north_arrow
from scale_bar_only import scale_bar_only
from urbansprawl.scale_bar import scale_bar

# Description:

# Plots buildings for each city in a separate svg file
# Adds a north arrow to the previously generated svg files
# Puts the svg files (containing the north arrow) into panels of a panel plot.


def reset_extents(city_to_extent, r_max_x, r_max_y):
    for city, old_ext in city_to_extent:
        xc = sum(old_ext[:2]) / 2
        yc = sum(old_ext[2:]) / 2

        new_ext = [xc - r_max_x, xc + r_max_x, yc - r_max_y, yc + r_max_y]

        city_to_extent[city] = new_ext




def plot_cities_in_svg(cities: dict, out_dir=None, radius_m=2000):
    if out_dir is None:
        out_dir = Path(__file__).parent.parent / "out_svg"

    fig_dir = Path(out_dir)
    fig_dir.mkdir(exist_ok=True)

    # Define the CartoPy CRS object.
    crs = ccrs.Miller()
    # This can be converted into a `proj4` string/dict compatible with GeoPandas
    crs_proj4 = crs.proj4_init

    city_to_data = OrderedDict()
    city_to_extent = OrderedDict()

    # get the data and compute some things
    for ci, city in enumerate(cities):
        print(f"Downloading {city}")
        try:
            # blds = ox.buildings_from_place(city)
            blds = download_buildings_cached_for(city, cities, radius_m=radius_m)
        except TypeError:
            continue

        # blds.plot(facecolor="indigo", ax=ax)

        blds = blds.to_crs(crs_proj4)
        minx, miny, maxx, maxy = blds.total_bounds
        city_to_data[city] = blds
        city_to_extent[city] = [minx, maxx, miny, maxy]

    gs = GridSpec(1, 1, hspace=0, wspace=0)
    # plotting
    for ci, city in enumerate(cities):

        city_img = fig_dir / f"{city}.svg"

        if city_img.exists():
            print(f"{city_img} already exists, remove to redraw.")
        else:
            fig = plt.figure(figsize=(5, 5), frameon=False)
            ax = fig.add_subplot(gs[0, 0], projection=crs)

            blds = city_to_data[city]

            # Plot
            print(f"Plotting {city}")

            ax.add_geometries(blds['geometry'], crs=crs,
                              facecolor="k",
                              edgecolor="none",
                              linewidth=0)

            ax.set_extent(city_to_extent[city], crs=crs)

            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)
            ax.outline_patch.set_visible(False)
            ax.background_patch.set_visible(False)

            add_river_shapes(ax, city, crs=ccrs.PlateCarree())
            # add_river_shapes(ax, city, crs=ccrs.epsg(5713))


            # ax.add_geometries(Reader(river_shapes_path).geometries(),
            #                   ccrs.PlateCarree(),
            #                   facecolor=feature.COLORS["water"], linewidth=0, zorder=-10)

            # ax.add_feature(NaturalEarthFeature("physical", "rivers_lake_centerlines", "10m"),
            #                linewidth=0.5, facecolor=feature.COLORS["water"],
            #                edgecolor=feature.COLORS["water"])

            fontsize = 10
            scale_bar_only(ax, crs, length=10,
                           fontsize=fontsize,
                           location=(0.5, 0.06),
                           linewidth=1)

            ax.set_title(city, fontsize=fontsize)
            fig.savefig(str(city_img), bbox_inches="tight")

        north_arrow(city_img)



def main():
    ox.config(log_console=True)

    river_shapes_path = "../canvec_1M_CA_Hydro_shp/canvec_1M_CA_Hydro/waterbody_2.shp"
    radius_m = 20000

    # Coordinates taken from http://latitudelongitude.org/ca/
    cities = OrderedDict([
        ("Toronto", (43.653908, -79.384293)),
        ("Montreal", (45.50884, -73.58781)),
        ("Vancouver", (49.24966, -123.11934)),
        ("Calgary", (51.05011, -114.08529)),
        ("Edmonton", (53.55014, -113.46871)),
        ("Ottawa-Gatineau", (45.41117, -75.69812)),
        ("Winnipeg", (49.8844, -97.14704)),
        ("Halifax", (44.64533, -63.57239)),
        ("Saskatoon", (52.11679, -106.63452)),
        ("Moncton", (46.090946, -64.790497)),
        ("Charlottetown", (46.2389900, -63.1341400))
    ])

    # cities = OrderedDict([
    #     ("Toronto", (43.653908, -79.384293)),
    # ])

    # cities = ["city of Calgary, Alberta, Canada"]
    plot_cities_in_svg(cities=cities, radius_m=radius_m)


if __name__ == '__main__':
    main()
