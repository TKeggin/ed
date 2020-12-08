# set session ####

setwd("C:/Users/thoma/OneDrive/Documents/ed/")

library(readxl)
library(tidyverse)
library(rjson)
library(plotly)
library(data.table)

# load data ####

systems_raw     <- fromJSON(file = "./data/raw/systems_populated.json")
listings_raw    <- read_csv("./data/raw/listings.csv")
commodities_raw <- fromJSON(file = "./data/raw/commodities.json")
stations_raw    <- fromJSON(file = "./data/raw/stations.json")
factions_raw    <- read_csv("./data/raw/factions.csv", col_types = "iciicicil")

# system_main ####
keep   <- names(systems_raw[[1]])[!names(systems_raw[[1]]) %in% c("states","minor_faction_presences")]
system_main <- data.frame(matrix(nrow=0,ncol=length(keep)))

for(i in 1:length(systems_raw)){
  
  system <- systems_raw[[i]][keep]
  system <- lapply(system,function(x)if(is.null(x)) NA else x)
  
  system <- as.matrix(system)
  system_main <- rbind(system_main,system[,1])
  
}
colnames(system_main) <- c("system_id",keep[-1])

write_csv(system_main, "./data/clean/station_main.csv")

# system_state ####

system_state <- data.frame()
for(system in 1:length(systems_raw)){
  
  stat   <- systems_raw[[system]]$states
  sys_id <- systems_raw[[system]]$id
  
  if(length(stat)==0){
  }else{
    states_df <- data.frame()
    for(i in 1:length(stat)){
      
      state <- data.frame(stat[[i]])
      state$system_id <- sys_id
      
      states_df <- rbind(states_df,state)
    }
    system_state <- rbind(system_state, states_df)
  }
}
colnames(system_state) <- c("state_id","state","system_id")

write_csv(system_state, "./data/clean/system_state.csv")

# system_faction ####
system_faction <- rbindlist(systems_raw[[1]]$minor_faction_presences, fill=TRUE)

length(systems_raw[[1]]$minor_faction_presences)

rbindlist(systems_raw[[1]]$minor_faction_presences[[1]], fill=TRUE)

test <- names(unlist(systems_raw[[1]]$minor_faction_presences))

# listings ####
write_csv(listings_raw,"./data/clean/listings.csv")

# commodities ####
commodities_df <- rbindlist(commodities_raw, fill=TRUE)
colnames(commodities_df) <- c("commodity_id", colnames(commodities_df)[-1])

commodities_df <- distinct(commodities_df[,c(1,2)])

write_csv(commodities_df, "./data/clean/commodity.csv")

# station_main ####

states
import_commodities
export_commodities
prohibited_commodities
selling_ships
selling_modules

names()

# station_state ####

station_state <- data.frame()
for(station in 1:length(stations_raw)){
  
  stat       <- stations_raw[[station]]$states
  station_id <- stations_raw[[station]]$id
  
  if(length(stat)==0){
  }else{
    states_df <- data.frame()
    for(i in 1:length(stat)){
      
      state <- data.frame(stat[[i]])
      state$station_id <- station_id
      
      states_df <- rbind(states_df,state)
    }
    station_state <- rbind(station_state, states_df)
  }
  print(paste(round(station/length(stations_raw)*100,2),"%"))
}
colnames(station_state) <- c("state_id","state","station_id")

write_csv(station_state, "./data/clean/station_state.csv")

# station_faction ####


# station_ship ####
# station_commodity_export ####
# station_commodity_import ####
# station_commodity_prohib ####
# station_module ####

