from collections import OrderedDict
from pathlib import Path
from cartopy import crs as ccrs

def calculate_annual_max_temperature(cities: dict, data_root: Path):
    # calculate for each year

    # get the average over available years

    # return the field to plot
    pass


def plot_field_for_cities(cities_extents: dict,
                          field, data_lons, data_lats):



    pass


def main(cities: dict, radius_m=20000,
         projection=ccrs.Miller()):

    data_root = Path("/scratch/huziy/MODIS_hambourg/DAILY")

    tmax_mean = calculate_annual_max_temperature(cities=cities, data_root=data_root)


def test():
    cities = OrderedDict([
        ("Toronto", (43.653908, -79.384293)),
    ])

    main(cities=cities)


if __name__ == '__main__':
    test()