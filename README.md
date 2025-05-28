# MeteoTownPicker
Own try at the picking of Towns in Switzerland used for the SRF Meteo Map

Data on the townships is taken from the [Official index of cities and towns including postal codes and perimeter](https://data.geo.admin.ch/browser/#/collections/ch.swisstopo-vd.ortschaftenverzeichnis_plz/items/ortschaftenverzeichnis_plz?.asset=asset-ortschaftenverzeichnis_plz_2056.csv.zip).

Data on the boundaries is taken from the [swissBOUNDARIES3D](https://www.swisstopo.admin.ch/de/landschaftsmodell-swissboundaries3d) dataset.

The transformation between CH1903+ and WGS84 is done using the Approximation specified in Section 2 of the [Näherungsformeln für die Transformation zwischen Schweizer Projektionskoordinaten und WGS84](https://backend.swisstopo.admin.ch/fileservice/sdweb-docs-prod-swisstopoch-files/files/2023/11/14/2bd5f57e-1109-40d6-8430-cbdfc9f42203.pdf).