# Track.ing
A python web application project developed by Yves Touitou and Raphaël Richard within the ESILV's 5th year course named "Web scraping and data processing".

## Objective
Find interesting statistics about your favorite artists thanks to our customized metrics.

### How it works
It gets data from multiple sources:
- Spotify API
- whosampled.com
- Billboard top 200 (from 2020 to 2022)
- ChartMasters Studio Albums Sales

<br/>

You first write down the artist you want to know about in the search bar entering the website. You will be able to link your search with an official Spotify artist thanks to suggestions.  
If this artist is already in our database, it will display your artist's overview quickly. Otherwise, it will dynamically retrieve all the albums, tracks and the sampling information about them.

### Point of Track.ing

Our customized metrics offer you a quick overview about the artist whereas the graphs generated below allow you to understand these metrics.
Here are the metrics (rated between 0 and 100):
- Consistency :muscle:
- Hard Working :books:
- Original :heavy_plus_sign:
- Inspirational :star:
- G.O.A.T :goat:

### What's improvable

Except adding other sources to make the metrics even more precise, we're currently missing every song's play count closing many doors about analyzing an artist. This type of data is hidden by song streaming platforms and this would need a collaboration acquiring it.

### How to use it

First go to the website folder and run the command "py manage.py runserver".
Then go to http://127.0.0.1:8000/Tracking and type the name of the artist you are searching for