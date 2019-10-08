#!/usr/bin/env python3

# Program: bookmarkArchiver
# Objective: Organize bookmarks and add music to ia Writer docs
# Author: Ben Tilden

import re
import threading
from datetime import datetime, timezone
import requests
import chrome_bookmarks
from lxml import html
from ChromeBookmarkEditor import Chrome

class ChromeExtension(Chrome):

    def __init__(self, date):
        super().__init__()
        self.temp = self.otherBookmarks.getFolder('temp')
        self.tmtReviews = (self.otherBookmarks
            .getFolder('Personal')
            .getFolder('Culture')
            .getFolder('Journalism')
            .getFolder('Articles to Read')
            .getFolder('TMT Reviews (To Read)'))


def getFolderCheck(locationFolder, title):
    folder = locationFolder.getFolder(title)
    if folder == None:
        locationFolder.addFolder(title)
        folder = locationFolder.getFolder(title)
    return folder

def processPitchforkAlbum(bookmark):
    albumList = []
    titleSearch = (re.search(
        '(.+): (.+) Album Review \| Pitchfork', bookmark.title()))
    artistName = titleSearch.group(1)
    page = requests.get(bookmark.URL())
    tree = html.fromstring(page.content)
    years = tree.xpath(
        '//span[@class="single-album-tombstone__meta-year"]/text()[4]')
    if len(years) > 1:
        albumNames = tree.xpath(
            '//h1[@class="single-album-tombstone__review-title"]/text()')
        if albumNames != None:
            for x in range(0, len(albumNames)):
                albumList.append({
                    "artist": artistName,
                    "title": albumNames[x],
                    "year": years[x],
                    "type": "album"
                })
    else:
        albumName = titleSearch.group(2)
        albumList.append({
            "type": "album",
            "artist": artistName,
            "title": albumName,
            "year": years[0]
        })
    return albumList

def processPitchforkSong(bookmark):
    titleSearch = (re.search(
        '(“.+”( \[.+\])?) by (.+) Review \| Pitchfork', bookmark.title()))
    songName = titleSearch.group(1).replace('“', '').replace('”', '')
    artistName = titleSearch.group(3)
    page = requests.get(bookmark.URL())
    tree = html.fromstring(page.content)
    songElement = {
        "type": "song",
        "artist": artistName,
        "title": songName
    }
    return songElement

def processTMTAlbum(bookmark):
    titleSearch = (re.search(
        '(.+) - (.+) \| Music Review \| Tiny Mix\xa0Tapes', bookmark.title()))
    artistName = titleSearch.group(1)
    albumName = titleSearch.group(2)
    page = requests.get(bookmark.URL())
    tree = html.fromstring(page.content)
    years = tree.xpath(
        '//p[@class="meta"]/text()')
    yearName = re.search('.+; (.+)]', years[0]).group(1)
    albumElement = {
        "type": "album",
        "artist": artistName,
        "title": albumName,
        "year": yearName
    }
    return albumElement

def processPitchfork(bookmark, chrome):
    if "Album Review" in bookmark.title():
        return processPitchforkAlbum(bookmark)
        # chrome.temp.getBookmark(bookmark).delete() #TODO: uncomment all delete
    elif "Review" in bookmark.title():
        return processPitchforkSong(bookmark)
        # chrome.temp.getBookmark(bookmark.title()).delete()
    else:
        discoveryMusic = getFolderCheck(chrome.temp, 'Discovery (Music)')
        discoveryMusic.addBookmark(bookmark.title(), bookmark.URL())
        return None
        # chrome.temp.getBookmark(bookmark.title()).delete()

def processTMT(bookmark, chrome):
    if "Music Review" in bookmark.title():
        chrome.tmtReviews.addBookmark(bookmark.title(), bookmark.URL())
        return processTMTAlbum(bookmark)
        # chrome.temp.getBookmark(bookmark.title()).delete()
    else:
        discoveryMusic = getFolderCheck(chrome.temp, 'Discovery (Music)')
        discoveryMusic.addBookmark(bookmark.title(), bookmark.URL())
        return None
        # chrome.temp.getBookmark(bookmark.title()).delete()

def processYouTube(bookmark, chrome):
    youtubeFolder = getFolderCheck(chrome.temp, 'YouTube') #TODO: look into adding this to ChromeBookmarkEditor
    youtubeFolder.addBookmark(bookmark.title(), bookmark.URL())
    return None
    # chrome.temp.getBookmark(bookmark.title()).delete()

def processBookmarkThread(bookmark, chrome):
    if "Pitchfork" in bookmark.title():
        return processPitchfork(bookmark, chrome)
    elif "Tiny Mix\xa0Tapes" in bookmark.title():
        return processTMT(bookmark, chrome)
    elif "YouTube" in bookmark.title():
        return processYouTube(bookmark, chrome)

def bookmarkArchiver(year):
    elementList = []
    elementNo = 0
    chrome = ChromeExtension(year)
    for bookmark in chrome.temp.bookmarks:
        element = processBookmarkThread(bookmark, chrome)
        if type(element) is list:
            elementList.extend(element)
        elif type(element) is dict:
            elementList.append(element)
        elementNo += 1
        print(elementNo)
        # threads = []
        # thread = threading.Thread(target=processBookmarkThread, args=(bookmark, chrome))
        # thread.daemon = True
        # threads.append(thread)
        # thread.start()
        # for x in threads
        #     x.join()
        # [x.join() for x in threads]
    print(elementList)
    with open('/Users/bentilden/Library/Mobile Documents/'
             '27N4MQEA55~pro~writer/Documents/temp.txt', 'a+') as f:
        for element in elementList:
            f.write('\t'.join(value for key, value in element.items()) + '\n')

if __name__ == "__main__":
    bookmarkArchiver("")
