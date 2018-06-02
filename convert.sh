export map_path 'Poa2'
wget https://overpass-api.de/api/map?bbox=-51.2417,-30.0373,-51.2274,-30.0249 -O $map_path/map2
netconvert --guess-ramps --geometry.remove --remove-edges.isolated --try-join-tls --verbose --osm-files Poa2/map --output-file Poa2/poa.net.xml