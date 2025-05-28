# class that implements the town picking functionality

import random
import pyproj
import pandas as pd
import geopandas as gpd
import plotly.express as px
from shapely.ops import transform
from importlib.resources import files
from sklearn.cluster import MiniBatchKMeans
from .transformer import CoordinateTransformer as OptimusPrime


class TownPicker:
    def __init__(self):
        self.TOWNS = pd.read_csv(files('MeteoTownPicker.data') / 'towns.csv', sep=';')
        # add cartesian coordinates to the towns dataframe
        t = OptimusPrime()
        coords_ch = self.TOWNS[['E', 'N']].to_numpy()
        coords_wgs84 = t.transform(coords_ch, 'CH1903+', 'WGS84')
        #now add the coordinates to the dataframe

        self.TOWNS['lat'] = coords_wgs84[:, 0]
        self.TOWNS['lon'] = coords_wgs84[:, 1]


        return

    def info(self, town=None):
        """
        Get information about the available towns or a specific town.
        :param town: Name of the town to get information about (optional).
        :return: DataFrame with town information or a specific town's information.
        """
        if town is None:
            result = pd.DataFrame(self.TOWNS.iloc[random.randint(0, len(self.TOWNS) - 1)])
        else:
            result = self.TOWNS[self.TOWNS['Ortschaftsname'].str.contains(f'{town}', case=False, na=False)]
            if result.empty:
                raise ValueError(f"Town '{town}' not found.")

        # print the result in a readable format
        max_oname_length = result['Ortschaftsname'].astype(str).map(len).max()
        max_plz_length = result['PLZ'].astype(str).map(len).max()
        max_kanton_length = result['Kantonskürzel'].astype(str).map(len).max()

        print('Your town information:')
        out = 'Name' + ' ' * (max_oname_length +1 ) + 'PLZ' + ' ' * (max_plz_length + 2) + 'Kanton'
        print(out)
        print('-' * len(out))

        for index, row in result.iterrows():
            on = row['Ortschaftsname']
            plz = str(row['PLZ'])
            k = row['Kantonskürzel']
            out = on + ' ' * (max_oname_length - len(on) + 5) + plz + ' ' * (max_plz_length - len(plz) + 5) + k
            print(out)
        return

    def _generate_clusters(self, N):
        # generate N clusters of towns based on their spatial distribution using the MiniBatchKMeans algorithm
        if N > len(self.TOWNS):
            raise ValueError(f"N must be less than or equal to {len(self.TOWNS)}")
        coords = self.TOWNS[['lat', 'lon']].to_numpy()
        kmeans = MiniBatchKMeans(n_clusters=N, n_init='auto')
        kmeans.fit(coords)
        labels = kmeans.labels_
        self.TOWNS['cluster'] = labels
        return


    def meteo_view(self, N=10):
        """
        Visualize the N towns chjosen from regions in the dataframe.
        :param N: Number of random towns to visualize (default is 7).
        """
        if N > len(self.TOWNS):
            raise ValueError(f"N must be less than or equal to {len(self.TOWNS)}")

        # generate the indices based on N groups of spacially equal regions
        self._generate_clusters(N)
        # now randomly select one town from each cluster
        towns = self.TOWNS.groupby('cluster').apply(lambda x: x.sample(1)).reset_index(drop=True)
        fig = px.scatter_mapbox(
            towns,
            lat='lat',
            lon='lon',
            hover_name='Ortschaftsname',
            hover_data=['PLZ', 'Kantonskürzel', 'Gemeindename'],
            zoom=6,
            height=600,
            mapbox_style='carto-positron',
            color='cluster',
            title=f'Random {N} Swiss Towns',
        )
        config = {'scrollZoom': True, 'displayModeBar': True}
        fig.show(config=config)
        return

    def full_view(self):
        """
        Visualize all the town information in a plotly scatter mapbox.
        """
        if 'cluster' in self.TOWNS.columns:
            c = 'cluster'
        else:
            c = 'PLZ'
        fig = px.scatter_mapbox(
            self.TOWNS,
            lat='lat',
            lon='lon',
            hover_name='Ortschaftsname',
            hover_data=['PLZ', 'Kantonskürzel', 'Gemeindename'],
            zoom=6,
            height=600,
            mapbox_style='carto-positron',
            color=c,
            title='Swiss Towns'
        )
        config = {'scrollZoom': True, 'displayModeBar': True}
        fig.show(config=config)
        return