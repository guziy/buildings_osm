from collections import OrderedDict
from pathlib import Path
from cartopy import crs as ccrs
import xarray
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from show_buildings import download_buildings_cached_for, add_river_shapes
import numpy as np


def calculate_annual_max_temperature(data_root: Path):
    # calculate for each year
    data_list = []
    lons = None
    lats = None

    for yr_dir in data_root.iterdir():

        print(yr_dir)

        if not yr_dir.is_dir():
            continue

        data_files = yr_dir / "MODIS-C06__MOD11C1__DAILY__LandSurfaceTemperature__0.05deg__UHAM-ICDC__*.nc4"

        data_files_s = str(data_files)


        with xarray.open_mfdataset(data_files_s) as ds:

            print(ds["lst_day"])

            arr_data = ds["lst_day"].max(dim="time").to_masked_array().squeeze()

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


    ncols = 3
    nrows = len(cities) // 3 + int(len(cities) % ncols > 0)
    gs = GridSpec(nrows=nrows, ncols=ncols, width_ratios=[1,] * ncols, height_ratios=[1,] * nrows,
                  wspace=0.5, hspace=0.5)

    fig = plt.figure(figsize=(6, 6), frameon=False)

    # plotting
    for ci, city in enumerate(cities):
        row = ci // ncols
        col = ci % ncols

        ax = fig.add_subplot(gs[row, col], projection=projection)


        # Plot
        print(f"Plotting {city}")


        cs = ax.contourf(lons, lats, tmax_mean)
        plt.colorbar(cs)

        ax.set_extent(city_to_extent[city], crs=projection)

        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.outline_patch.set_visible(False)
        ax.background_patch.set_visible(False)

        add_river_shapes(ax, city, crs=ccrs.PlateCarree())

    fig.savefig("cities_tmax.png", dpi=300, bbox_inches="tight")

def test():
    cities = OrderedDict([
        ("Toronto", (43.653908, -79.384293)),
    ])

    main(cities=cities)


if __name__ == '__main__':
    test()