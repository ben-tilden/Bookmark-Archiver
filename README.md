# Bookmark-Archiver

archiveBookmarks.py is a python program which automatically organizes Chrome bookmarks according to personal specifications, extracts data from specific bookmarks, and writes said data into a local file 'temp.txt'

Please note that chromeBookmarkEditor.py has been cloned and edited from https://github.com/robperc/ChromeBookmarkEditor. It was originally written by Robert I. Percival (https://github.com/robperc).

A note on bookmark deletion: When the delete() method of the initial Chrome class deletes a bookmark or folder, the bookmark or folder immediately below that bookmark or folder takes its places, and all other contents shift up with it. This makes deleting during iteration, as well as reassigning items in general, more complicated.

The most significant methods:
* getElementList()
    * Iterates through Chrome bookmarks in /Other Bookmarks/temp and moves music and YouTube links into different folders based on website and content
    * Deletes unnecessary bookmarks after organizing
    * Returns a list of all songs and albums to be archived
* archiveBookmarks()
    * Writes all elements in the element list to temp.txt
    * Songs will be of the format:
        * `<type> <artist> <title>`
    * Albums will be of the format:
        * `<type> <artist> <title> <year>`

## Requirements

There is a requirements.txt file included in the main directory  
Type 'pip install -r requirements.txt' into the command line and enter and the necessary packages will install

## Built With

re
datetime
multiprocessing
requests: https://requests.kennethreitz.org/en/master/
lxml: https://lxml.de/

## Author

Ben Tilden
