# packages!
library(RSocrata)
library(lubridate)
library(dplyr)
library(readr)
# get the data from data.hartford.gov as the API url
raw_data <- read.socrata("https://data.hartford.gov/Public-Safety/Police-Incidents-01012005-to-Current/889t-nwfu")

# Keep columns of interest
keep_cols <- c("Date", "UCR_1_Category")
clean_data <- raw_data[,keep_cols]

# fix the date
clean_data$Date <- mdy(clean_data$Date)
clean_data$year <- year(clean_data$Date)
clean_data$month <- month(clean_data$Date)
clean_data$month <- as.integer(clean_data$month)
clean_data$day <- day(clean_data$Date)
clean_data <- clean_data[, c("year", "month", "day", "UCR_1_Category")]

# clean up the special characters in the offense column
names(clean_data)[4] <- "crime"
clean_data$crime <- gsub("[0-9]","", clean_data$crime)
clean_data$crime <- gsub("[[:punct:]] ","", clean_data$crime)

# get count of crimes
processed_data <- clean_data %>% filter(year == 2016) %>% 
                             group_by(year, month, day, crime) %>% 
                             summarise(count = n())

# processed structure: year, month, day, offense, count
# write the data as a csv
write_csv(processed_data, "hartford-2016-data.csv")
