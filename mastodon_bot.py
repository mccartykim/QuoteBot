import requests
from mastodon import Mastodon

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
        api_base_url = 'https://mastodon.social'
    )
    return mastodon

def get_mentions(since_id=None):
    mentions = [mention for mention in mastodon.notifications(since_id=since_id) if mention['type'] == 'mention']

#Global object for Mastodon, because I don't want multiple copies screwing up the rate limit
mastodon = None

def main():
    mastodon = get_api()
    since_id = None
    with open("since_id.txt") as f:
        since_id = int(f.readline())
    mentions = get_mentions(since_id)
    #Prevent errors if since_id was None, since Python doesn't cast None to 0 in comparison operators
    since_id = since_id or 0
    for mention in mentions:
        #check if it's a new toot, sometimes people mention accounts in past toots automatically
        context = mastodon.status_context(mention['id'])
        if (!context['ancestors']):
            if (int(mention['id']) > since_id):
                since_id = int(mention['id'])
            try:
                query, author = mention['status'].split(",")
                resp = quote_lookup(query, author)
            except ValueError:
                resp = "I look up authors given the format:\nquery, author\nlike: families, Leo Tolstoy"
            finally:
                mastodon.status_post(resp, in_reply_to_id=mention['id'])





#TODO: function to get request

    #TODO: toot first quote from results

