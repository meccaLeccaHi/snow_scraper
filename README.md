# SI 206 Final Project- Cooper Seligson
## View My Project Online at:
https://si206-final.herokuapp.com/
## To Run my Project:
Install 
```
requirements.txt
```
To view the data already in the cache, run the following code in your terminal
```
python3 app.py
```
Copy and paste the URL into a browser to view the project

### If you want to update the snowfall data
```
rm cache-opensnow.json
python3 main_file.py
python3 app.py
```
Copy and paste the URL into a browser to view the project

### Data Sources
- [Open Snow](www.opensnow.com)
- [Yelp Fusion](https://www.yelp.com/fusion)
- [Google Gecode](https://developers.google.com/maps/documentation/geocoding/start)

Both Yelp and Google need API keys, in a file called secrets.py

It should be organized as follows:
```
# secrets.py
yelp_api_key = 'API_KEY_HERE'
google_places_key = 'API_KEY_HERE'
```
### Main Code Structure
```
# app.py

# This class takes in (name, total, state, rating) and creates a class for the proper text format on Plotly
class Text

# This class takes in (rating) and returns the correct Unicode star characters for Plotly
class Rating:
```
```
# opensnow.py

# This function crawls the Opensnow website for each state and provience that they forecast snow for
def crawl_main():

# This function takes in a URL for a state on Opensnow and crawls the page to recieve snow prediction data for each resort
def crawl_state(url):

# This file caches the data recieved from wwww.opensnow.com
```
```
# google_api.py

# This function crawls uses the ski mountain name and the state to request data from the Google Geocode API and return each 
# places Latitude and Longitude
def get_lat_and_long(ski_name, ski_state):

# This file caches the data recieved from the Google API
```
```
# main_file.py

# This function creates a Databse with three different tables
def init_db():

# This function inserts all the neccesary data into the three database tables
def insert_data()
```
The Following Files are used for the Heroku Wesbite:
```
Procfile
runtime.txt
```

### Built With
- [Atom](https://atom.io/)
- [Plotly Dash](https://plot.ly/products/dash/)
- [DB Browser for SQLite](http://sqlitebrowser.org/)
- [Stack Overflow!](https://stackoverflow.com/)

## More Information on the "About This Project" page of the program
\
\
\
![UM](https://umich.tfaforms.net/forms/get_image/8/2bc3c431222001fedf392dab5608e09d-signature_marketing_U_blue.png)
