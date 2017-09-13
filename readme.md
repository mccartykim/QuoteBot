# Goodreads Quote Bot #

I'm not sure whether this bot will live on mastodon (it's a good neighborhood) or irc (a rowdy neighborhood)

Either way, the plan is:

Use the Goodreads API to find an author, and then search for the best fitting quote

Initial version "flow"
* IMPORTANT! Limit request time.  Probably going to make the request object explicitly single threaded and prone to reject requests.
* Find best fit for author.
* Scrape each page until we find a fit

Later refinements:
* Can I search without author?
* Can I cache quotes from popular authors? Will pagination make that weird?
* Could I set up a queue?  Works well for Twitter, Masto, or IRC...
