#!/bin/bash

# create a directory with the current date
mkdir "$(date +"%d-%m-%Y")"

# switch to the daily directory
cd "$(date +"%d-%m-%Y")"

# pull the eddb.io data
wget https://eddb.io/archive/v6/systems_populated.json
wget https://eddb.io/archive/v6/stations.json
wget https://eddb.io/archive/v6/commodities.json
wget https://eddb.io/archive/v6/factions.json
wget https://eddb.io/archive/v6/listings.csv