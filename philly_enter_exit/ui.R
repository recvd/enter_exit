#
# This is the user-interface definition of a Shiny web application. You can
# run the application by clicking 'Run App' above.
#
# Find out more about building applications with Shiny here:
# 
#    http://shiny.rstudio.com/
#

library(shiny)
library(leaflet)

# Define UI for application that draws a histogram
shinyUI(fluidPage(
  
  # Application title
  titlePanel("Philadelphia Business Entrance/Exit Rates"),
  
  # Sidebar with a slider input for number of bins 
  sidebarLayout(
    sidebarPanel(
      radioButtons("measure", "Rate type:",
                   list("Enter" = "entr_yr",
                        "Exit" = "exit_yr",
                        "Net Change" = "net")),
      br(),
      selectInput("cat", "Category:", 
                  choices = c("Total",
                              "All Clinical Treatment",
                              "Walking Destinations",
                              "Fast Food")),
      br(),
     sliderInput("yr",
                 "Year",
                 min = 1990,
                 max = 2013,
                 value = 1991,
                 sep = "")
    ),
    
    # Show a plot of the generated distribution
    mainPanel(
       leafletOutput("myMap")
    )
    
    
  )
))
