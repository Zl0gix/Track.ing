############################################################################
## Initialisation to make the two functions work

import json
import time
from datetime import date
import re
import requests
import base64

import pandas as pd
import numpy as np
import time
import re

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from requests_html import HTMLSession
import nest_asyncio

nest_asyncio.apply()
s = HTMLSession()

# API key needs to be hidden
"""
from secret import Secrets

secrets = Secrets()

client_id = secrets["spotifyClientID"]
client_secret = secrets["spotifyClientSecret"]

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
                                                           client_secret=client_secret))
"""

class Artist:
    def __init__(self, uri, name, followers, image, id) -> None:
        self.uri = uri
        self.name = name
        self.followers = followers
        self.image = image
        self.id = id

    def as_dict(self):
        return {
            'uri': self.uri,
            'name': self.name,
            'followers': self.followers,
            'image': self.image,
            'id': self.id,
        }

from Backend import sp

############################################################################
## Function for Spotify suggestions when entering the website

def getArtistInfo(artistName, number) -> list[Artist]:
    artists = []
    artists_info = sp.search(artistName, limit = number, type = 'artist')['artists']['items']

    if len(artists_info) == 0:
        artists_info = sp.search('Daft Punk', limit = 1, type = 'artist')['artists']['items']

    for artist_info in artists_info:
        artist_uri = artist_info['uri']
        artist_id = artist_info['id']
        ## We retrieve the official name for accurate seeking on other websites
        artist_name = artist_info['name']
        artist_followers = artist_info['followers']['total']
        if len(artist_info['images']) > 0:
            artist_image = artist_info['images'][0]['url']
        else:
            artist_image = 'https://i.imgur.com/3z7wB8n.png'
    
        artists.append(Artist(artist_uri, artist_name, artist_followers, artist_image, artist_id))

    return artists

############################################################################
## Function for Spotify artist from ID

def getArtistInfoFromID(artistID) -> Artist:
    artist_info = sp.artist(artistID)

    artist_uri = artist_info['uri']
    artist_id = artist_info['id']
    ## We retrieve the official name for accurate seeking on other websites
    artist_name = artist_info['name']
    artist_followers = artist_info['followers']['total']
    if len(artist_info['images']) > 0:
        artist_image = artist_info['images'][0]['url']
    else:
        artist_image = 'https://i.imgur.com/3z7wB8n.png'

    return Artist(artist_uri, artist_name, artist_followers, artist_image, artist_id)

############################################################################
## Function for dynamic data retrieval, data goes into DynamicData/

## Used in the below function named GetArtistAlbumsAndTracks(artistName)
def getArtistAlbums(artistURI):
    n = 0
    allAlbums = []
    # Prevent duplicates
    allAlbumsNames = []

    album_types = ['album', 'single']

    while len(sp.artist_albums(artistURI, album_type='album,single', limit=50, offset = n)['items']) > 0:
        
        albums = sp.artist_albums(artistURI, album_type='album,single', limit=50, offset = n)['items']
        
        for album in albums:
            if album['name'] not in allAlbumsNames:
                allAlbumsNames.append(album['name'])

                albumSpecs = {}
                albumSpecs['id'] = album['id']
                albumSpecs['name'] = album['name']
                albumSpecs['release_date'] = album['release_date']
                albumSpecs['total_tracks'] = album['total_tracks']
                allAlbums.append(albumSpecs)
        
        n += 50

    return allAlbums


def GetArtistAlbumsAndTracks(artistName):
    ## By default, considers only first artist mentioned
    artistURI = getArtistInfo(artistName, 1)[0][0]
    albums = getArtistAlbums(artistURI)

    dfAlbums = pd.DataFrame(albums)

    ### Retrieves all albums' tracks
    allTracks = []

    for album in list(dfAlbums['id']):
        spAlbumTracks = sp.album_tracks(album)['items']
        albumTracks = []
        for track in spAlbumTracks:
            albumTracks.append(track['id'])
        allTracks.append(albumTracks)

    dfAlbums['tracks_ids'] = allTracks

    ### New dataframe dedicated to tracks
    dfTracks = dfAlbums.explode('tracks_ids')[::-1].reset_index().drop(columns=['index'])
    dfTracks = dfTracks.rename(columns = {'id' : 'albumID', 'name' : 'albumName', 'tracks_ids' : 'trackID'})

    ### Additional data about tracks
    trackNames = []
    trackPopularities = []
    for track in list(dfTracks['trackID']):
        trackInfo = sp.track(track)
        trackNames.append(trackInfo['name'])
        trackPopularities.append(trackInfo['popularity'])

    dfTracks['trackName'] = trackNames
    dfTracks['trackPop'] = trackPopularities

    print(f'Stats for {artistName} --')

    print(f'Number of albums/EPs/singles : {len(dfAlbums)}')
    dfAlbums.drop(columns=['tracks_ids'])[::-1].to_csv('DynamicData/artist_albums.csv', index = False)

    print(f'Number of tracks : {len(dfTracks)}')
    #dfTracks.to_csv('artist_albumsTracks.csv', index = False)

    dfTracks = dfTracks.drop_duplicates(subset=['trackName'], keep='first')

    print(f'Number of unique tracks : {len(dfTracks)}')
    dfTracks.to_csv('DynamicData/artist_uniqueTracks.csv', index = False)


def GetSamplingInfo(dfTracks, artistName):
    tracksNbSamples = []
    tracksNbSampled = []
    tracksNbRemixes = []

    urlSearchPrefix = "https://www.whosampled.com/search/?q="
    urlPrefix = "https://www.whosampled.com/"
    for track in dfTracks['trackName']:
        URLsearch = urlSearchPrefix + track.replace(' ', '+') + '+' + artistName.replace(' ', '+')

        response = s.get(URLsearch)
        trackRef = ''
        trackRefs = re.findall(r'<a class="trackTitle" href=(.*)>\S', response.text)

        nbSamples = np.NaN
        nbSampled = np.NaN
        nbRemixes = np.NaN

        if (len(trackRefs) > 0):

            trackRef = trackRefs[0]

            url = urlPrefix + trackRef[2:-1]

            response = s.get(url)
            #print(response.text)
            headers = re.findall(r'<span class="section-header-title">(.*)</span>', response.text)

            for header in headers:
                if (re.match(r'Contains samples', header)):
                    nbSamples = int(re.findall('\d+', header)[0])
                else:
                    nbSamples = 0
                if (re.match(r'Was sampled', header)):
                    nbSampled = int(re.findall('\d+', header)[0])
                else:
                    nbSampled = 0
                if (re.match(r'Was remixed', header)):
                    nbRemixes = int(re.findall('\d+', header)[0])
                else:
                    nbRemixes = 0

        tracksNbSamples.append(nbSamples)
        tracksNbSampled.append(nbSampled)
        tracksNbRemixes.append(nbRemixes)

    dfTracks['nbSamples'] = tracksNbSamples
    dfTracks['nbSampled'] = tracksNbSampled
    dfTracks['nbRemixes'] = tracksNbRemixes


def ArtistPotentialDynamicData(artistName):
    start = time.time()

    artist_uri = getArtistInfo(artistName, 1)[0][0]
    # Writes necessary csvs if needed
    if (artist_uri not in pd.read_csv('Data/albumsTOP12artists.csv')['artist_uri'].unique()):
        GetArtistAlbumsAndTracks(artistName)

        artistName = artistName.replace('/', '-')
        
        dfCurrentArtistAlbums = pd.read_csv('DynamicData/artist_albums.csv', index_col=False)
        dfCurrentArtistAlbums['artist_uri'] = artist_uri
        dfCurrentArtistAlbums.to_csv(f'DynamicData/artist_albums.csv')

        dfCurrentArtistTracks = pd.read_csv('DynamicData/artist_uniqueTracks.csv', index_col=False)
        GetSamplingInfo(dfCurrentArtistTracks, artistName)
        dfCurrentArtistTracks['artist_uri'] = artist_uri
        dfCurrentArtistTracks.to_csv(f'DynamicData/artist_uniqueTracks.csv')

    print(f'Time needed for {artistName} : {time.time() - start} seconds.')


#print(getArtistInfo('Metallica', 1))
#ArtistPotentialDynamicData('Mariah Carey')
