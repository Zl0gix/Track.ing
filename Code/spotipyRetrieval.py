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

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from secret import Secrets

secrets = Secrets()

client_id = secrets.spotifyClientID
client_secret = secrets.spotifyClientSecret

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
                                                           client_secret=client_secret))


############################################################################
## Function for Spotify suggestions when entering the website

def getArtistInfo(artistName, number):
    artists = []
    artists_info = sp.search(artistName, limit = number, type = 'artist')['artists']['items']

    for artist_info in artists_info:

        artist_uri = artist_info['uri']
        ## We retrieve the official name for accurate seeking on other websites
        artist_name = artist_info['name']
        artist_followers = artist_info['followers']['total']
        artist_image = artist_info['images'][0]['url']
    
        artists.append([artist_uri, artist_name, artist_followers, artist_image])

    return artists


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


############################################################################
## Function for dynamic data retrieval, data goes into DynamicData/

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


#print(getArtistInfo('Metallica', 1))
#GetArtistAlbumsAndTracks('Mariah Carey')
