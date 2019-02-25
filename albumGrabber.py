import os
import requests
import json
import mutagen
import urllib.request
from PIL import Image
import PIL
config = open('config.txt')
dict = {
}
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
#todo make this all subdirectories that contains music
for item in rootDirectory:
    if os.path.isdir(os.path.join(dict["root"],item)):
        albums.append(os.path.join(dict["root"],item))
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
##        if ".flac" in song:
##            songs.append(os.path.join(album,song))
##        if ".mp3" in song:
##            songs.append(os.path.join(album,song))
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
        saveSong(locationOfFolderJPG, thisURL)
        unfinished = False



    if unfinished:
        print("0 - skip")
        for index in range(len(results)):
            print(str(index + 1) + " - " + results[index]['collectionName'] + " - " + results[index]['artistName'] + " - " +  results[index]['releaseDate'])
        inputs = input("No match found for " + albumName +" - " + artist + "." +" Choose one: ")
        #todo tighten edge cases. Maybe have it show 10 at a time(Optional)

        if inputs is not "0":
            saveSong(locationOfFolderJPG,results[int(inputs) - 1]['artworkUrl100'].replace("100x100bb","100000x100000-999"))
