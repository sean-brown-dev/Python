import tweepy
import time
import xml.etree.ElementTree as xmlTree
from auto_responder import ResponseGenerator
from datetime import datetime
from dateutil import tz


def limit_handler(cursor):
    try:
        while True:
            yield cursor.next()
    except StopIteration:
        return
    except tweepy.RateLimitError:
        time.sleep(900)


class Bot:
    def __init__(self):
        self.start_time = datetime.now()
        self.since_id = 1
        self.response_generator = ResponseGenerator()

        # Initialized in connect_tweepy()
        self.oAuth = None
        self.tweepy_api = None
        self.connect_tweepy()

    def connect_tweepy(self):
        auth_tokens = self.get_oauth_tokens()

        self.oAuth = tweepy.OAuthHandler(auth_tokens['oAuth']['key'], auth_tokens['oAuth']['secret'])
        self.oAuth.set_access_token(auth_tokens['access_token']['token'], auth_tokens['access_token']['secret'])
        self.tweepy_api = tweepy.API(self.oAuth)

    def get_oauth_tokens(self):
        auth_tokens = {
            'oAuth': { 'key': '', 'secret': ''},
            'access_token': {'token': '', 'secret': ''}
        }

        twit_config = xmlTree.parse('./twitter_tokens.xml').getroot()
        oAuth_node = twit_config.find('consumerKey')
        acess_token_node = twit_config.find('accessToken')

        auth_tokens['oAuth']['key'] = oAuth_node.attrib['key']
        auth_tokens['oAuth']['secret'] = oAuth_node.attrib['secret']

        auth_tokens['access_token']['token'] = acess_token_node.attrib['token']
        auth_tokens['access_token']['secret'] = acess_token_node.attrib['secret']

        return auth_tokens

    def follow_back_all(self):
        for follower_page in limit_handler(tweepy.Cursor(self.tweepy_api.followers, count=100).pages()):
            for follower in follower_page:
                if not follower.following:
                    follower.follow()
                    print(f"Followed {follower.name}")

    def unfollow_non_follow_backs(self):
        for following_page in limit_handler(tweepy.Cursor(self.tweepy_api.friends, count=100).pages()):
            for following in following_page:
                if not following.followed_by:
                    self.tweepy_api.destroy_friendship(id=following.id)
                    print(f"Unfollowed {following.name}")

    def monitor_mentions(self):
        while True:
            try:
                for tweet in limit_handler(tweepy.Cursor(self.tweepy_api.mentions_timeline,
                                                         tweet_mode="extended",
                                                         since_id=self.since_id).items()):
                    self.since_id = max(tweet.id, self.since_id)

                    if self.start_time.replace(tzinfo=tz.tzlocal()) < tweet.created_at.replace(tzinfo=tz.tzutc()).astimezone(tz=tz.tzlocal()):
                        try:
                            print(f"[{datetime.now()}] >> Got a mention from {tweet.author.screen_name} to reply to.")
                            reply = self.response_generator.get_bot_response(tweet.full_text)

                            self.tweepy_api.update_status(
                                status=f"@{tweet.author.screen_name} {reply}",
                                in_reply_to_status_id=tweet.id,
                            )

                            print(f"[{datetime.now()}] >> Replied to {tweet.author.screen_name} with: '{reply}'")
                        except tweepy.TweepError as ex:
                            print(ex)

                time.sleep(60)
            except tweepy.TweepError as outerEx:
                print(outerEx)
                time.sleep(60)
