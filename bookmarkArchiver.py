#!/usr/bin/env python3

# Program: bookmarkArchiver
# Objective: Organize bookmarks and add music to ia Writer docs
# Author: Ben Tilden

import os
import re
import datetime
from datetime import timezone
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

def bookmarkArchiver(date):
    youtubeUrls, bookmarksSinceDate = parseBookmarkList(date)
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
                set = {}
                titleSearch = (re.search('(.+): (.+) Album Review | Pitchfork',
                               bookmark.title()))
                artistName = titleSearch.group(1)
                page = requests.get(bookmarksSinceDate[bookmark.title()])
                tree = html.fromstring(page.content)
                dates = tree.xpath(
                            '//span'
                            '[@class="single-album-tombstone__meta-year"]'
                            '/text()[4]') #TODO: Better formatting
                if len(dates) > 1:
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
                                "date": dates[x]
                            })
                        set[artistName] = albumList
                else:
                    albumName = titleSearch.group(2)
                    set[artistName] = {
                        "album": albumName,
                        "date": dates[0]
                    }
                print(set)
                # Add to albums / Add to music to keep in mind *year* (f.write())
                # temp.getBookmark(bookmark.title()).delete()
            elif "Review" in bookmark.title():
                pass
                # print("Song: {}".format(bookmark.title()))
                # Add to music to keep in mind *year* or just notify
                # "Listen | Pitchfork"
                # temp.getBookmark(bookmark.title()).delete()
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