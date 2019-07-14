#!/usr/bin/env python
# coding: utf-8

# # Segmenting and Clustering Neighborhoods in Toronto

# **Extracting out Toronto neighbourhood data from their wikipedia page https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M**

# ### Reading data from HTML using Beautiful Soup Library

# Importing Beautiful Soup package and other necessary libraries for data extraction

# In[1]:


# from bs4 import BeautifulSoup
# import requests
# source = requests.get(' https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M').text
# soup = BeautifulSoup(source,'lxml')
# table = soup.table  # or table = soup.find('table')
# table_rows = table.find_all('tr')
# for tr in table_rows:
#     td = tr.find_all('td')
#     row = [i.text for i in td]
#     print(row)


# Let us see another method to extract out datframe from html web page
# ### Reading datframe from HTML through pandas 
# It is much simpler to extract out dataframe from html using pandas compared to Beautiful Soup package

# In[5]:


import pandas as pd
data = []
dfs = pd.read_html('https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M',header=0)
for df in dfs:
    data.append(df)

table = pd.DataFrame(data[0])



# **1. Removing the cells with borough 'Not assigned'**

# In[6]:


table.drop(table.index[table.Borough == 'Not assigned'], inplace=True)


# **2. Combining rows with same postal code**

# In[7]:


table_final = table.groupby(['Postcode','Borough'])['Neighbourhood'].apply(','.join).reset_index()


# **3. For cells having a borough but a 'Not assigned' neighborhood, replacing neighborhood with the borough name** 

# In[8]:


table_final.loc[table_final['Neighbourhood'] == 'Not assigned']
table_final.iloc[85,2] = table_final.iloc[85,1]



# **Shape of final dataframe**

# In[11]:


table_final


# # Location of Postal codes

# **Importing dataframe which contains latitude and longitute of postal codes**

# In[7]:


import pandas as pd
table_2 = pd.read_csv('C:/Users/saksh/Downloads/Geospatial_Coordinates.csv')


# **Joining two datframes**

# In[14]:


join = table_2.set_index('Postal Code').join(table_final.set_index('Postcode'))
join = join.reset_index()
join


# In[9]:


join.Borough.nunique()
join.head


# The final dataframe contains 103 Neighbourhoods and 11 Boroughs

# In[10]:


#!conda install -c conda-forge geopy --yes 
from geopy.geocoders import Nominatim # convert an address into latitude and longitude values

import folium # map rendering library


# In[11]:


address = 'Toronto, ontario'

geolocator = Nominatim(user_agent="on_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of Toronto are {}, {}.'.format(latitude, longitude))


# In[12]:


map_toronto = folium.Map(location = [latitude,longitude], zoom_start=10)

# Add markers to map
for lat, lon, neighb, bor in zip(join['Latitude'], join['Longitude'], join['Neighbourhood'], join['Borough']):
    label = '{},{}'.format(neighb,bor)
    label = folium.Popup(label, parse_html =True)
    folium.CircleMarker([lat,lon],
                        radius = 5,
                        Popup = label,
                        color = 'blue',
                        fill = True,
                        fill_color = '#3186cc',
                        fill_opacity = 0.7,
                        parse_html =False).add_to(map_toronto)
    
map_toronto


# In[19]:


# Let us examine DowntownToronto 

DownTor_data = join[join['Borough']=='Downtown Toronto'].reset_index(drop=True)
DownTor_data


# In[20]:


address = 'Downtown Toronto, ontario'

geolocator = Nominatim(user_agent="on_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of Downtown Toronto are {}, {}.'.format(latitude, longitude))


# As we did with all of Toronto City, let's visualize the neighborhoods of Downtown Toronto in it.

# In[21]:


map_downtown = folium.Map(location = [latitude,longitude], zoom_start=10)

# Add markers to map
for lat, lon, neighb, bor in zip(DownTor_data['Latitude'], DownTor_data['Longitude'], DownTor_data['Neighbourhood'], DownTor_data['Borough']):
    label = '{},{}'.format(neighb,bor)
    label = folium.Popup(label, parse_html =True)
    folium.CircleMarker([lat,lon],
                        radius = 5,
                        Popup = label,
                        color = 'blue',
                        fill = True,
                        fill_color = '#3186cc',
                        fill_opacity = 0.7,
                        parse_html =False).add_to(map_downtown)
    
map_downtown


# #### Define Foursquare Credentials and Version

# In[22]:


CLIENT_ID = 'U3CPOLQKZXPSRE3LUXCBAWQONS1OFXIE42UOJBEL3345MMSR' # your Foursquare ID
CLIENT_SECRET = '4WD4I5RY0DMYPBN0QJDEAVFOF2FCA0ISOHCUAH4BR4RPCO01' # your Foursquare Secret
VERSION = '20180605' # Foursquare API version

print('Your credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)


# #### Let's explore the first neighborhood in our dataframe.

# Get the neighborhood's name.

# In[27]:


DownTor_data.loc[0,'Neighbourhood']


# Get the neighborhood's latitude and longitude values.

# In[30]:


neighborhood_latitude = DownTor_data.loc[0, 'Latitude'] # neighborhood latitude value
neighborhood_longitude = DownTor_data.loc[0, 'Longitude'] # neighborhood longitude value

neighborhood_name = DownTor_data.loc[0, 'Neighbourhood'] # neighborhood name

print('Latitude and longitude values of {} are {}, {}.'.format(neighborhood_name, 
                                                               neighborhood_latitude, 
                                                               neighborhood_longitude))


# #### Now, let's get the top 100 venues that are in Rosedale within a radius of 500 meters.

# First, let's create the GET request URL.

# In[32]:


# type your answer here
LIMIT = 100
radius = 500

url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
    CLIENT_ID, 
    CLIENT_SECRET, 
    VERSION, 
    neighborhood_latitude, 
    neighborhood_longitude, 
    radius, 
    LIMIT)


# In[34]:


import requests # library to handle requests
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe
results = requests.get(url).json()
results


# let's borrow the **get_category_type** function from the Foursquare lab.

# In[35]:


# function that extracts the category of the venue
def get_category_type(row):
    try:
        categories_list = row['categories']
    except:
        categories_list = row['venue.categories']
        
    if len(categories_list) == 0:
        return None
    else:
        return categories_list[0]['name']


# Now we are ready to clean the json and structure it into a *pandas* dataframe.

# In[38]:


venues = results['response']['groups'][0]['items']
    
nearby_venues = json_normalize(venues) # flatten JSON

# filter columns
filtered_columns = ['venue.name', 'venue.categories', 'venue.location.lat', 'venue.location.lng']
nearby_venues =nearby_venues.loc[:, filtered_columns]

# filter the category for each row
nearby_venues['venue.categories'] = nearby_venues.apply(get_category_type, axis=1)

# clean columns
nearby_venues.columns = [col.split(".")[-1] for col in nearby_venues.columns]

nearby_venues.head()


# In[37]:


print('{} venues were returned by Foursquare.'.format(nearby_venues.shape[0]))


# ## Let's create a function to repeat the same process to all the neighborhoods in Downtown Toronto

# In[40]:


def getNearbyVenues(names, latitudes, longitudes, radius=500):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood', 
                  'Neighborhood Latitude', 
                  'Neighborhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)


# In[42]:


downtown_venues = getNearbyVenues(names=DownTor_data['Neighbourhood'],
                                   latitudes=DownTor_data['Latitude'],
                                   longitudes=DownTor_data['Longitude']
                                  )


# #### Let's check the size of the resulting dataframe

# In[44]:


print(downtown_venues.shape)
downtown_venues.head()


# Let's check how many venues were returned for each neighborhood

# In[46]:


downtown_venues.groupby('Neighborhood').count()


# In[ ]:





# In[ ]:




