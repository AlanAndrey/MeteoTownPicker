# Define class that allows transformation between coordinate systems (CRS)
# using the WGS84 as a reference system.
import pandas as pd
import numpy as np
from importlib.resources import files

SUPPORTED_CRS = pd.read_csv(files('MeteoTownPicker.data') / 'formats.csv', sep=';')

class CoordinateTransformer:
    def __init__(self):
        return

    def transform(self, coords, from_crs, to_crs):
        """
        Transform coordinates from one CRS to another. For coordinate formatting check .info() method.
        :param coords: coordinates in the appropriate format
        :param from_crs: source coordinate reference system
        :param to_crs: target coordinate reference system
        :return: transformed coordinates
        """
        assert (SUPPORTED_CRS['name'] == from_crs).any(), f"Unsupported source CRS: {from_crs}"
        assert (SUPPORTED_CRS['name'] == to_crs).any(), f"Unsupported target CRS: {to_crs}"
        assert type(coords) in [list, np.ndarray], "Coordinates must be a list or numpy array."
        if type(coords) is list:
            coords = np.array(coords)
        #if single entry, convert to 2D array
        if coords.ndim == 1:
            coords = coords.reshape(1, -1)

        # if no height is specified, assume it as zero and drop on return
        drop_height = coords.shape[1] == 2
        if drop_height:
            coords = np.hstack((coords, np.zeros((coords.shape[0],1))))

        if from_crs == to_crs:
            return coords[:,:2] if drop_height else coords

        #transform to reference system WGS84
        coords = self._transform_to_wgs84(coords, from_crs)
        #transform to target CRS
        coords = self._transform_from_wgs84(coords, to_crs)

        return coords[:,:2] if drop_height else coords

    def _transform_to_wgs84(self, coords, from_crs):
        """
        Transform coordinates to WGS84.
        :param coords: coordinates in format
        :param from_crs: source coordinate reference system
        :return: coordinates in WGS84 format
        """
        if from_crs == 'WGS84':
            return coords
        if from_crs == 'CH1903+':
            # Transformation logic from CH1903+ (LV95) to WGS84
            E, N, h_ch = coords[:, 0], coords[:, 1], coords[:, 2]
            _y = (E-2600000) / 1000000
            _x = (N-1200000) / 1000000
            _long = 2.6779094 + 4.728982 * _y + 0.791484 * _y * _x + 0.1306 * _y * _x**2 - 0.0436 * _y**3
            _lat = 16.9023892 + 3.238272 * _x - 0.270978 * _y**2 - 0.002528 * _x**2 - 0.0447 * _x * _y + 0.0140 * _y**3
            long = _long * 100 / 36
            lat = _lat * 100 / 36
            h_wgs = h_ch + 49.55 - 12.6 * _y - 22.64 * _x
            return np.column_stack([lat, long, h_wgs])
        raise ValueError(f"Unsupported source CRS: {from_crs}")

    def _transform_from_wgs84(self, coords, to_crs):
        """
        Transform coordinates from WGS84 to the target CRS.
        :param coords: coordinates in WGS84 format
        :param to_crs: target coordinate reference system
        :return: coordinates in target CRS format
        """
        if to_crs == 'WGS84':
            return coords
        if to_crs == 'CH1903+':
            _lat = (coords[:,0]-169028.66) / 10000
            _long = (coords[:,1]-26782.5) / 10000
            E = 2600072.37 + 211455.93 * _lat - 10938.51 * _lat * _long - 0.36 * _lat * _long**2 + - 44.54 * _lat**3
            N = 1200147.07 + 308807.95 * _long + 3745.25 * _lat**2 + 76.63 * _long**2 - 194.56 * _lat**2 * _long + 119.79 * _lat**3
            h_ch = coords[:,2] - 49.55 + 2.73 * _lat + 6.94 * _long
            return np.column_stack([E, N, h_ch])
        raise ValueError(f"Unsupported target CRS: {to_crs}")

    def info(self):
        """
        Print information about supported coordinate reference systems (CRS).
        :return: None
        """
        #format the strings nicely
        max_name_length = SUPPORTED_CRS['name'].astype(str).map(len).max()
        max_format_length = SUPPORTED_CRS['format'].astype(str).map(len).max()
        max_description_length = SUPPORTED_CRS['description'].astype(str).map(len).max

        print('Supported Coordinate Reference Systems (CRS):\n')
        out = 'Name' + ' ' * (max_name_length+1) + 'Format' + ' ' * (max_format_length-1) + 'Description'
        print(out)
        print('-' * (len(out) - 11 + max_description_length))

        #print each CRS
        for index, row in SUPPORTED_CRS.iterrows():
            out = row['name']
            out += ' ' * (max_name_length+5 - len(out))
            out += row['format'] + ' ' * (max_format_length+5 - len(row['format']))
            out += row['description']
            print(out)
        return