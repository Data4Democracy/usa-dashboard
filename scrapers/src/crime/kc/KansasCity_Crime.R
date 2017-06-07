# packages
library(RSocrata)
library(lubridate)
library(dplyr)
library(readr)

# get the data from data.kcmo.org as the API url
url.year<-c(2016,2015,2014,2013,2012,2011,2010,2009)
url.api<-c("https://data.kcmo.org/resource/c6e8-258d.json","https://data.kcmo.org/resource/geta-wrqs.json","https://data.kcmo.org/resource/nsn9-g8a4.json","https://data.kcmo.org/resource/ff6a-bhbu.json","https://data.kcmo.org/resource/xwdv-8y2g.json","https://data.kcmo.org/resource/5u8g-kq4k.json","https://data.kcmo.org/resource/c3qq-bxi5.json","https://data.kcmo.org/resource/3u3f-44ew.json")
api.urls<-data.frame(url.year,url.api)



scrape_kc_crime <- function(crime.year = 2016){
  kc_crime_raw <-
    read.socrata(as.character(api.urls$url.api[which(api.urls$url.year == crime.year)]))
  
  #observations are at the victim level
  #collapse down to crime level (Report ID and Date)
  kc_crime <-
    kc_crime_raw %>% distinct(report_no, description, reported_date, .keep_all = TRUE)
  
  # Keep columns of interest
  kc_crime <- kc_crime %>% select(reported_date, description, offense)
  
  #rename to match format
  names(kc_crime) <- c("Date", "Category")
  
  
  # fix the date
  kc_crime$Year <- year(kc_crime$Date)
  kc_crime$Month <- month(kc_crime$Date)
  kc_crime$Month <- as.integer(kc_crime$Month)
  kc_crime$Day <- day(kc_crime$Date)
  kc_crime <- kc_crime %>% select(Year,Month,Day,Category)
  
  # clean up the special characters in the offense column
  kc_crime$Category <- gsub("[0-9]", "", kc_crime$Category)
  kc_crime$Category <- gsub("[[:punct:]] ", "", kc_crime$Category)
  
  # get count of crimes
  kc_crime_counts <- kc_crime %>%
    group_by(Year,Month,Day,Category) %>%
    summarise(Count = n())
  
  
  
  # processed structure: year, month, day, offense, count
  # write the data as a csv
  write_csv(kc_crime_counts,paste0("KansasCity-", crime.year, "-crime.csv"))
  print(paste0("Wrote: ", length(kc_crime_counts$Count)," Records for: ", crime.year) )
}

scrape_kc_crime()
#scrape_kc_crime(2015)


