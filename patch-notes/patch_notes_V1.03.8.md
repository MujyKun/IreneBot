# **V1.03.8 Patch Notes**  

## **New Commands/Features:**  
Full/Stage Name and the Idol Id now appears when calling an idol photo.  

Channels with Verse and Self Assignable Roles have been added as datadog metrics.  

If `%time (user)` is used and the input is not a user, it will check for the time in a timezone.  

Server-Sided NWord LB has been added.  

Vote Requirement increased from 12 hours to 24 hours.  

Added Twitch Notifications (`%addtwitch` `%listtwitch` `%removetwitch`, `%settwitchchannel`, `%settwitchrole`)

Added pagination to `%listroles`  

Added link to commands in `%help`  

Added Scientific Notation to currency leaderboard if the amount is above the known value places.  

15 results now show on bias game leaderboards instead of 10.  

## **Bug/Issue/Backend Fixes:**  

Fixed memory leak issues with biasgame.  

Fixed Majority API issues.  

Fixed guessing game not properly loading.  

The entirety of the API was recoded in Python.  

Unsupported locale on host is accounted for in regards to user timezones.  

Single pages on music are not longer paginated.  

Trash emoji on dead images now works.  

Kill command now properly terminates background processes  

`%nwl` now displays 10 results instead of 11.  

Fixed the inaccurate amount of text channels subbed metrics that are being sent.  

Fixed Guessing Game randomly crashing from names that start with the prefix.  

Fixed normal patrons not being considered a patron once discord cache loaded.  

Fixed duplicate stream notifications. Check time was increased from 30 seconds to 1 minute.  






