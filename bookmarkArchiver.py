#!/usr/bin/env python3

# Program: bookmarkArchiver
# Objective: Organize bookmarks and add music to ia Writer docs
# Author: Ben Tilden

import re
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

def processAlbumsPitchfork(bookmarkTitle, bookmarksSinceDate):
    albumList = []
    titleSearch = (re.search('(.+): (.+) Album Review \| Pitchfork',
                   bookmarkTitle))
    artistName = titleSearch.group(1)
    page = requests.get(bookmarksSinceDate[bookmarkTitle])
    tree = html.fromstring(page.content)
    years = tree.xpath(
                '//span'
                '[@class="single-album-tombstone__meta-year"]'
                '/text()[4]') #TODO: Better formatting
    if len(years) > 1:
        albumNames = tree.xpath(
                    '//h1'
                    '[@class='
                    '"single-album-tombstone__review-title"]'
                    '/text()')
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

def processSongsPitchfork(bookmarkTitle, bookmarksSinceDate):
    titleSearch = (re.search('(“.+”( \[.+\])?) by (.+) Review \| Pitchfork',
                   bookmarkTitle))
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

def processAlbumsTMT(bookmarkTitle, bookmarksSinceDate):
    titleSearch = (re.search('(.+) - (.+) \| Music Review \| Tiny Mix\xa0Tapes',
                   bookmarkTitle))
    artistName = titleSearch.group(1)
    albumName = titleSearch.group(2)
    page = requests.get(bookmarksSinceDate[bookmarkTitle])
    tree = html.fromstring(page.content)
    years = tree.xpath(
                '//p'
                '[@class="meta"]'
                '/text()') #TODO: Better formatting
    albumElement = {
        "type": "album",
        "artist": artistName,
        "title": albumName,
        "year": re.search('.+; (.+)]', years[0]).group(1)
    }
    return albumElement

def bookmarkArchiver(year):
    elementCount = 0
    elementList = []
    youtubeUrls, bookmarksSinceDate = parseBookmarkList(year)
    f = open('/Users/bentilden/Library/Mobile Documents/'
             '27N4MQEA55~pro~writer/Documents/temp.txt', 'a+')
    chrome = Chrome()
    temp = chrome.otherBookmarks.getFolder('temp')
    youtube = temp.getFolder('YouTube')
    if youtube == None:
        temp.addFolder('YouTube')
        youtube = temp.getFolder('YouTube')
    for bookmark in temp.bookmarks:
        if "Pitchfork" in bookmark.title():
            if "Album Review" in bookmark.title():
                elementList.extend(processAlbumsPitchfork(bookmark.title(),
                                                          bookmarksSinceDate))
                elementCount += 1
                print(elementCount)
                # temp.getBookmark(bookmark.title()).delete()
            elif "Review" in bookmark.title():
                elementList.append(processSongsPitchfork(bookmark.title(),
                                                         bookmarksSinceDate))
                elementCount += 1
                print(elementCount)
                # temp.getBookmark(bookmark.title()).delete()
            else:
                discoveryMusic = temp.getFolder('Discovery (Music)')
                if discoveryMusic == None:
                    temp.addFolder('Discovery (Music)')
                    discoveryMusic = temp.getFolder('Discovery (Music)')
                discoveryMusic.addBookmark(bookmark.title(), 
                                bookmarksSinceDate[bookmark.title()])
                elementCount += 1
                print(elementCount)
                # temp.getBookmark(bookmark.title()).delete()
        elif "Tiny Mix\xa0Tapes" in bookmark.title():
            if "Music Review" in bookmark.title():
                elementList.append(processAlbumsTMT(bookmark.title(),
                                                    bookmarksSinceDate))
                elementCount += 1
                print(elementCount)
                tmtReviews = (chrome.otherBookmarks
                                            .getFolder('Personal')
                                            .getFolder('Culture')
                                            .getFolder('Journalism')
                                            .getFolder('Articles to Read')
                                            .getFolder('TMT Reviews (To Read)'))
                tmtReviews.addBookmark(bookmark.title(),
                                bookmarksSinceDate[bookmark.title()])
                # temp.getBookmark(bookmark.title()).delete()
            else:
                discoveryMusic = temp.getFolder('Discovery (Music)')
                if discoveryMusic == None:
                    temp.addFolder('Discovery (Music)')
                    discoveryMusic = temp.getFolder('Discovery (Music)')
                discoveryMusic.addBookmark(bookmark.title(), 
                                bookmarksSinceDate[bookmark.title()])
                elementCount += 1
                print(elementCount)
                # temp.getBookmark(bookmark.title()).delete()
        elif "YouTube" in bookmark.title():
            youtube.addBookmark(bookmark.title(), 
                                youtubeUrls[bookmark.title()])
            elementCount += 1
            print(elementCount)
            # temp.getBookmark(bookmark.title()).delete()
        else:
            elementCount += 1
            print(elementCount)
    print(len(elementList))
    print(elementList)
    for element in elementList:
        f.write('\t'.join(value for key, value in element.items()) + '\n')
    f.close()

if __name__ == "__main__":
    bookmarkArchiver("")
