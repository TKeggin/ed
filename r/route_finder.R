
# script to find the shortest route between selected star systems

# set session ####

library(tidyverse)
library(reshape2)
library(TSP)

# load system data
systems <- read_delim("C:/Users/thoma/OneDrive/Documents/ed/data/systems.csv", delim=",")


# specify target systems
way_systems <- c("HIP 33287",
                 "LP 131-66",
                 "Zeaex")
# present system
start_system <- "LHS 28"

# filter for target system data
systems_target <- filter(systems, name %in% c(way_systems,start_system))

# create a distance matrix
sys_dist <- as.matrix(dist(systems_target[,c("x","y","z")], method = "euclidean"))
colnames(sys_dist) <- systems_target$name
rownames(sys_dist) <- systems_target$name

# melt distance matrix into routes
routes <- melt(sys_dist, varnames = c("row", "col"))

# filter out duplicated and non-viable routes
routes <- filter(routes) %>% filter(row !=col) %>% filter(duplicated(value))

# find shortest route
routes %>% group_by(col) %>% summarise(min(value))
routes %>% group_by(col) %>% slice(which.min(value))

# find shortest route
sys_tsp <- TSP(sys_dist, labels = colnames(sys_dist))

# 
test <- solve_TSP(sys_tsp)

# run the concorde solver
concorde_path("C:/Program Files (x86)/Concorde")
concorde_help()

write_TSPLIB(sys_tsp, "./test.tsp", precision = 4)


