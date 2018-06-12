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

from urbansprawl.scale_bar import scale_bar


def reset_extents(city_to_extent, r_max_x, r_max_y):
    for city, old_ext in city_to_extent:
        xc = sum(old_ext[:2]) / 2
        yc = sum(old_ext[2:]) / 2

        new_ext = [xc - r_max_x, xc + r_max_x, yc - r_max_y, yc + r_max_y]

        city_to_extent[city] = new_ext


def download_buildings_cached_for(city_name, cities_dict, radius_m):
    cache_dir = Path("../cache")
    cache_dir.mkdir(exist_ok=True)

    cache_file = cache_dir / f"{city_name}_{radius_m}.bin"

    if cache_file.exists():
        return pickle.load(cache_file.open("rb"))

    blds = ox.buildings_from_point(cities_dict[city_name], radius_m, retain_invalid=True)

    pickle.dump(blds, cache_file.open("wb"))
    return blds


def add_river_shapes(ax, city, crs=None):
    data_dir = Path(__file__).parent.parent / "canvec_250K"

    city_to_province = {
        "Toronto": "ON",
        "Montreal": "QC",
        "Ottawa-Gatineau": "ON",
        "Vancouver": "BC",
        "Calgary": "AB",
        "Edmonton": "AB",
        "Winnipeg": "MB",
        "Halifax": "NS",
        "Saskatoon": "SK",
        "Moncton": "NB",
        "Charlottetown": "PE"

    }

    params = dict(facecolor=feature.COLORS["water"], linewidth=0)
    for province_dir in data_dir.iterdir():
        if province_dir.is_dir() and city_to_province[city] in province_dir.name:
            for f in (province_dir / province_dir.name[:-4]).iterdir():
                if f.name.startswith("waterbody_2") and f.name.endswith(".shp"):
                    ax.add_geometries(Reader(str(f)).geometries(), crs, **params)



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

    cities = OrderedDict([
        ("Toronto", (43.653908, -79.384293)),
    ])

    # cities = ["city of Calgary, Alberta, Canada"]

    ncols = 3
    nrows = len(cities) // 3 + int(len(cities) % ncols > 0)

    gs = GridSpec(nrows=nrows, ncols=ncols, width_ratios=[1,] * ncols, height_ratios=[1,] * nrows,
                  wspace=0.5, hspace=0.5)
    fig = plt.figure(figsize=(6, 6), frameon=False)

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



    # plotting
    for ci, city in enumerate(cities):
        row = ci // ncols
        col = ci % ncols

        ax = fig.add_subplot(gs[row, col], projection=crs)

        blds = city_to_data[city]

        # Plot
        print(f"Plotting {city}")

        ax.add_geometries(blds['geometry'], crs=crs, facecolor="k", edgecolor="none", linewidth=0)
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

        scale_bar(ax, crs, length=10, fontsize=5, location=(0.5, 0.06), linewidth=1)

        ax.set_title(city, fontsize=5)


    png_low = False
    if not png_low:
        fig.savefig("buildings_by_point_10_dpi300.pdf", dpi=300, bbox_inches="tight", transparent=True)
    else:
        fig.savefig("buildings_by_point_11_dpi300.png", dpi=300, bbox_inches="tight")

if __name__ == '__main__':
    main()