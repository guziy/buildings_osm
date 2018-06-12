import matplotlib
matplotlib.use("Agg")


import pickle
from collections import OrderedDict
from pathlib import Path
from cartopy import crs as ccrs
import xarray
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import BoundaryNorm
from matplotlib.gridspec import GridSpec
from mpl_toolkits.axes_grid1 import make_axes_locatable

from show_buildings import download_buildings_cached_for, add_river_shapes, reset_extents
import numpy as np


def calculate_annual_max_temperature(data_root: Path):
    # calculate for each year
    data_list = []
    lons = None
    lats = None

    for yr_dir in data_root.iterdir():

        print(yr_dir)

        arr_data = None
        if not yr_dir.is_dir():
            continue

        yr_max_cache = yr_dir / "max_cache.bin"
        if yr_max_cache.exists():
            print(f"Reusing cache from {yr_max_cache}")
            arr_data = pickle.load(yr_max_cache.open("rb"))

        data_files = yr_dir / "MODIS-C06__MOD11C1__DAILY__LandSurfaceTemperature__0.05deg__UHAM-ICDC__*.nc4"

        data_files_s = str(data_files)

        with xarray.open_mfdataset(data_files_s, data_vars="minimal", coords="minimal") as ds:

            print(ds["lst_day"])

            # read in the data if it were not yet retrieved from cache
            if arr_data is None:
                arr_data = ds["lst_day"].max(dim="time").to_masked_array().squeeze()

                #cache it for the next run
                pickle.dump(arr_data, yr_max_cache.open("wb"))


            if lons is None:
                lons = ds["lon"].values
                lats = ds["lat"].values

            data_list.append(
                np.ma.masked_where(arr_data >= 200, arr_data)
            )

    # get the average over available years
    arr_mean = np.ma.mean(data_list, axis=0)

    # return the field to plot
    return lons, lats, arr_mean



def main(cities: dict, radius_m=20000,
         projection: ccrs.Projection=ccrs.Miller()):

    data_root = Path("/scratch/huziy/MODIS_hambourg/DAILY")

    lons, lats, tmax_mean = calculate_annual_max_temperature(data_root=data_root)


    # Define the CartoPy CRS object.
    crs = projection
    # This can be converted into a `proj4` string/dict compatible with GeoPandas
    crs_proj4 = projection.proj4_init


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
        city_to_extent[city] = [minx, maxx, miny, maxy]

        reset_extents(city_to_extent,r_max_x=radius_m, r_max_y=radius_m)


    ncols = 3
    nrows = len(cities) // 3 + int(len(cities) % ncols > 0)
    gs = GridSpec(nrows=nrows, ncols=ncols, width_ratios=[1,] * ncols, height_ratios=[1,] * nrows,
                  wspace=0.5, hspace=0.5)

    fig = plt.figure(figsize=(6, 6), frameon=False)


    levels = np.arange(20, 40, 1)
    bn = BoundaryNorm(levels, len(levels) - 1)
    cmap = cm.get_cmap("RdYlGn_r", len(levels) - 1)

    # plotting
    for ci, city in enumerate(cities):
        row = ci // ncols
        col = ci % ncols

        ax = fig.add_subplot(gs[row, col], projection=projection)


        # Plot
        print(f"Plotting {city}")
        print(city_to_extent[city])

        cs = ax.contourf(lons, lats, tmax_mean, levels=levels, norm=bn, cmap=cmap, extend="both")

        divider = make_axes_locatable(ax)
        ax_cb = divider.new_horizontal(size="5%", pad=0.1, axes_class=plt.Axes)
        fig.add_axes(ax_cb)
        cb = plt.colorbar(cs, cax=ax_cb)
        cb.ax.tick_params(labelsize=5)

        ax.add_geometries(blds['geometry'], crs=crs, facecolor="k", edgecolor="none", linewidth=0, alpha=0.3)
        ax.set_extent(city_to_extent[city], crs=projection)

        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.outline_patch.set_visible(False)
        ax.background_patch.set_visible(False)

        add_river_shapes(ax, city, crs=ccrs.PlateCarree())

        ax.set_title(city, fontsize=5)

    fig.savefig("cities_tmax.png", dpi=300, bbox_inches="tight")


def test():
    # cities = OrderedDict([
    #     ("Toronto", (43.653908, -79.384293)),
    # ])

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


    main(cities=cities)


if __name__ == '__main__':
    test()