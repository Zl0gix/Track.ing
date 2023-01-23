from django.shortcuts import render

from django.http import HttpResponse
from django.template import loader

from Backend.spotipyRetrieval import getArtistInfo

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
    template = loader.get_template('overview.html')
    context = {
        'title': 'Tracking - Overview',
        #'SpotifyID': request.GET.get('ArtistName'),
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