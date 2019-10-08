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

def parseBookmarkList(date):
    youtubeUrls = {}
    bookmarksSinceDate = {}
    givenDate = datetime(2019, 5, 15) #TODO: Hardcoded
    for url in chrome_bookmarks.urls:
        if "YouTube" in url.name:
            youtubeUrls[url.name] = url.url
        if (url.added > givenDate.replace(tzinfo=timezone.utc) and 
           ("Pitchfork" in url.name or "Tiny Mix\xa0Tapes" in url.name)):
            bookmarksSinceDate[url.name] = url.url
    return youtubeUrls, bookmarksSinceDate

def getFolderCheck(locationFolder, title):
    folder = locationFolder.getFolder(title)
    if folder == None:
        locationFolder.addFolder(title)
        folder = locationFolder.getFolder(title)
    return folder

def processPitchforkAlbum(bookmarkTitle, bookmarksSinceDate):
    albumList = []
    titleSearch = (re.search(
        '(.+): (.+) Album Review \| Pitchfork', bookmarkTitle))
    artistName = titleSearch.group(1)
    page = requests.get(bookmarksSinceDate[bookmarkTitle])
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

def processPitchforkSong(bookmarkTitle, bookmarksSinceDate):
    titleSearch = (re.search(
        '(“.+”( \[.+\])?) by (.+) Review \| Pitchfork', bookmarkTitle))
    songName = titleSearch.group(1).replace('“', '').replace('”', '')
    artistName = titleSearch.group(3)
    page = requests.get(bookmarksSinceDate[bookmarkTitle])
    tree = html.fromstring(page.content)
    songElement = {
        "type": "song",
        "artist": artistName,
        "title": songName
    }
    return songElement

def processTMTAlbum(bookmarkTitle, bookmarksSinceDate):
    titleSearch = (re.search(
        '(.+) - (.+) \| Music Review \| Tiny Mix\xa0Tapes', bookmarkTitle))
    artistName = titleSearch.group(1)
    albumName = titleSearch.group(2)
    page = requests.get(bookmarksSinceDate[bookmarkTitle])
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

def processPitchfork(bookmarkTitle, bookmarksSinceDate, temp):
    if "Album Review" in bookmarkTitle:
            return processPitchforkAlbum(bookmarkTitle, bookmarksSinceDate)
        # temp.getBookmark(bookmarkTitle).delete() #TODO: uncomment all delete
    elif "Review" in bookmarkTitle:
            return processPitchforkSong(bookmarkTitle, bookmarksSinceDate)
        # temp.getBookmark(bookmarkTitle).delete()
    else:
        discoveryMusic = getFolderCheck(temp, 'Discovery (Music)')
        discoveryMusic.addBookmark(
            bookmarkTitle, bookmarksSinceDate[bookmarkTitle])
        # temp.getBookmark(bookmarkTitle).delete()

def processTMT(bookmarkTitle, bookmarksSinceDate, tmtReviews, temp):
    if "Music Review" in bookmarkTitle:
        tmtReviews.addBookmark(
            bookmarkTitle, bookmarksSinceDate[bookmarkTitle])
        return processTMTAlbum(bookmarkTitle, bookmarksSinceDate)
        # temp.getBookmark(bookmarkTitle).delete()
    else:
        discoveryMusic = getFolderCheck(temp, 'Discovery (Music)')
        discoveryMusic.addBookmark(
            bookmarkTitle, bookmarksSinceDate[bookmarkTitle])
        # temp.getBookmark(bookmarkTitle).delete()

def processYouTube(bookmarkTitle, youtubeUrls, temp):
    youtubeFolder = getFolderCheck(temp, 'YouTube') #TODO: look into adding this to ChromeBookmarkEditor
    youtubeFolder.addBookmark(bookmarkTitle, youtubeUrls[bookmarkTitle])
    # temp.getBookmark(bookmarkTitle).delete()

def processBookmarkThread(bookmarkTitle, bookmarksSinceDate, youtubeUrls, temp, tmtReviews):
    if "Pitchfork" in bookmarkTitle:
        return processPitchfork(bookmarkTitle, bookmarksSinceDate, temp)
    elif "Tiny Mix\xa0Tapes" in bookmarkTitle:
        return processTMT(bookmarkTitle, bookmarksSinceDate, tmtReviews, temp)
    elif "YouTube" in bookmarkTitle:
        processYouTube(bookmarkTitle, youtubeUrls, temp)

def bookmarkArchiver(year):
    elementList = []
    elementNo = 0
    youtubeUrls, bookmarksSinceDate = parseBookmarkList(year)
    chrome = Chrome()
    temp = chrome.otherBookmarks.getFolder('temp')
    tmtReviews = (chrome.otherBookmarks
            .getFolder('Personal')
            .getFolder('Culture')
            .getFolder('Journalism')
            .getFolder('Articles to Read')
            .getFolder('TMT Reviews (To Read)'))
    for bookmark in temp.bookmarks:
        element = processBookmarkThread(bookmark.title(), bookmarksSinceDate, youtubeUrls, temp, tmtReviews) #TODO: Look into OOP and minimizing the parameters here
        if type(element) is list:
            elementList.extend(element)
        elif type(element) is dict:
            elementList.append(element)
        elementNo += 1
        print(elementNo)
        # threads = []
        # thread = threading.Thread(target=processBookmarkThread, args=(bookmark, bookmarksSinceDate, youtubeUrls))
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
