import osmnx as ox

# Retrieve OSM data
from urbansprawl.core import get_processed_osm_data



def main():
    region_args = {"place": "Paris, France"}
    df_osm_built, df_osm_building_parts, df_osm_pois = get_processed_osm_data(city_ref_file='Paris_France',
                                                                              region_args=region_args)

    # Plot
    ax = df_osm_built.plot()
    ax.get_xaxis().set_visible(False);
    ax.get_yaxis().set_visible(False)


if __name__ == '__main__':
    main()