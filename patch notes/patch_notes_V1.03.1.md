# **V1.03.1 Patch Notes**  

## **New Commands/Features:**  
Currently Adding the following groups with thousands of photos:  
**2NE1, SATURDAY, Purplebeck, BVNDIT, BOL4, Berry Good, Cignature, GWSN, Gugudan**  
`%lyrics` was coded (still waiting on the API key).  
Removed `%getlinks`, `%tenor`, `%sort`, `%scrapelink`  
  
## **Bug/Issue Fixes:**  
`%addemoji` now refers to the optimize url on ezgif instead of resizing.  
`%deletegroup` works now.  
`%randomidol` is now limited for non-patrons.  
Fixed `%disableinteraction` error that didn't allow more than one interaction to be disabled.  
Tables Removed: `scrapedlinks`, `groupphotocount`  
`%scandrive` now puts links in the table `uploadimagelinks` instead of `imagelinks`  
Loop that updates group photo count is now set from 24 to 12 hours.  
Aliases and Idol to Groups now have proper correlation in the database to minimize a lot of unnecessary code and allow for smoother SQL queries.  