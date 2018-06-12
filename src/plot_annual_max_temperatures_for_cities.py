from collections import OrderedDict
from pathlib import Path
from cartopy import crs as ccrs
import xarray
import matplotlib.pyplot as plt

def calculate_annual_max_temperature(data_root: Path):
    # calculate for each year

    for yr_dir in data_root.iterdir():

        print(yr_dir)

        if not yr_dir.is_dir():
            continue

        data_files = yr_dir / "MODIS-C06__MOD11C1__DAILY__LandSurfaceTemperature__0.05deg__UHAM-ICDC__*.nc4"

        data_files_s = str(data_files)

        with xarray.open_mfdataset(data_files_s) as ds:

            print(ds["lst_day"])

            arr_data = ds["lst_day"].max(dim="time").to_masked_array().squeeze()

            plt.figure()
            cs = plt.contourf(arr_data.max(axis=0).T)
            plt.colorbar(cs)
            plt.show()

            if True:
                raise Exception

    # get the average over available years

    # return the field to plot
    pass


def plot_field_for_cities(cities_extents: dict,
                          field, data_lons, data_lats):
    pass


def main(cities: dict, radius_m=20000,
         projection=ccrs.Miller()):

    data_root = Path("/scratch/huziy/MODIS_hambourg/DAILY")

    tmax_mean = calculate_annual_max_temperature(data_root=data_root)


def test():
    cities = OrderedDict([
        ("Toronto", (43.653908, -79.384293)),
    ])

    main(cities=cities)


if __name__ == '__main__':
    test()