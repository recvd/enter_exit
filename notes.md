# Updates and Notes

- **1/24/2019**:  Realized the first version of the entry/exit data has an issue with showing businesses exiting in the last year such that there are always equal counts of businesses entering and exiting. This only happens if 2014 is the last year.  This boils down to the fact that we can't know whether a business exits in 2014, because it would have to not be there in 2015 (which we don't have data for)
  - Resolved by substituting np.nan for 2014 in LastYear
- **1/25/2019**: Realized the idea of "Total" includes ALL business in NETS, not just ones we defined as matching a business, which seems relatively important.

# Where We Left Off
- 