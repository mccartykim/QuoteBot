import requests
import re
from mastodon import Mastodon
#import asyncio
import time

#based on example code

# Register app - only once!
def init_register():
    Mastodon.create_app(
        'pytooterapp',
        api_base_url = 'https://botsin.space',
        to_file = 'pytooter_clientcred.secret'
    )

# Log in - either every time, or use persisted
def new_session():
    mastodon = Mastodon(
        client_id = 'pytooter_clientcred.secret',
        api_base_url = 'https://botsin.space'
    )
    mastodon.log_in(
        input("Mastodon Email"),
        input("Mastodon Password"),
        to_file = 'pytooter_usercred.secret'
    )

# Create actual API instance
def get_api():
    mastodon = Mastodon(
        client_id = 'pytooter_clientcred.secret',
        access_token = 'pytooter_usercred.secret',
        api_base_url = 'https://botsin.space'
    )
    return mastodon

def get_mentions(mast, since_id=None):
    mentions = [mention for mention in mast.notifications(since_id=since_id) if mention['type'] == 'mention']
    print(mentions)
    return mentions


def main():
    mast = get_api()
    since_id = None
    try:
        with open("since_id.txt") as f:
            since_id = int(f.readline())
    except FileNotFoundError:
        #Default is a sane value
        pass
    mentions = get_mentions(mast, since_id)
    #Prevent errors if since_id was None, since Python doesn't cast None to 0 in comparison operators
    since_id = since_id or 0
    for mention in mentions:
        #check if it's a new toot, sometimes people mention accounts in past toots automatically
        print(mention)
        context = mast.status_context(mention['id'])
        if (int(mention['id']) > since_id):
            since_id = int(mention['id'])
        if (len(context['ancestors']) == 0):
            resp = ""
            try:
                #strip out html using regex from stack overflow
                #https://stackoverflow.com/a/4869782
#as well as usernames
                content = re.sub('<[^<]+?>', '', mention['status']['content'])
                content = re.sub(r'(\s|^)@\w+', '', content)
                query, author = content.split(",")
                print(query)
                print(author)
                toot_search(query.strip(), author.strip(), mention['status']['id'])
            except ValueError as e:
                resp = "I look up authors given the format:\nquery, author\nlike: families, Leo Tolstoy"
                mast.status_post(resp, visibility="private", in_reply_to_id=mention['status']['id'])
    with open("since_id.txt", "w") as out_:
        out_.write(str(since_id))

"""API communication bits"""
FLASK_URL="http://localhost:5000/"

def quote_lookup(query, author):
    FLASK_PATH = "search_quote"
    url = FLASK_URL + FLASK_PATH
    r = requests.post(url, params= {"query": query, "author": author})
    #[1:] trims out the extra /
    nextPath =  r.json()['result'][1:]
    #Wait for server to process request
    print(nextPath)
    resp = {'state': "PENDING"}
    while (resp['state'] == "PENDING"):
        time.sleep(2)
        print(FLASK_URL+nextPath)
        r = requests.get(FLASK_URL + nextPath)
        try:
            resp = r.json()
        except ValueError:
            print(r.text)
    return resp

def toot_search(query, author, mention_id):
    mast = get_api()
    result = quote_lookup(query, author)
    if result["success"]:
        if result["author"]["name"] in result["quotes"][0][:400]:
            msg = result["quotes"][0][:400] + ", source: GoodReads"
        else:
            msg = "{} - {}, source Goodreads".format(result["quotes"][0][:400], " - " + result["author"]["name"])
    else:
        msg = "No result found on the first 10 pages of GoodReads quotes, and I'm a lazy robot that doesn't exist for the humanoid gaze.  Sorry."
    mast.status_post(msg, in_reply_to_id=mention_id, visibility="private")

if __name__=="__main__":
    main()
    #init_register()
    #new_session()
