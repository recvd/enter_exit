# Updates and Notes

- **1/24/2019**:  Realized the first version of the entry/exit data has an issue with showing businesses exiting in the last year such that there are always equal counts of businesses entering and exiting. This only happens if 2014 is the last year.  This boils down to the fact that we can't know whether a business exits in 2014, because it would have to not be there in 2015 (which we don't have data for)
  - Resolved by substituting np.nan for 2014 in LastYear
- **1/25/2019**: Realized the idea of "Total" includes ALL business in NETS, not just ones we defined as matching a business, which seems relatively important.
- Similarly to the problem on 1/24, need to substitute np.nan for 1990 in FirstYear because we don't know if these businesses actually entered on this year. After this fix i reuploaded the new version to S3.
- **1/28/2019** For the purpose of being able to determine the number of any businesses in any tract at any year, we should include the starting number of businesses as a baseline.  
- **1/30/2019** finished fix of interval datasets and added NaN values 
- **1/31/2019** feather is an option later but lets ignore it for now

# Ideas

- Graphs of actual business numbers rather than just change 
- Changes in terms of percent of originial
- Plot distribution histograms interactively, with a slider bar for time



# Where We Left Off
- Spatial join put everything in different columns which is throwing shit off, gotta fix it in arcmap