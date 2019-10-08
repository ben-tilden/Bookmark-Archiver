#!/usr/bin/env python3

# Program: bookmarkArchiver
# Objective: Organize bookmarks and add music to ia Writer docs
# Author: Ben Tilden

import os
import re
import datetime
from datetime import timezone #TODO: Clean up imports
import requests
import chrome_bookmarks
from lxml import html
from ChromeBookmarkEditor import Chrome

def parseBookmarkList(date):
    youtubeUrls = {}
    bookmarksSinceDate = {}
    givenDate = datetime.datetime(2019, 5, 15) #TODO: Hardcoded
    for url in chrome_bookmarks.urls:
        if "YouTube" in url.name:
            youtubeUrls[url.name] = url.url
        if (url.added > givenDate.replace(tzinfo=timezone.utc) and
            "Review" in url.name):
            bookmarksSinceDate[url.name] = url.url
    return youtubeUrls, bookmarksSinceDate

def processAlbumsPitchfork(bookmarkTitle, bookmarksSinceDate):
    set = {}
    titleSearch = (re.search('(.+): (.+) Album Review | Pitchfork',
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
            albumList = []
            for x in range(0, len(albumNames)):
                albumList.append({
                    "album": albumNames[x],
                    "year": years[x]
                })
            set[artistName] = albumList
    else:
        albumName = titleSearch.group(2)
        set[artistName] = {
            "album": albumName,
            "year": years[0]
        }
    return set

def processSongsPitchfork(bookmarkTitle, bookmarksSinceDate):
    set = {}
    print(bookmarkTitle)
    titleSearch = (re.search('“(.+)” by (.+) Review | Pitchfork',
                   bookmarkTitle))
    songName = titleSearch.group(1)
    artistName = titleSearch.group(2)
    page = requests.get(bookmarksSinceDate[bookmarkTitle])
    tree = html.fromstring(page.content)
    year = tree.xpath(
                '//span'
                '[@class="year"]'
                '/text()') #TODO: Better formatting
    set[artistName] = {
        "song": songName,
        "year": year[0]
    }
    return set

def bookmarkArchiver(year):
    youtubeUrls, bookmarksSinceDate = parseBookmarkList(year)
    f = open('/Users/bentilden/Library/Mobile Documents/'
             '27N4MQEA55~pro~writer/Documents/temp.txt', 'w+')
    chrome = Chrome()
    temp = chrome.otherBookmarks.getFolder('temp')
    youtube = temp.getFolder('YouTube')
    if youtube == None:
        temp.addFolder('YouTube')
        youtube = temp.getFolder('YouTube')
    for bookmark in temp.bookmarks:
        if "Pitchfork" in bookmark.title():
            if "Album Review" in bookmark.title():
                print(processAlbumsPitchfork(bookmark.title(), bookmarksSinceDate))
                # Add to albums / Add to music to keep in mind *year* (f.write())
                # temp.getBookmark(bookmark.title()).delete()
            elif "Review" in bookmark.title():
                print(processSongsPitchfork(bookmark.title(), bookmarksSinceDate))
                # Add to music to keep in mind *year* or just notify
                # temp.getBookmark(bookmark.title()).delete()
            elif "Listen | Pitchfork" in bookmark.title():
                pass
            else:
                pass
                # Add to articles to read / music discovery(?)
        elif "Tiny Mix Tapes" in bookmark.title():
            if "Music Review" in bookmark.title():
                pass
                # print("Album (TMT): {}".format(bookmark.title()))
                # Add to albums / Add to music to keep in mind *year*
                # Add to TMT reviews
            else:
                pass
                # Add to articles to read / music discovery(?)
        elif "YouTube" in bookmark.title():
            youtube.addBookmark(bookmark.title(), 
                                youtubeUrls[bookmark.title()])
            # temp.getBookmark(bookmark.title()).delete()
        # Check temp possible classifications
    f.close()

if __name__ == "__main__":
    bookmarkArchiver("")