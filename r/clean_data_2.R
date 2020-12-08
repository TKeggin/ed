# set session ####

library(tidyverse)

# load data ####

data <- readRDS("./database.RDS")

# systems_main ####

remove       <- which(sapply(data$systems,class) == "list")
systems_main <- data$systems[,-remove]

# systems_states ####

systems_states_list <- data$systems$states

systems_states <- data.frame()
for(i in 1:length(systems_states_list)){
  if(dim(systems_states_list[[i]])[1]){
    states <- data.frame(systems_states_list[[i]])
    states$system_name <- systems_main$name[i]
    
    systems_states <- rbind(systems_states,states)
    print(i)
  }
}
colnames(systems_states) <- c("id","state_name","system_name")

# systems_factions ####

systems_factions_list <- data$systems$minor_faction_presences

systems_factions <- data.frame()
for(i in 1:length(systems_factions_list)){
  if(dim(systems_factions_list[[i]])[1]){
    factions <- data.frame(systems_factions_list[[i]])
    factions$system_name <- systems_main$name[i]
    
    systems_factions <- rbind(systems_factions,factions)
    print(i)
  }
}
colnames(systems_factions) <- c("id","state_name","faction_name")

# stations_main ####
