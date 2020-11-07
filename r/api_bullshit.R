# INARA API key
api_key <- "93ed0iol73swsowgokocwogws8kc804s44ccggg"

?get

setwd("C:/Users/thoma/Documents/ed")

library(readxl)
library(tidyverse)
library(rjson)
library(plotly)

# load data ####

systems_pop_url <- "https://eddb.io/archive/v6/systems_populated.json"
systems_pop.list <- fromJSON(paste(readLines(systems_pop_url), collapse=""))


# extract coordinates ####
elements <- c("id","name","x","y","z","population")

systems_pop.mat <-  matrix(nrow = length(systems_pop), ncol = length(elements))
for(i in 1:length(systems_pop.list)){
  
  x <- unlist(systems_pop.list[[i]])[elements]
  systems_pop.mat[i,] <- x

}
colnames(systems_pop.mat) <- elements

test <- as.data.frame(systems_pop.mat)

# plot plotly ####

ggplot(test, aes(x=x,y=y)) +
  geom_point()


