library(dplyr); library(rvest); library(stringr); library(lubridate);
library(readr); library(httr); library(readxl)

get_atlanta_crime_data <- function(write_files = TRUE){
     if(!dir.exists("Data")){
          dir.create("Data")
     }
     
     atlanta_crime_links_html <- 
          read_html("http://www.atlantapd.org/i-want-to/crime-data-downloads") %>% 
          html_nodes("#widget_362_0_197 .content_link")
     
     atlanta_crime_links <- 
          data_frame(filename = atlanta_crime_links_html %>% html_text(),
                     url = atlanta_crime_links_html %>% html_attr("href") %>% paste0("http://www.atlantapd.org", .))
     
     temp_list <- vector(mode = "list", length = 9)
     for(i in seq_along(atlanta_crime_links$url)){
          temp_list[[i]] <- headers(GET(atlanta_crime_links$url[i]))     
     }
     
     atlanta_crime_links_fileinfo <- 
          lapply(temp_list, function(x) data_frame(type = x$`content-type`,
                                                   disposition = x$`content-disposition`, 
                                                   documenttitle = x$`content-documenttitle`,
                                                   lastmodified = x$`last-modified`)) %>%
          bind_rows()
     
     atlanta_crime_links <- bind_cols(atlanta_crime_links, atlanta_crime_links_fileinfo) %>% 
          mutate(filename2 = str_sub(disposition, start = 11, end = -2))
     
     atlanta_crime_links
     
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
     
     atlanta_crime_data <- vector(mode = "list", length = nrow(atlanta_crime_links))
     for(i in seq_along(atlanta_crime_links$filename)){
          if(atlanta_crime_links$type[i] == "application/zip"){
               atlanta_crime_data[[i]] <- get_crime_zipfile(atlanta_crime_links$url[i])
          }else if(atlanta_crime_links$type[i] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"){
               atlanta_crime_data[[i]] <- 
                    get_crime_nonzipfile(atlanta_crime_links$url[i], file.name = atlanta_crime_links$filename2[i])
          }
     }
     
     xlsx_filenames <- atlanta_crime_links %>% .[str_detect(.$filename2, "\\.xlsx"),] %>% .$filename2
     for(i in seq_along(xlsx_filenames)){
          unlink(xlsx_filenames[i])
     }
     
     atlanta_crime_data2 <- 
          bind_rows(atlanta_crime_data) %>%
          mutate(rpt_date = mdy(rpt_date), 
                 occur_datetime = mdy_hms(paste(occur_date, occur_time)), occur_date = mdy(occur_date),
                 poss_datetime = mdy_hms(paste(poss_date, poss_time)), poss_date = mdy(poss_date),
                 MaxOfnum_victims = as.integer(MaxOfnum_victims),
                 x = round(as.numeric(x), 5), y = round(as.numeric(y), 5))
     
     if(write_files){
          print("Writing atl/AtlantaCrime.csv")
          write_csv(atlanta_crime_data2, "atl/AtlantaCrime.csv")
          
          print("Writing atl/AtlantaCrime_Links.csv")
          write_csv(atlanta_crime_links, "atl/AtlantaCrime_Links.csv")
     }
     
     return(atlanta_crime_data2)
}

atlanta_crime_data <- get_atlanta_crime_data(write_files = TRUE)