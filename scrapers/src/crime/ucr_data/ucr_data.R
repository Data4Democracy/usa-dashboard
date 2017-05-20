library(rvest); library(dplyr); library(tidyr); library(tibble); 
library(stringr); library(readr)

scrape_ucr_data <- function(ucr_year, link){
     print("Getting HTML Table")
     if(ucr_year >= 2010){
          scraped_raw <- 
               read_html(link) %>% html_nodes("#table-data-container > table") %>% html_table() %>% .[[1]]
     }else if(ucr_year %in% 2006:2009){
          scraped_raw <- read_html(link) %>% html_nodes("#datatable > table") %>% html_table() %>% .[[1]]
     }else{
          scraped_raw <- read_html(link) %>% html_nodes("#data") %>% html_table() %>% .[[1]]
     }
     print("Cleaning up names")
     names(scraped_raw) <- 
          names(scraped_raw) %>% 
          str_replace_all("\\n", "") %>%
          str_replace_all(" |/|-", "_") %>% tolower() %>%
          sapply(function(x) ifelse(str_sub(x, 1, 7) == "larceny", "larceny_theft", x)) %>% unname() %>%
          sapply(function(x) ifelse(x == "counties_principalcities", "counties_principal_cities", x)) %>% unname() %>%
          sapply(function(x) ifelse(x == "violentcrime", "violent_crime", x)) %>% unname() %>%
          sapply(function(x) ifelse(x == "propertycrime", "property_crime", x)) %>% unname() %>%
          sapply(function(x) ifelse(x == "motorvehicletheft", "motor_vehicle_theft", x)) %>% unname() %>%
          sapply(function(x) ifelse(x == "murder_andnonnegligentmanslaughter", 
                                    "murder_and_nonnegligent_manslaughter", x)) %>% unname() %>%
          sapply(function(x) ifelse(x == "aggravatedassault", "aggravated_assault", x)) %>% unname()
     print("step 2")
     scraped_raw2 <- 
          scraped_raw %>%     
          filter((metropolitan_statistical_area == "Flint, MI M.S.A." & counties_principal_cities == "Estimated total") | 
                      counties_principal_cities == "Total area actually reporting")
     print("step 3")
     scraped_raw3 <- scraped_raw2 %>%
          mutate_at(vars(population:motor_vehicle_theft), funs(parse_number))
     print("step 4")
     scraped_raw4 <- scraped_raw3 %>%
          select(-counties_principal_cities)
     print("step 5")
     scraped_raw5 <- scraped_raw4 %>%
          gather(offense_category, count, murder_and_nonnegligent_manslaughter:aggravated_assault, 
                 burglary:motor_vehicle_theft)
     print("step 6")
     scraped_raw6 <- scraped_raw5 %>%
          select(-c(population, violent_crime, property_crime))
     print("step 7")
     scraped_raw7 <- scraped_raw6 %>% 
          arrange(metropolitan_statistical_area, offense_category)
     print("step 8")
     scraped_raw8 <- scraped_raw7 %>% 
          rename(msa = metropolitan_statistical_area) 
     print("step 9")
     scraped_raw9 <- scraped_raw8 %>% 
          mutate(year = ucr_year) 
     print("step 10")
     scraped_raw10 <- scraped_raw9 %>% 
          select(year, msa, offense_category, count)
}

ucr_metadata <- 
     tribble(
          ~year, ~link,
          2005, "https://www2.fbi.gov/ucr/05cius/data/table_06.html",
          2006, "https://www2.fbi.gov/ucr/cius2006/data/table_06.html",
          2007, "https://www2.fbi.gov/ucr/cius2007/data/table_06.html",
          2008, "https://www2.fbi.gov/ucr/cius2008/data/table_06.html",
          2009, "https://www2.fbi.gov/ucr/cius2009/data/table_06.html",
          2010, "https://ucr.fbi.gov/crime-in-the-u.s/2010/crime-in-the-u.s.-2010/tables/table-6",
          2011, "https://ucr.fbi.gov/crime-in-the-u.s/2011/crime-in-the-u.s.-2011/tables/table-6",
          2012, "https://ucr.fbi.gov/crime-in-the-u.s/2012/crime-in-the-u.s.-2012/tables/6tabledatadecpdf/table-6",
          2013, "https://ucr.fbi.gov/crime-in-the-u.s/2013/crime-in-the-u.s.-2013/tables/6tabledatadecpdf/table-6",
          2014, "https://ucr.fbi.gov/crime-in-the-u.s/2014/crime-in-the-u.s.-2014/tables/table-6",
          2015, "https://ucr.fbi.gov/crime-in-the-u.s/2015/crime-in-the-u.s.-2015/tables/table-6"
     )

ucr_data_list <- vector(mode = "list", length = nrow(ucr_metadata))

for(i in 1:nrow(ucr_metadata)){
     print(paste0("# ", i, ": ", ucr_metadata$link[i]))
     ucr_data_list[[i]] <- scrape_ucr_data(ucr_year = ucr_metadata$year[i], link = ucr_metadata$link[i])
}

ucr_data <- bind_rows(ucr_data_list)

print("Writing data to CSV")
write_csv(ucr_data, "ucr_data/ucr_data.csv")
