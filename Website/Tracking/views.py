from django.shortcuts import render

from django.http import HttpResponse
from django.template import loader

from Backend.spotipyRetrieval import getArtistInfo, getArtistInfoFromID, ArtistPotentialDynamicData
from Backend.artistMetricsCalculation import GetMetrics
from Backend.graph import Radar

import json

# Create your views here.
def index(request):
    template = loader.get_template('index.html')
    context = {
        'title': 'Tracking - Search',
        'data': getArtistInfo('The Beatles', 3),
    }
    return HttpResponse(template.render(context, request))

def overview(request):
    artist = None
    if request.method == 'GET':
        if request.GET.get('ArtistName'):
            artist = getArtistInfo(request.GET.get('ArtistName'), 1)
        elif request.GET.get('SpotifyID'):
            artist = getArtistInfoFromID(request.GET.get('SpotifyID'))
        else:
            return HttpResponse('There was an error')
    template = loader.get_template('overview.html')
    
    ArtistPotentialDynamicData(artist.name)

    context = {
        'title': 'Tracking - Overview',
        'artist': artist,
        'radar': Radar(GetMetrics(artist.uri, artist.name, artist.followers)),
    }
    return HttpResponse(template.render(context, request))

def search(request):
    if request.method == 'GET':
        if request.GET.get('ArtistName'):
            artists = getArtistInfo(request.GET.get('ArtistName'), 5)
            #print(artists)
            #print(json.dumps([artist.as_dict() for artist in artists]))
            return HttpResponse(json.dumps([artist.as_dict() for artist in artists]))
        else:
            return HttpResponse('[]')