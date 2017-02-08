library(dplyr); library(rvest); library(stringr); library(lubridate);
library(readr); library(httr); library(readxl)

get_apd_crime_data <- function(write_files = TRUE){
     if(!dir.exists("Data")){
          dir.create("Data")
     }
     
     crime_links_html <- 
          read_html("http://www.atlantapd.org/i-want-to/crime-data-downloads") %>% 
          html_nodes("#widget_362_0_197 .content_link")
     
     crime_links <- 
          data_frame(filename = crime_links_html %>% html_text(),
                     url = crime_links_html %>% html_attr("href") %>% paste0("http://www.atlantapd.org", .))
     
     temp_list <- vector(mode = "list", length = 9)
     for(i in seq_along(crime_links$url)){
          temp_list[[i]] <- headers(GET(crime_links$url[i]))     
     }
     
     crime_links_fileinfo <- 
          lapply(temp_list, function(x) data_frame(type = x$`content-type`,
                                                   disposition = x$`content-disposition`, 
                                                   documenttitle = x$`content-documenttitle`,
                                                   lastmodified = x$`last-modified`)) %>%
          bind_rows()
     
     crime_links <- bind_cols(crime_links, crime_links_fileinfo) %>% 
          mutate(filename2 = str_sub(disposition, start = 11, end = -2))
     
     crime_links
     
     get_crime_zipfile <- function(zip.url){
          td <- tempdir()
          print(paste0("Reading ", zip.url))
          tf <- tempfile(tmpdir=td, fileext=".zip") 
          download.file(zip.url, tf, mode = "wb")
          fname <- unzip(tf, list=TRUE)$Name[1] 
          unzip(tf, files=fname, exdir=td,overwrite=TRUE)
          fpath <- file.path(td, fname)
          print(excel_sheets(fpath))
          read_excel(fpath, sheet = "Query")
     }
     
     get_crime_nonzipfile <- function(file.url, file.name){
          print(paste0("Downloading file: ", file.name, ", URL: ", file.url))
          download.file(url = file.url, destfile = file.name, mode = "wb")
          print(excel_sheets(file.name))
          return(read_excel(file.name, sheet="Query"))
     }
     
     crime_data <- vector(mode = "list", length = nrow(crime_links))
     for(i in seq_along(crime_links$filename)){
          if(crime_links$type[i] == "application/zip"){
               crime_data[[i]] <- get_crime_zipfile(crime_links$url[i])
          }else if(crime_links$type[i] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"){
               crime_data[[i]] <- 
                    get_crime_nonzipfile(crime_links$url[i], file.name = crime_links$filename2[i])
          }
     }
     
     xlsx_filenames <- crime_links %>% .[str_detect(.$filename2, "\\.xlsx"),] %>% .$filename2
     for(i in seq_along(xlsx_filenames)){
          unlink(xlsx_filenames[i])
     }
     
     crime_data2 <- 
          bind_rows(crime_data) %>%
          mutate(rpt_date = mdy(rpt_date), 
                 occur_datetime = mdy_hms(paste(occur_date, occur_time)), occur_date = mdy(occur_date),
                 poss_datetime = mdy_hms(paste(poss_date, poss_time)), poss_date = mdy(poss_date),
                 MaxOfnum_victims = as.integer(MaxOfnum_victims),
                 x = round(as.numeric(x), 5), y = round(as.numeric(y), 5))
     
     if(write_files){
          print("Writing Data/crime_data.rds")
          write_rds(crime_data2, "Data/crime_data.rds")
          
          print("WritingData/crime_data.csv")
          write_csv(crime_data2, "Data/crime_data.csv")
          
          print("Writing Data/crime_links.csv")
          write_csv(crime_links, "Data/crime_links.csv")
     }
     
     return(crime_data2)
}

crime_data <- get_apd_crime_data(write_files = TRUE)