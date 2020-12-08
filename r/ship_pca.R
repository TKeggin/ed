# set session

library(readxl)
library(tidyverse)
library(ggrepel)

# load data
ship_data  <- read_excel("C:/Users/thoma/OneDrive/Documents/ed/data/meta/ships.xlsx", sheet = 1)
hardpoints <- read_excel("C:/Users/thoma/OneDrive/Documents/ed/data/meta/ships.xlsx", sheet = 2)
core       <- read_excel("C:/Users/thoma/OneDrive/Documents/ed/data/meta/ships.xlsx", sheet = 3)
optional   <- read_excel("C:/Users/thoma/OneDrive/Documents/ed/data/meta/ships.xlsx", sheet = 4)

# merge data
all <- merge(ship_data, hardpoints)
all <- merge(all, core)
all <- merge(all, optional)

# standardise traits
all$PAD   <- as.numeric(as.factor(all$PAD))

all_quant <- all[,-1]
rownames(all_quant) <- all$Model

all_quant_stand <- all_quant

for(trait in colnames(all_quant_stand)){
  x <- all_quant_stand[,trait]
  all_quant_stand[,trait] <- (x-min(x)) / (max(x)-min(x))
}

# figure out alliance ships
#alliance <- all
alliance <- all_quant_stand
alliance$Model <- rownames(alliance)

alliance <- filter(alliance, grepl("Alliance",Model))

alliance_long <- pivot_longer(alliance,colnames(alliance)[-which(colnames(alliance)=="Model")])

ggplot(alliance_long, aes(x = value, y = name)) +
  geom_col(aes(fill = Model),
           position = "dodge")


alliance_opt <- filter(alliance_long, grepl("class",name) & !grepl("_m",name))
ggplot(alliance_opt, aes(x = value, y = name)) +
  geom_col(aes(fill = Model),
           position = "stack")

# pca stuff ####


# pca

ship_data_mat <- as.matrix(all_quant_stand)

rownames(ship_data_mat) <- ship_data$SHIP

ship_data_mat <- t(ship_data_mat)

pca <- prcomp(ship_data_mat)

pca_df <- as.data.frame(pca$rotation)


# plot
ggplot(pca_df, aes(x=PC1,y=PC2)) +
  geom_point() +
  geom_label_repel(label = rownames(pca_df))
