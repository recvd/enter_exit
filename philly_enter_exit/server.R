library(shiny)
library(leaflet)
library(tidyverse)
library(sf)
library(here)

data <- read_sf(here("philly_enter_exit")) 

shinyServer(function(input, output) {
  
  business_cat <- reactive({
    switch(input$cat,
      "Total" = "TOTAL",
      "All Clinical Treatment" = "ACTH",
      "Walking Destinations" = "WALH",
      "Fast Food" = "FFAH")
  })
  
  filteredData <- reactive({
    filter(data, year==as.integer(input$yr),
                    bsnss_t==business_cat()) 
  })
  
  # Separate bins for whether we're plotting Net Change or Enter/Exit rates  
  bins_entex <- c(0, 5, 10, 25, 50, 100, 250, 500, 1000, Inf)
  bins_net <- c(-Inf, -100, -50, -25, -10, -5, 0, 5, 10, 25, 50, 100, Inf)
  
  output$myMap <- renderLeaflet({
    
    # Enter, exit or net change
    rate_type <- switch(input$measure,
                        "entr_yr" = filteredData()$entr_yr,
                        "exit_yr" = filteredData()$exit_yr,
                        "net" = filteredData()$net)
    
    # set correct color binning based on Net Change 
    pal <- switch(input$measure,
                  "entr_yr" = colorBin("viridis", domain = rate_type, bins = bins_entex),
                  "exit_yr" = colorBin("viridis", domain = rate_type, bins = bins_entex),
                  "net" = colorBin("Spectral", domain = rate_type, bins = bins_net)
                  )
    
    leaflet(filteredData()) %>%
      setView(lng = -75.1125, lat = 39.9971, zoom = 10.5) %>%
      addProviderTiles("MapBox", options = providerTileOptions(
        id = "mapbox.light",
        accessToken = Sys.getenv('MAPBOX_ACCESS_TOKEN'))) %>% 
      addTiles() %>% 
      addPolygons(weight=1,
                  color="red",
                  fillColor = ~pal(rate_type),
                  opacity=.5,
                  fillOpacity = .7) %>%
      addLegend(pal = pal,
                values = ~rate_type,
                opacity = 0.7,
                title = NULL,
      position = "bottomright")
    
  })
  
  
})
