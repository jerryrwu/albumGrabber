import os
import requests
import json
import mutagen
import urllib.request
from PIL import Image
import PIL
import math
config = open('config.txt')
dict = {
}
fullList = []
def listSong(location, photoURL):
    fullList.append([location,photoURL])
def saveSong(location, photoURL):
    f = open(location, 'wb')
    f.write(requests.get(photoURL).content)
    f.close()
    if not dict["resolution"] == "default":
        img = Image.open(location)
        base = int(dict["resolution"])
        scale = (base/float(img.size[0]))
        size = int((float(img.size[1]) * float(scale)))
        img = img.resize((base, size), PIL.Image.ANTIALIAS)
        img.save(location)


with config as f:
    for line in f:
        pair = line.split(';')
        dict[pair[0]] = pair[1].rstrip('\n')
extensions = dict['extensions'].split(',')

rootDirectory = os.listdir(dict["root"])
albums = []
for root, dirs, files in os.walk(dict["root"]):
    albums.append(root)
            
##for item in rootDirectory:
##    if os.path.isdir(os.path.join(dict["root"],item)):
##        albums.append(os.path.join(dict["root"],item))

for album in albums:
    albumDir = os.listdir(album)
    if "folder.jpg" in albumDir:
        continue
    songs = ""
    for song in albumDir:
        exts = song.split('.')
        ext = exts[len(exts)-1]
        if ext in extensions:
            songs=os.path.join(album,song)
            break
    if songs is "":
        continue
    artist = ""
    albumName = ""
    if songs is not "":
        audiofile = mutagen.File(songs)
        artist = audiofile.tags["TPE1"].text[0]
        albumName = audiofile.tags["TALB"].text[0]
    url = "https://itunes.apple.com/search?term="+albumName + "&entity=album&country=" + dict['location']
    results = requests.get(url).json()['results']
    locationOfFolderJPG = album + "/folder.jpg"



    unfinished = True
    exactMatch = []
    for result in results:
        if albumName.lower() in result['collectionName'].lower() and artist.lower() == result['artistName'].lower():
            exactMatch.append(result)



    if len(exactMatch) == 1:
        thisURL = exactMatch[0]['artworkUrl100']
        thisURL = thisURL.replace("100x100bb","100000x100000-999")
        listSong(locationOfFolderJPG, thisURL)
        unfinished = False


    if unfinished:
        pages = []
        page = []
        for index in range(len(results)):
            page.append(results[index])
            if len(page) is 8:
                pages.append(page)
                page = []
        if len(page) is not 0:
            pages.append(page)
        pageIndex = 0
        while(True):
            print("0 - skip")
            myPage = pages[pageIndex]
            for index in range(len(myPage)):
                print(str(index+1) + " - " + myPage[index]['collectionName'] + " - " + myPage[index]['artistName'] + " - " +  myPage[index]['releaseDate'])                     
            print("n = next page, p = previous page")
            inputs = input("choose one for " + albumName +" - " + artist + ".")
            if inputs is "n":
                if pageIndex is len(pages)-1:
                    continue
                pageIndex+= 1
                continue
            if inputs is "p":
                if pageIndex is not 0:
                    pageIndex-= 1
                    continue
                continue
            if inputs is "0":
                break
            listSong(locationOfFolderJPG,myPage[int(inputs) - 1]['artworkUrl100'].replace("100x100bb","100000x100000-999"))
            break
for lists in fullList:
    saveSong(lists[0],lists[1])
print("done")
log = input("printLog? y/n")
if log is "y":
    print(fullList)
