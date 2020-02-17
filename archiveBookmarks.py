#!/usr/bin/env python3

# Program: archiveBookmarks
# Objective: Organize bookmarks and add music to ia Writer docs
# Author: Ben Tilden

import re
import requests
from lxml import html
from datetime import datetime, timezone
from multiprocessing.pool import ThreadPool
from chromeBookmarkEditor import Chrome

class ChromeExtension(Chrome):
    """Extend Chrome to contain temp, TODO, and tmtReviews"""

    def __init__(self):
        super().__init__()
        self.temp = self.otherBookmarks.getFolderUnsure('temp')
        self.TODO = self.otherBookmarks.getFolderUnsure('TODO')
        self.tmtReviews = (self.otherBookmarks
            .getFolder('Personal')
            .getFolder('Culture')
            .getFolder('Journalism')
            .getFolder('Articles to Read')
            .getFolder('TMT Reviews (To Read)'))


def processPitchforkAlbum(bookmark):
    """Add Pitchfork album info to elementList"""
    albumList = []
    titleSearch = (re.search(
        r'(.+?): (.+) Album Review \| Pitchfork', bookmark.title()))
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
                    "type": "music",
                    "title": albumNames[x],
                    "artist": artistName,
                    "discipline": "album",
                    "year": years[x],
                    "star": "",
                    "listenedThrough": "false"
                })
    else:
        albumName = titleSearch.group(2)
        albumList.append({
            "type": "music",
            "title": albumName,
            "artist": artistName,
            "discipline": "album",
            "year": years[0],
            "star": "",
            "listenedThrough": "false"
        })
    return albumList

def processPitchforkSong(bookmark):
    """Add Pitchfork song info to elementList"""
    titleSearch = (re.search(
        r'(“.+”( \[.+\])?) by (.+) Review \| Pitchfork', bookmark.title()))
    songName = titleSearch.group(1).replace('“', '').replace('”', '')
    artistName = titleSearch.group(3)
    songElement = {
        "type": "music",
        "title": songName,
        "artist": artistName,
        "discipline": "song",
        "year": int(datetime.datetime.now().year)
    }
    return [songElement]

def processTMTAlbum(bookmark):
    """Add TMT album info to elementList"""
    titleSearch = (re.search(
        r'(.+) - (.+) \| Music Review \| Tiny Mix', bookmark.title()))
    artistName = titleSearch.group(1)
    albumName = titleSearch.group(2).replace('\u200b', '')
    page = requests.get(bookmark.URL())
    tree = html.fromstring(page.content)
    years = tree.xpath(
        '//p[@class="meta"]/text()')
    yearName = re.search('.+; (.+)]', years[0]).group(1)
    albumElement = {
        "type": "music",
        "title": albumName,
        "artist": artistName,
        "discipline": "album",
        "year": yearName,
        "star": "",
        "listenedThrough": "false"
    }
    return [albumElement]

def processPitchfork(bookmark, chrome):
    """Allocate Pitchfork bookmark to proper sorting"""
    if "Album Review" in bookmark.title():
        return processPitchforkAlbum(bookmark)
    elif "Review" in bookmark.title():
        return processPitchforkSong(bookmark)
    else:
        discoveryMusic = chrome.temp.getFolderUnsure('Discovery (Music)')
        discoveryMusic.addBookmark(bookmark.title(), bookmark.URL())
        return []

def processTMT(bookmark, chrome):
    """Allocate TMT bookmark to proper sorting"""
    if "Music Review" in bookmark.title():
        if not chrome.tmtReviews.isBookmark(bookmark.title()):
            chrome.tmtReviews.addBookmark(bookmark.title(), bookmark.URL())
        return processTMTAlbum(bookmark)
    else:
        discoveryMusic = chrome.temp.getFolderUnsure('Discovery (Music)')
        discoveryMusic.addBookmark(bookmark.title(), bookmark.URL())
        return []

def processYouTube(bookmark, chrome):
    """Add YouTube bookmark to YouTube folder"""
    youtubeFolder = chrome.temp.getFolderUnsure('YouTube')
    youtubeFolder.addBookmark(bookmark.title(), bookmark.URL())
    return []

def processBookmark(bookmark, chrome):
    """Allocate temp bookmark to proper sorting"""
    if "Pitchfork" in bookmark.title():
        return processPitchfork(bookmark, chrome)
    elif ("Tiny Mix\xa0Tapes" in bookmark.title()
          or "Tiny Mix Tapes" in bookmark.title()):
        return processTMT(bookmark, chrome)
    elif "YouTube" in bookmark.title():
        return processYouTube(bookmark, chrome)
    return None

def addElementToList(bookmark, chrome, elementList):
    """Add element extracted from bookmark to list"""
    element = processBookmark(bookmark, chrome)
    if element != None:
        elementList.extend(element)
    else:
        chrome.TODO.addBookmark(bookmark.title(), bookmark.URL())

def getElementList(chrome):
    """Use threadpool to organize bookmarks and extract data"""
    elementList = []
    pool = ThreadPool()
    for bookmark in chrome.temp.bookmarks:
        pool.apply_async(
            addElementToList, (bookmark, chrome, elementList))
    pool.close()
    pool.join()
    # chrome.temp.delete()
    # chrome.temp is now equal to the folder previously located below it
    # chrome.temp = chrome.otherBookmarks.addFolder('temp')
    return elementList

def archiveBookmarks():
    """Archive bookmarks and write song and album data to temp.txt"""
    chrome = ChromeExtension()
    elementList = getElementList(chrome)
    with open('/Users/bentilden/Library/Mobile Documents/'
             '27N4MQEA55~pro~writer/Documents/temp.txt', 'a+') as f:
        for element in elementList:
            f.write('\t'.join(value for key, value in element.items()) + '\n')

if __name__ == "__main__":
    archiveBookmarks()
