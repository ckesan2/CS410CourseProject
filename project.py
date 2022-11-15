import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob

import signal

# Inital program welcome message
welcome_message = "Welcome to the Twitter User Sentiment Analyzer! This program will allow you to analyze the Twitter sentiment of various users across multiple criteria: their personal tweets, their mentions, and their liked tweets. Sentiment scores are returned in the form XX / YY where XX represent the percentage of tweets that are positive and YY represents the percentage of tweets that are negative. There are currently four analysis types supported: personal, mentions, liked, and overall.\n"

# Current supported analysis types (overall takes an average of the other three types)
valid_types = ["personal", "mentions", "liked", "overall"]

# Initialize Tweepy API (Elevated Twitter developer account is required)
auth = tweepy.OAuth2BearerHandler("ENTER PERSONAL BEARER TOKEN")
api = tweepy.API(auth)

# Prompt user for input and parse given user requests
def processInput():
    value = input("Enter a valid Twitter handle and anlysis type in the form \"@username, anlysis_type\": ")
    request = value.split(",")

    user = request[0]
    type = request[1]

    if type[0] == ' ':
        type = type[1:]

    if '@' not in user:
        return print("Please start Twitter handle names with @")
    elif type not in valid_types:
        return print("Please enter a valid analysis type (personal, mentions, liked, overall)")

    user = user[1:]
    try:
        u = api.get_user(screen_name=user)

        # Check if user's account type is private
        if u.protected:
            return print("This user is private, please enter a public Twitter handle!")
        else:

            # Fetch relevant tweets based on analysis type
            if type == "personal":
                tweets = getTweets(user)
            elif type == "mentions":
                tweets = getMentions(user)
            elif type == "liked":
                tweets = getLiked(user, u)
            else:
                tweets = getTweets(user) + getMentions(user) + getLiked(user, u)

            # Currently relevant tweets are printed to console (this will be updated in future development)
            print(tweets)

    except Exception as e:
        return print(str(e))

# Returns 200 most recent tweets of a user
def getTweets(user):
    tweet_info = api.user_timeline(screen_name = user, count = 200, include_rts = False, tweet_mode = "extended")
    tweets = [info.full_text for info in tweet_info]
    return tweets

# Returns 200 most recent mentions of a user
def getMentions(user):
    tweets = [mention.text for mention in tweepy.Cursor(api.search_tweets, q = ('@'+user)).items(200)]
    return tweets

# Returns 200 most recent liked tweets of a user
def getLiked(user, u):
    tweets = [liked.text for liked in tweepy.Cursor(api.get_favorites, user_id = u.id).items(200)]
    return tweets

# Handles graceful program exit
def handler(sig, fr):
    print("\nExiting program . . .")
    exit(1)

signal.signal(signal.SIGINT, handler)

# Main driver function
def main():
    print(welcome_message)
    while True:
        processInput()

if __name__ == '__main__':
    main() 
