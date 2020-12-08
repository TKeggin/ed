# set session

library(httr)
library(jsonlite)

# get data
systems_raw     <- GET("https://eddb.io/archive/v6/systems_populated.json")
stations_raw    <- GET("https://eddb.io/archive/v6/stations.json")
commodities_raw <- GET("https://eddb.io/archive/v6/commodities.json")
factions_raw    <- GET("https://eddb.io/archive/v6/factions.json")

# convert data to data frames
systems     <- fromJSON(rawToChar(systems_raw$content))
stations    <- fromJSON(rawToChar(stations_raw$content))
commodities <- fromJSON(rawToChar(commodities_raw$content))
factions    <- fromJSON(rawToChar(factions_raw$content))
listings    <- read_csv("https://eddb.io/archive/v6/listings.csv")

# compile into a time stamped list
data <- list(date.time   = as.numeric(Sys.time()),
             systems     = systems,
             stations    = stations,
             commodities = commodities,
             factions    = factions,
             listings    = listings)

# write the data to disk
saveRDS(data, "database.RDS")
