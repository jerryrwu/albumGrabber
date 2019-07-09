import os
import requests
import json
import time
import mutagen
import urllib.request
from PIL import Image
import PIL
import math


class albumGetter:
    def __init__(self):
        self.configurationDictionary = {}
        self.errorLogger = []
        self.readyForDownload = []
        self.needManualEntry = []
        self.pathOfAlbums = []
        self.needManualSelection = []
        with open("config.txt") as reader:
            for line in reader:
                pair = line.split(";")
                self.configurationDictionary[pair[0]] = pair[1].rstrip("\n")
        self.acceptedExtensions = self.configurationDictionary[
            "extensions"].split(",")
        self.rootDirectory = self.configurationDictionary["root"]
        for root, _, _ in os.walk(self.rootDirectory):
            self.pathOfAlbums.append(root)

    def makeRequest(self, url):
        maxTries = 6
        numTries = 0
        print("trying: " + url)
        while True:
            response = requests.get(url)
            if 200 != response.status_code:
                numTries += 1
                time.sleep(numTries * 3)
                if maxTries < numTries:
                    self.errorLogger.append(["api error: ", url])
                    return [response, "-1"]
                print("retrying: " + url)
                continue
            return [response, '0']

    def stageSongForDownload(self, location, photoURL):
        self.readyForDownload.append([location, photoURL])

    def downloadArtToPath(self, path, photoURL):
        photo = open(path, "wb")
        photo.write(requests.get(photoURL).content)
        photo.close()
        if "default" != self.configurationDictionary["resolution"]:
            ##TODO look over this conditional for refactoring
            img = Image.open(path)
            base = int(self.configurationDictionary["resolution"])
            scale = (base / float(img.size[0]))
            size = int((float(img.size[1]) * float(scale)))
            img = img.resize((base, size), PIL.Image.ANTIALIAS)
            img.save(path)

    def userSelection(self, arguments):
        requestResult = arguments[0]
        albumName = arguments[1]
        artist = arguments[2]
        locationOfFolderJPG = arguments[3]
        pages = []
        page = []
        pageIndex = 0
        for index in range(len(requestResult)):
            page.append(requestResult[index])
            if len(page) is 8:
                pages.append(page)
                page = []
        if 0 != len(page):
            pages.append(page)
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
            inputs = input("choose one for " + albumName + " - " + artist +
                           ".")
            if "n" == inputs:
                if pageIndex is len(pages) - 1:
                    continue
                pageIndex += 1
                continue
            if "p" == inputs:
                if pageIndex is not 0:
                    pageIndex -= 1
                    continue
                continue
            if "m" == inputs:
                self.needManualEntry.append(
                    [artist, albumName, locationOfFolderJPG])
                break
            if "0" == inputs:
                break
            try:
                self.stageSongForDownload(
                    locationOfFolderJPG,
                    myPage[int(inputs) - 1]['artworkUrl100'].replace(
                        "100x100bb", "100000x100000-999"))
            except:
                print("input error. Are you sure you entered a valid input?")
                continue
            break

    def findExactMatches(self, requestResults, albumName, artist):
        exactMatch = []
        for result in requestResults:
            if albumName.lower() in result['collectionName'].lower(
            ) and artist.lower() == result['artistName'].lower():
                exactMatch.append(result)
        return exactMatch

    def manualQuery(self, artist, albumName, locationOfFolderJPG):
        print(artist + " - " + albumName)
        query = input("search term: ")
        url = "https://itunes.apple.com/search?term=" + query + "&entity=album"
        myRequest = self.makeRequest(url)
        results = None
        if '-1' == myRequest[1]:
            #if here, non-200 error code. API did not work as intended
            print("network error. Potentially a cooldown for the api.")
            retry = input("retry? (y/n)")
            if "y" == retry:
                return self.manualQuery(artist, albumName, locationOfFolderJPG)
            else:
                return None
        try:
            results = myRequest[0].json()['results']
            if 0 == len(results):
                proceed = input("no results. retry? (y/n)")
                if "y" == proceed:
                    return self.manualQuery(artist, albumName,
                                            locationOfFolderJPG)
        except:
            print("error reading request")
            self.errorLogger.append(
                ["error making request a json", locationOfFolderJPG])
            return None
        return results

    def getPathOfAnySong(self, directory):
        directoryContents = os.listdir(directory)
        if "folder.jpg" in directoryContents:
            return ""
        for fileName in directoryContents:
            if fileName.split(".")[-1] in self.acceptedExtensions:
                return os.path.join(directory, fileName)
        self.errorLogger.append(["no songs in ", directory])
        return ""

    def getMetadata(self, songPath):
        ##TODO possibly handle exception if file at songpath does not have metadata and mutagen throws
        metadata = mutagen.File(songPath.replace(os.sep, '/'))
        ##TODO possibly have tag keys in configuration file. This may make it more modular
        possibleTagKeys = [["TPE1", "TALB"], ["ALBUMARTIST", "ALBUM"],
                           ["artist", "album"]]
        for key in possibleTagKeys:
            if key[0] not in metadata.tags or key[1] not in metadata.tags:
                continue
            return [
                metadata.tags[key[0]].text[0], metadata.tags[key[1]].text[0]
            ]
        ##if reaches here, tags unreadable
        self.errorLogger.append(["tags unreadable/not found at ", songPath])
        return [None, None]

    def saveStagedArt(self):
        for album in self.readyForDownload:
            self.downloadArtToPath(album[0], album[1])

    def writeErrorFile(self):
        errorLog = open("errorlog.txt", "w")
        for line in self.errorLogger:
            ##TODO sometimes it has some encoding issues, which is why we use a try block.
            try:
                errorlog.write(line[0] + " " + line[1] + "\n")
            except:
                pass
        errorLog.close()

    def patchURLHighResolution(self, url):
        return url.replace("100x100bb", "100000x100000-999")

    def processManualEntry(self):
        while len(self.needManualEntry) >= 1:
            badResult = self.needManualEntry.pop()
            artist = badResult[0]
            albumName = badResult[1]
            locationOfFolderJPG = badResult[2]
            results = self.manualQuery(artist, albumName, locationOfFolderJPG)
            if results is None:
                continue
            exactMatch = self.findExactMatches(results, albumName, artist)
            if len(exactMatch) == 1:
                thisURL = exactMatch[0]['artworkUrl100']  #finds the url
                thisURL = self.patchURLHighResolution(thisURL)
                self.stageSongForDownload(locationOfFolderJPG, thisURL)
                print("success")
                continue
            else:
                self.userSelection(
                    [results, albumName, artist, locationOfFolderJPG])

    def start(self):
        for directory in self.pathOfAlbums:
            #sleep prevents api overuse. 20 calls a minute limit
            time.sleep(1)
            songPath = self.getPathOfAnySong(directory)
            if songPath is "":
                continue
            artist, albumName = self.getMetadata(songPath)
            if artist is None:
                continue
            url = "https://itunes.apple.com/search?term=" + albumName + "&entity=album"
            myRequest = self.makeRequest(url)
            if myRequest[1] is '-1':
                #-1 means we did not get a 200 error code. this means we were unable to make the api request
                self.errorLogger.append(["bad request", directory])
                continue
            try:
                results = myRequest[0].json()['results']
                folderJPGPath = directory + "/folder.jpg"
                if len(results) is 0:
                    self.errorLogger.append(["no results", directory])
                    self.needManualEntry.append(
                        [artist, albumName, folderJPGPath])
                    continue
            except:
                self.errorLogger.append(
                    ["error making request a json", directory])
                continue
            exactMatch = self.findExactMatches(results, albumName, artist)
            if len(exactMatch) == 1:
                thisURL = exactMatch[0]['artworkUrl100']
                thisURL = self.patchURLHighResolution(thisURL)
                self.stageSongForDownload(folderJPGPath, thisURL)
                print("finished current album")
            else:
                self.needManualSelection.append(
                    [results, albumName, artist, folderJPGPath])
                print("finished current album")
        for result in self.needManualSelection:
            self.userSelection(result)
        self.processManualEntry()
        self.saveStagedArt()
        self.writeErrorFile()
        input("done")


instance = albumGetter()
instance.start()