import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob

import signal

BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAIPYjwEAAAAAMxcWc40PvgF2vZkmst9wL26NucQ%3D5o671fqtP0KxDGHMJ3LPlJ1qcZcRxFiF1j75zuOIQf3yGfzV3z"

# Inital program welcome message
welcome_message = "Welcome to the Twitter User Sentiment Analyzer! This program will allow you to analyze the Twitter sentiment of various users across multiple criteria: their personal tweets, their mentions, and their liked tweets. Sentiment scores are returned in the form XX / YY where XX represent the percentage of tweets that are positive and YY represents the percentage of tweets that are negative. There are currently four analysis types supported: personal, mentions, liked, and overall.\n"

# Current supported analysis types (overall takes an average of the other three types)
valid_types = ["personal", "mentions", "liked", "overall"]

# Initialize Tweepy API (Elevated Twitter developer account is required)
# auth = tweepy.OAuth2BearerHandler("ENTER PERSONAL BEARER TOKEN")
auth = tweepy.OAuth2BearerHandler(BEARER_TOKEN)
api = tweepy.API(auth)

# Prompt user for input and parse given user requests
def processInput():
    value = input("Enter a valid Twitter handle and anlysis type in the form \"@username, analysis_type\": ")
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
            # print(tweets)
            return user, tweets

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

#cleans tweets
def standardize(tweets):
    cleaned_tweets = []
    for tweet in tweets:
        #remove special characters
        new_tweet = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
        cleaned_tweets.append(new_tweet)
    return cleaned_tweets

#gets sentiment of passed in tweets as positive, negative, or neutral
def getSentiment(tweets):
    pos_tweets = []
    neg_tweets = []
    neutral_tweets = []

    for tweet in tweets:

        #creates TextBlob object using passed in tweet
        #this further processes the tweet by tokenizing it, removes stop words, does POS tagging.
        #all done over the textblob library
        analysis = TextBlob(tweet)
        
        #uses the sentiment classifier
        #TextBlob uses a dataset with positive and negative labels to use for training
        #internally, the Naive Bayes Classifier trains the data
        if analysis.sentiment.polarity > 0:
            pos_tweets.append(tweet)
        elif analysis.sentiment.polarity < 0: 
            neg_tweets.append(tweet)
        else:
            neutral_tweets.append(tweet)

    return pos_tweets, neg_tweets, neutral_tweets

#gives numerical results for the sentiment of a twitter user
def calculateTotalSentiment(user, pos_tweets, neg_tweets, neutral_tweets):
    total = len(pos_tweets) + len(neg_tweets) + len(neutral_tweets)

    pos_perc = (len(pos_tweets) / total) * 100 
    neg_perc = (len(neg_tweets) / total) * 100
    neutral_perc = (len(neutral_tweets) / total) * 100

    sentiment = None 
    
    if pos_perc > neg_perc and pos_perc >= neutral_perc:
        sentiment = "Positive!"
    elif neg_perc > pos_perc and neg_perc >= neutral_perc:
        sentiment = "Negative!"
    else:
        sentiment = "Neutral!"

    print(str(pos_perc) + "%" + " of the tweets are Positive!")
    print(str(neg_perc) + "%" + " of the tweets are Negative!")
    print(str(neutral_perc) + "%" + " of the tweets are Neutral!")

    print("The overall sentiment of " + user + " is " + sentiment)


# Handles graceful program exit
def handler(sig, fr):
    print("\nExiting program . . .")
    exit(1)

signal.signal(signal.SIGINT, handler)

# Main driver function
def main():
    print(welcome_message)
    while True:
        user, tweets = processInput()
        cleaned_tweets = standardize(tweets)

        (pos_tweets, neg_tweets, neutral_tweets) = getSentiment(cleaned_tweets)
        calculateTotalSentiment(user, pos_tweets, neg_tweets, neutral_tweets)


if __name__ == '__main__':
    main() 
