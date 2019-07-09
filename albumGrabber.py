# -*- coding: utf8 -*-
import os
import requests
import json
import time
import mutagen
import urllib.request
from PIL import Image
import PIL
import math
configurationDictionary = {}
errorLogger = []
readyForDownload = []
userSeparated = []
configurationFile = open('config.txt')

#this is for those without any results. Given information like album, artist, year
needManualEntry = []

#list of all directories where an album could exist
albumPaths = []

#this adds the configuration file into dict.
with configurationFile as reader:
    for line in reader:
        pair = line.split(';')
        configurationDictionary[pair[0]] = pair[1].rstrip('\n')

acceptedExtensions = configurationDictionary['extensions'].split(',')
#possible extensions that we want to handle. Examples include flac, mp3 etc. Could include others
#like alac, mp4, wav

#for every single directory inside the root directory from the configuration file
#adds them into albums
#although some directories are not albums, it is fine
#it will be handled later, where only directories with songs inside are considered album folders
for root, dirs, files in os.walk(configurationDictionary["root"]):
    albumPaths.append(root)


#takes in a url to make a request
#returns a list[requests.get object, boolean success code]
#-1 means not successful
#does 6 tries before giving up
def makeRequest(url):
    maxTries = 6
    numTries = 0
    print("trying: " + url)
    while True:
        response = requests.get(url)
        if response.status_code is not 200:
            numTries += 1
            ## linear backoff
            ## there is a three second initial delay per request
            ## from there, it retries after 2, 4, 6, 8, 10, 12 seconds
            ## itunes api is rated for 20/min, or once every three seconds
            time.sleep(numTries * 3)
            if numTries > maxTries:
                errorLogger.append(["api error", url])
                return [response, '-1']
            print("retrying: " + url)
            continue
        return [response, '0']


#adds a song to a fullList. It includes the location of where to save a song,
#as well as the url of the picture
def stageSongForDownload(location, photoURL):
    readyForDownload.append([location, photoURL])


#given the location of where to save a photo
#and the url of the photo
#saves the photo from the url at the directory of location
def downloadArtToPath(path, photoURL):
    f = open(path, 'wb')
    f.write(requests.get(photoURL).content)
    f.close()
    if not configurationDictionary["resolution"] == "default":
        img = Image.open(path)
        base = int(configurationDictionary["resolution"])
        scale = (base / float(img.size[0]))
        size = int((float(img.size[1]) * float(scale)))
        img = img.resize((base, size), PIL.Image.ANTIALIAS)
        img.save(path)


#takes in a list [json request object, album. artst, directory] and allows a user to choose which one they want
#User chooses which search result they want and we return it.
#if none, return None
def userSelection(arguments):
    requestResult = arguments[0]
    albumName = arguments[1]
    artist = arguments[2]
    locationOfFolderJPG = arguments[3]
    pages = []
    page = []
    #separates it into pages with at most 8 results each
    for index in range(len(requestResult)):
        page.append(requestResult[index])
        if len(page) is 8:
            pages.append(page)
            page = []
    #in case the last page is not a full page, it wont be appended to pages, so we must do it here
    if len(page) is not 0:
        pages.append(page)
    pageIndex = 0
    while (True):
        print("0 - skip")
        myPage = pages[pageIndex]
        for index in range(len(myPage)):
            print(
                str(index + 1) + " - " + myPage[index]['collectionName'] +
                " - " + myPage[index]['artistName'] + " - " +
                myPage[index]['releaseDate'])
        print(
            "n = next page, p = previous page, m = skip. add to manual search list"
        )
        inputs = input("choose one for " + albumName + " - " + artist + ".")
        if inputs is "n":
            if pageIndex is len(pages) - 1:
                continue
            pageIndex += 1
            continue
        if inputs is "p":
            if pageIndex is not 0:
                pageIndex -= 1
                continue
            continue
        if inputs is "m":
            needManualEntry.append([artist, albumName, locationOfFolderJPG])
            break
        if inputs is "0":
            break
        try:
            stageSongForDownload(
                locationOfFolderJPG,
                myPage[int(inputs) - 1]['artworkUrl100'].replace(
                    "100x100bb", "100000x100000-999"))
        except:
            continue
        break


#returns all the exact matches of a result
def exactMatches(requestResult, albumName, artist):
    exactMatch = []
    for result in requestResult:
        if albumName.lower() in result['collectionName'].lower(
        ) and artist.lower() == result['artistName'].lower():
            exactMatch.append(result)
    return exactMatch


def manualQuery(artist, albumName, locationOfFolderJPG):
    print(artist + " - " + albumName)
    query = input("search term: ")
    url = "https://itunes.apple.com/search?term=" + query + "&entity=album"
    myRequest = makeRequest(url)
    results = None
    if myRequest[1] is '-1':
        #if here, non-200 error code. API did not work as intended
        print("network error. Potentially a cooldown for the api.")
        retry = input("retry? (y/n)")
        if retry == "y":
            return manualQuery(artist, albumName, locationOfFolderJPG)
        else:
            return None
    try:
        results = myRequest[0].json()['results']
        if len(results) is 0:
            proceed = input("no results. retry? (y/n)")
            if proceed is "y":
                return manualQuery(artist, albumName, locationOfFolderJPG)
    except:
        print("error reading request")
        errorLogger.append(["error making request a json", album])
        return None
    return results


#takes in directory and returns path of a song
#if there is no songs or art is already there, return -1
#^in addition, logs this
def getPathOfSong(directory):
    directoryContents = os.listdir(directory)
    #skips any folders with art
    if "folder.jpg" in directoryContents:
        return ""
    for item in directoryContents:
        if item.split('.')[-1] in acceptedExtensions:
            return os.path.join(directory, item)
    errorLogger.append(['no songs in ', directory])
    return ""


#returns metadata from the path of a song
#[artist, albumName]
def getMetadata(songPath):
    ##TODO possibly handle exception if file at songpath does not have metadata and mutagen throws
    metadata = mutagen.File(songPath.replace(os.sep, '/'))
    ##TODO possibly have tag keys in configuration file. This may make it more modular
    possibleTagKeys = [["TPE1", "TALB"], ["ALBUMARTIST", "ALBUM"],
                       ["artist", "album"]]
    for key in possibleTagKeys:
        if key[0] not in metadata.tags or key[1] not in metadata.tags:
            continue
        return [metadata.tags[key[0]].text[0], metadata.tags[key[1]].text[0]]
    ##if reaches here, tags unreadable
    errorLogger.append(["tags unreadable/not found at ", songPath])
    return [None, None]


#This looks through each of the directories inside albums
#if there are songs in it's immediate directory, it will be considered an album directory
for album in albumPaths:
    #sleep prevents api overuse. 20 calls a minute limit
    time.sleep(1)
    songPath = getPathOfSong(album)
    if songPath is "":
        continue
    artist, albumName = getMetadata(songPath)
    if artist is None:
        continue
    url = "https://itunes.apple.com/search?term=" + albumName + "&entity=album"
    myRequest = makeRequest(url)
    if myRequest[1] is '-1':
        #-1 means we did not get a 200 error code. this means we were unable to make the api request
        errorLogger.append(["bad request", album])
        continue
    try:
        results = myRequest[0].json()['results']
        locationOfFolderJPG = album + "/folder.jpg"
        if len(results) is 0:
            errorLogger.append(["no results", album])
            needManualEntry.append([artist, albumName, locationOfFolderJPG])
            continue
    except:
        errorLogger.append(["error making request a json", album])
        continue
    exactMatch = exactMatches(results, albumName, artist)
    # If there are only one exact match, no user input is required. It will automatically assume it is correct
    if len(exactMatch) == 1:
        thisURL = exactMatch[0]['artworkUrl100']
        #replaces the low resolution picture url to the high resolution version(highest)
        thisURL = thisURL.replace("100x100bb", "100000x100000-999")
        stageSongForDownload(locationOfFolderJPG, thisURL)
        print("success")
        continue
    # if it gets to this point, it means there are multiple possible matches
    # Appends into a list that will later be user-inputted
    userSeparated.append([results, albumName, artist, locationOfFolderJPG])
    print("success")

#for every single result where there are more than one match in a search, the user will need to
#select which search result they want
for result in userSeparated:
    userSelection(result)

while len(needManualEntry) >= 1:
    badResult = needManualEntry.pop()
    artist = badResult[0]
    albumName = badResult[1]
    locationOfFolderJPG = badResult[2]
    results = manualQuery(artist, albumName, locationOfFolderJPG)
    if results is None:
        continue
    exactMatch = exactMatches(results, albumName, artist)
    # If there are only one exact match, no user input is required. It will automatically assume it is correct
    if len(exactMatch) == 1:
        thisURL = exactMatch[0]['artworkUrl100']
        #replaces the low resolution picture url to the high resolution version(highest)
        thisURL = thisURL.replace("100x100bb", "100000x100000-999")
        stageSongForDownload(locationOfFolderJPG, thisURL)
        print("success")
        continue
# if it gets to this point, it means there are multiple possible matches
    userSelection([results, albumName, artist, locationOfFolderJPG])

#begins saving songs to the directory
for album in readyForDownload:
    downloadArtToPath(album[0], album[1])

print("saved everything")
#prints out every request
log = input("printLog? y/n")
if log is "y":
    print(readyForDownload)

#writes everything that was logged to errorLogger to an error text file
errorlog = open("errorlog.txt", "w")
for line in errorLogger:
    try:
        errorlog.write(line[0] + " " + line[1] + "\n")
    except:
        pass
errorlog.close()
input("done")
