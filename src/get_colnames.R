library(stringr)
library(purrr)

get_colnames <- function(filepath){
  # Works for a pandas column multiindex + row multiindex, both of order 2
  con = file(filepath, "r")
  cols = readLines(con, n=3)
  close(con)
  
  rows <- str_split(cols, ",") %>% 
    map(function(l) l[l != ""])
  
  # handle the columns
  cols <- str_c(rows[[1]], ".", rows[[2]])
  
  #handle the row "index"
  rows <- rows[[3]]
  
  return(c(rows, cols))
}