#!/usr/bin/python3

"""
QuoteBot:
    A robut that grabs quotes from goodreads
    selecting by author
    using
    lxml
    requests
    the Goodreads api
    AND GOOD MANNERS SO GOODREADS DOESN'T GET MAD
    - Kimberly McCarty for Recurse Center Fall 1 2017 batch
"""

from lxml import etree
import lxml.html
import bs4
import requests
import urllib
import os
import time
import re

PAGEMAX = 10

class GoodReads(object):
    def __init__(self):
        """try to find dev_key in environmental variables
        and fallback to local file, otherwise
        throw an exception
        """
        try:
            self.dev_key = os.environ['GOODREADS_KEY']
#NOTE secret left unadded as I don't intend to write.
            #self.secret = os.environ['GOODREADS_SECRET']
        except KeyError:
            try:
                with open('keys.txt') as keyfile:
                    self.dev_key = keyfile.readline().split(": ")[1]
            except IOError:
                raise IOError("Please either set the GOODREADS_KEY environmental variable or put your developer key in a text file named keys.txt")



    def find_author(self, author_name):
        """Find the GoodReads author id for string author_name
        returns dict with GoodReads authorid number and author name
        """
        payload = {"key": self.dev_key}
        time.sleep(1)
        r = requests.get("https://www.goodreads.com/api/author_url/" + urllib.parse.quote(author_name), params = payload)
        try:
            tree = etree.fromstring(r.content)
            id_ = tree[1].attrib['id']
            name_ = tree[1][0].text #Correct author name, since users might mangle it and search for, say, Haruki instead of Haruki Murakami.
            return {"name": name_, "id": id_}
        except IndexError:
            raise ValueError("Author not found")

    def get_page(self, author, n):
        page = n
        quotePage = "https://www.goodreads.com/author/quotes/" + urllib.parse.quote(author["id"])
        time.sleep(1.1)
        return requests.get(quotePage, params={"page": n})

    def get_quotes(self, req, query=""):
        """Iterate over div.quoteText elements, and put their texts in
        a list
        """
        doc = bs4.BeautifulSoup(req.text, "lxml")
        #Trim scripts, which bs4 likes to parse as text :-(
        for script in doc(["script", "style"]):
            script.extract()

        quote_els = doc.find_all(class_ = "quoteText")
        #I couldn't get BS4's regexs to work and I have a life to live
#so i used one of python's string manipulations
        #Do you pity me?  Are you going to look down on me?
#These things gnaw at me
#oh well

#nevermind, I went with regexes anyway, even though they make me moody
        #quotes = [quote.get_text(strip=True) for quote in quote_els if query in quote.get_text()]
        quotes = [quote.get_text(strip=True) for quote in quote_els if re.search(query, quote.get_text())]
        return quotes

    def load_quote(self, query, author):
        """find first quote that contains the query
        Goodreads returns quotes sorted by popularity, so presumably several pages of depth is plenty for pop-conscious quotes
        returns string of quote
        """
        for n in range(1, PAGEMAX):
            r = self.get_page(author, n)
            quotes = self.get_quotes(r, query)
            #print(len(quotes))
            if len(quotes) > 0:
                return quotes
        #return empty quotes object
        return []

    #TODO add mechanism to skip quotes that aren't it
    def search(self, quote, author):
        try:
            author = self.find_author(author)
        except ValueError:
            return {"success": False, "msg": "Author not found"}
        quotes = self.load_quote(quote, author)
        #This function was successful if one or more quote was found
        success = len(quotes) > 0
        return {"author": author, "quotes": quotes, "success": success}




if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        gr = GoodReads()
        #Slices actually return [] if a slice calls invalid index!  That's perfect for this, and I didn't know they worked like that.
        print(gr.search(sys.argv[1], "".join(sys.argv[2:])))
        #Guido thought of everything :)


        """
        author = gr.find_author(sys.argv[1])
        print(author)
        try:
            quotes = gr.load_quote(sys.argv[2], author)
        except IndexError:
            quotes = gr.load_quote("", author)
        [print(quote) for quote in quotes]
        #print(len(quotes))
        """

    else:
        print("usage: QuoteBot author query")

