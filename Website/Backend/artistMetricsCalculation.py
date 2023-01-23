import pandas as pd
import numpy as np

def GetMetrics(artist_URI, artist_name, artist_followers):

    dfBillboard = pd.read_csv('Data/billboard_global_200.csv')
    billboardUniqueArtist = dfBillboard[dfBillboard['Artist'] == artist_name]
    dfStudioSales = pd.read_csv('Data/top150ArtistsStudioSales.csv')
    studioUniqueArtist = dfStudioSales[dfStudioSales['Name'] == artist_name]

    albumsDf = pd.read_csv('Data/albumsTOP12artists.csv')
    tracksDf = None
    albumsUniqueArtist = None
    tracksUniqueArtist = None
    if (artist_URI in albumsDf['artist_uri'].unique()):
        albumsUniqueArtist = albumsDf[albumsDf['artist_uri'] == artist_URI]
        tracksUniqueArtist = tracksDf[tracksDf['artist_uri'] == artist_URI]
    else:
        # Dynamic Data needs to have been generated before
        albumsUniqueArtist = pd.read_csv('Backend/DynamicData/artist_albums.csv')
        tracksUniqueArtist = pd.read_csv('Backend/DynamicData/artist_uniqueTracks.csv')
    
    # Conversion to datetime64 for data analysis
    albumsUniqueArtist["release_date"] = pd.to_datetime(albumsUniqueArtist["release_date"])
    tracksUniqueArtist["release_date"] = pd.to_datetime(tracksUniqueArtist["release_date"])

    #############################
    ## Consistency
    #############################

    yearlyAlbumsActivity = pd.DataFrame(albumsUniqueArtist.groupby(albumsUniqueArtist.release_date.dt.year)['artist_uri'].count())
    yearlyAlbumsActivity = yearlyAlbumsActivity.rename(columns={'artist_uri' : 'nbTracks'})

    print(f"Variance for albums/EPs/Singles creation : {yearlyAlbumsActivity.var()[0]}")

    yearlyTracksActivity = pd.DataFrame(tracksUniqueArtist.groupby(tracksUniqueArtist.release_date.dt.year)['artist_uri'].count())
    yearlyTracksActivity = yearlyTracksActivity.rename(columns={'artist_uri' : 'nbTracks'})

    print(f"Variance for tracks creation : {yearlyTracksActivity.var()[0]}")
    print(f"Maximum for tracks creation : {yearlyTracksActivity.max()[0]}")


    creatingYears = list(yearlyTracksActivity.index)
    minYear = min(creatingYears)
    maxYear = max(creatingYears)
    overviewYears = [year in creatingYears for year in range(minYear, maxYear + 1)]

    print(f'Empty years track wise : {len(overviewYears) - len(creatingYears)}/{len(overviewYears)}')

    noActivityStreaks = []
    currentStreak = 0
    for year in overviewYears:
        if (year == False):
            currentStreak += 1
        else:
            if (currentStreak != 0):
                noActivityStreaks.append(currentStreak)
            currentStreak = 0
    # We don't need to add current streak one last time because last year is necessarily active

    print(f'Empty years track wise as streaks : {noActivityStreaks}')

    ################### 
    ## Calculation

    consistency = 1
    # -= empty years / total years
    consistency -= (len(overviewYears) - len(creatingYears))/len(overviewYears)
    print(f'\n{consistency}')
    # -= max empty years in a row / total years
    consistency -= max(noActivityStreaks) / len(overviewYears)
    print(consistency)
    # -= albums/EPs/singles variance / 2 / 100
    consistency -= yearlyAlbumsActivity.var()[0] / 2 / 100
    print(consistency)
    # -= tracks variance / max tracks / 100
    consistency -= yearlyTracksActivity.var()[0] / yearlyTracksActivity.max()[0] / 100
    print(consistency)

    # Anti-negative or too low condition 
    if consistency < len(creatingYears) / 100:
        consistency = len(creatingYears) / 100

    print(f'\nConsistency score : {consistency}')

    #####################
    ## Hard Working
    #####################

    print(f"Number of tracks created : {len(tracksUniqueArtist)}")

    yearlyOnlyAlbumsActivity = pd.DataFrame(albumsUniqueArtist[albumsUniqueArtist['total_tracks'] > 7].groupby(albumsUniqueArtist.release_date.dt.year)['artist_uri'].count())
    yearlyOnlyAlbumsActivity = yearlyOnlyAlbumsActivity.rename(columns={'artist_uri' : 'nbAlbums'})

    print(f"Number of albums throughout the career : {yearlyOnlyAlbumsActivity.sum()[0]}")

    yearlyOnlyEPsActivity = pd.DataFrame(albumsUniqueArtist[(albumsUniqueArtist['total_tracks'] <= 7) & (albumsUniqueArtist['total_tracks'] > 1)].groupby(albumsUniqueArtist.release_date.dt.year)['artist_uri'].count())
    yearlyOnlyEPsActivity = yearlyOnlyEPsActivity.rename(columns={'artist_uri' : 'nbEPs'})

    print(f"Number of EPs throughout the career : {yearlyOnlyEPsActivity.sum()[0]}")

    print(f'Number of career years : {len(overviewYears)}\n')

    ################### 
    ## Calculation

    # = total tracks / career years * 5 / 100
    hardWorking = len(tracksUniqueArtist) / len(overviewYears) * 5 / 100
    print(hardWorking)
    # += albums
    hardWorking += yearlyOnlyAlbumsActivity.sum()[0] / 100
    print(hardWorking)
    # += EPs / 3
    hardWorking += yearlyOnlyEPsActivity.sum()[0] / 3 / 100
    print(hardWorking)

    if (hardWorking > 1):
        hardWorking = 1

    print(f'\nHard Working score : {hardWorking}')

    #####################
    ## Original
    #####################

    print(f'Number of tracks created : {len(tracksUniqueArtist)}')
    print(f'Number of tracks referenced by whosampled.com : {len(tracksUniqueArtist) - tracksUniqueArtist.isnull().any(axis=1).sum()}')

    dfSamplingRefs = tracksUniqueArtist.dropna()
    print(f'Total number of samples used :', dfSamplingRefs['nbSamples'].sum())
    print(f'Number of songs using samples :', dfSamplingRefs[dfSamplingRefs['nbSamples'] > 0].count()[0])

    ################### 
    ## Calculation

    originality = 1
    # -= songs referenced using a sample / songs referenced
    originality -= dfSamplingRefs[dfSamplingRefs['nbSamples'] > 0].count()[0] / (len(tracksUniqueArtist) - tracksUniqueArtist.isnull().any(axis=1).sum())
    print(f'\nOriginality score : {originality}')

    #####################
    ## Inspirational
    #####################

    print(f'Number of tracks created : {len(tracksUniqueArtist)}')
    print(f'Number of tracks referenced by whosampled.com : {len(tracksUniqueArtist) - tracksUniqueArtist.isnull().any(axis=1).sum()}')

    print(f'Total number of {artist_name}\'s tracks sampled :', dfSamplingRefs['nbSampled'].sum())
    print(f'Total number of {artist_name}\'s tracks remixed :', dfSamplingRefs['nbRemixes'].sum())

    ################### 
    ## Calculation

    inspiration = 0
    # += sampled * 5 / 100
    inspiration += dfSamplingRefs['nbSampled'].sum() * 5 / (len(tracksUniqueArtist) - tracksUniqueArtist.isnull().any(axis=1).sum())
    print(inspiration)
    # += remixed / 3 / 100
    inspiration += dfSamplingRefs['nbRemixes'].sum() / 3 / (len(tracksUniqueArtist) - tracksUniqueArtist.isnull().any(axis=1).sum())
    print(inspiration)
    # += sampled / 100
    inspiration += dfSamplingRefs['nbSampled'].sum() / 100

    if (inspiration > 1):
        inspiration = 1

    print(f'\nInspirational score : {inspiration}')

    #####################
    ## G.O.A.T
    #####################

    if (len(studioUniqueArtist) > 0):
        print(f'Global studio sales rank within top 150 : n°{studioUniqueArtist.iloc[0]["Rank"]}')
        print(f'Global studio sales : {studioUniqueArtist.iloc[0]["StudioSales"]} albums')
    else:
        print(f'Global studio sales rank within top 150 : Unknown')
        print(f'Global studio sales : No information')

    musicPeaks = {}
    if (len(billboardUniqueArtist) > 0):
        print(f'Number of weeks within the billboard top 200 : {len(billboardUniqueArtist["Date"].unique())}')

        for song in billboardUniqueArtist['Song'].unique():
            musicPeaks[song] = billboardUniqueArtist[billboardUniqueArtist['Song'] == song].min()['Peak']
    else:
        print(f'Number of weeks within the billboard top 200 : None')
    print(musicPeaks)

    print(f'Number of followers : {artist_followers}')

    ################### 
    ## Calculation

    GOAT = 0
    if (len(studioUniqueArtist) > 0):
        billboardP = (151 - studioUniqueArtist.iloc[0]["Rank"]) / 150
        GOAT = 0.7 + billboardP * 0.3
    else:
        GOAT = artist_followers / 10000000
        if (GOAT > 0.55):
            GOAT = 0.55
        if (len(billboardUniqueArtist) > 0):
            GOAT += len(billboardUniqueArtist["Date"].unique()) / 50 / 10
            if (GOAT > 0.65):
                GOAT = 0.65
            if (min(list(musicPeaks.values()))) == 1:
                GOAT += 0.05

    print(f'\nGOAT score : {GOAT}')

    stats = {}
    stats['Consistency'] = consistency
    stats['Hard Working'] = hardWorking
    stats['Original'] = originality
    stats['Inspirational'] = inspiration
    stats['G.O.A.T'] = GOAT

    return stats

