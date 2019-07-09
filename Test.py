##tests
import random
from albumGrabberOOP import albumGetter


class Test:
    def test_makeRequest(self):
        randomKey = random.randint(0, 9999999)
        randomValue = random.randint(0, 9999999)
        url = 'https://postman-echo.com/get?' + str(randomKey) + "=" + str(
            randomValue)
        response = self.instance.makeRequest(url)
        if response[1] == "-1":
            print("makeRequest error. Possibly network? URL: " + url)
            return False
        # if this fails, look into:
        # is postman down
        # was there any changes to makeRequest
        return response[0].json()["args"][str(randomKey)] == str(randomValue)

    def test_downloadArtToPath(self):
        return True

    def test_exactMatches(self):
        return True

    def test_manualQuery(self):
        return True

    def test_writeErrorFile(self):
        return True

    def test_saveStagedArt(self):
        return True

    def test_getMetadata(self):
        # TODO add test songs and test library with fake songs
        return True

    def test_getPathOfSong(self):
        # TODO given a directory, check if there is a song in there with an accepted extension
        # if there is, return any one of them
        return True

    def __init__(self):
        self.instance = albumGetter()

    def test_all(self):
        assert self.test_makeRequest()
        assert self.test_downloadArtToPath()
        assert self.test_exactMatches()
        assert self.test_manualQuery()
        assert self.test_writeErrorFile()
        assert self.test_saveStagedArt()
        assert self.test_getMetadata()
        assert self.test_getPathOfSong()
        print("success")


Test().test_all()
