from asyncore import write
import re
import tweepy
from tweepy import OAuthHandler
import requests
import json
import yaml

class TwitterClient(object):
    def __init__(self, config):
        # keys and tokens from the Twitter Dev Console
        CONSUMER_KEY = config["twitter-auth"]["CONSUMER_KEY"]
        CONSUMER_SECRET = config["twitter-auth"]["CONSUMER_SECRET"]
        ACCESS_TOKEN = config["twitter-auth"]["ACCESS_TOKEN"]
        ACCESS_TOKEN_SECRET = config["twitter-auth"]["ACCESS_TOKEN_SECRET"]
        
        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
			# set access token and secret
            self.auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
			# create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")

    def clean_tweet(self, tweet):
        '''
		Utility function to clean tweet text by removing links, special 
        characters using simple regex statements.
		'''
        # Remove @ sign
        tweet = re.sub("@[A-Za-z0-9]+","",tweet)
        # Remove http links
        tweet = re.sub(r"(?:\@|http?\://|https?\://|www)\S+", "", tweet)
        tweet = " ".join(tweet.split())
        return tweet

    def ns_nlu_hatespeech(self, config, tweet):
        '''
		Utility function to classify whether the passed tweet 
        contains hate or offensive text 
        using NeuralSpace NLU -> NeuraLingo
        https://docs.neuralspace.ai/natural-language-understanding/overview
		'''
        try:
            payload_values = {}
        
            url = config["neuralspace-nlu-auth"]["neuralspace_nlu_url"]
            MODEL_ID = config["neuralspace-nlu-auth"]["MODEL_ID"]
            ACCESS_TOKEN = config["neuralspace-nlu-auth"]["ACCESS_TOKEN"]
        
            payload_values["modelId"] = MODEL_ID
            payload_values["text"] = self.clean_tweet(tweet)
        
            payload = json.dumps(payload_values)

            headers = {
                'Authorization': ACCESS_TOKEN,
                'Content-Type': 'application/json'
            }
            response = json.loads(requests.request(
                "POST", 
                url, 
                headers=headers, 
                data=payload).text
            )
        
            predicted_intent = response["data"]["intent"]["name"]
            predicted_confidence = response["data"]["intent"]["confidence"]

            return predicted_intent, predicted_confidence
        
        except:
            print("Error: NeuraLingo failed. Please check your ACCESS_TOKEN and MODEL_ID.")

    def ns_language_detection(self, config, tweet):
        '''
		Utility function to detect language of tweet  
        using NeuralSpace Language Detection API
        https://docs.neuralspace.ai/language-detection/overview
		'''
        try:
            payload = {}
            url = config["neuralspace-lang-detection-auth"]["neuralspace_lang_detect_url"]
            ACCESS_TOKEN = config["neuralspace-lang-detection-auth"]["ACCESS_TOKEN"]
        
            payload["text"] = self.clean_tweet(tweet.text)
            headers = {
            'authorization': ACCESS_TOKEN,
            }
            response = json.loads(requests.request(
                "POST", 
                url, 
                headers=headers, 
                data=payload).text
            )
            detected_lang = response["data"]["detected_languages"][0]["language"]
            
            return detected_lang
        
        except:
            print("Error: NeuralSpace Language Detection failed. Please check your ACCESS_TOKEN.")

    def get_tweets(self, config, user_handle, count_top):
        tweets = []
        # call twitter api to fetch tweets
        fetched_tweets = self.api.user_timeline(screen_name = user_handle, count=count_top)
        
		# parsing tweets one by one
        for tweet in fetched_tweets:
            detected_lang = self.ns_language_detection(config, tweet)
            
            #Check if detected_lang is belongs to list of training data langauges.
            if detected_lang in config["training-data"]["languages"]:
                parsed_tweet = {}
                parsed_tweet['text'] = tweet.text
                intent, confidence = self.ns_nlu_hatespeech(config, tweet.text)
                parsed_tweet["intent"] = intent
                parsed_tweet["confidence"] = confidence
                tweets.append(parsed_tweet)
            
            else:
                print("This tweet is " +str(detected_lang) + " language.")
                print("Please add training data in this language if you wish to classify this tweet")
        
        return tweets

def main_pass_userhandle(config):
    # creating object of TwitterClient Class
    api = TwitterClient(config)
    
    # calling function to get tweets
    tweets = api.get_tweets(
        config, 
        user_handle = config["twitter-query"]["USER_HANDLE"], 
        count_top = config["twitter-query"]["TOP_NUM_TWEETS"]
    )

    print("#"*200)
    print("NeuralSpace Twitter HateSpeech Bot")
    print("#"*200)
    
    print("Here are the " + 
        str(config["twitter-query"]["TOP_NUM_TWEETS"]) +
        " most recent tweets by " + 
        str(config["twitter-query"]["USER_HANDLE"])
    )
    
    for i, tweet in enumerate(tweets):
        print("----> Tweet: ", i+1)
        if tweet["intent"] == "hate_and_offensive":
            print("This tweet cannot be displayed since it contains hate and offensive text")
        else:
            print(tweet["text"])

    if config["report"] is True:
        f = open(config["report"]["report-filename"], "w")
        f.write("#"*200, "\n")
        f.write("NeuralSpace Twitter HateSpeech Bot", "\n")
        f.write("#"*200, "\n")
        f.write("Here are the " + 
        str(config["twitter-query"]["TOP_NUM_TWEETS"]) +
        " most recent tweets by " + 
        str(config["twitter-query"]["USER_HANDLE"]), "\n")
        for i, tweet in enumerate(tweets):
            f.write("----> Tweet: ", i+1, "\n")
            if tweet["intent"] == "hate_and_offensive":
                f.write("This tweet cannot be displayed since it contains hate and offensive text", "\n")
            else:
                f.write(tweet["text"], "\n")
        print("Report has been saved!")

# def main_pass_tweeturl(config):
#     # creating object of TwitterClient Class
#     api = TwitterClient(config)

#     tweet = api.get_oembed(config["twitter-query"]["TWITTER_URL"])
#     return 0

def main():
    with open("config.yaml", "r") as yamlfile:
        config = yaml.load(yamlfile, Loader=yaml.FullLoader)
    
    if config["pass-userhandle"] is True:
        main_pass_userhandle(config)
    
    # if config["pass-tweet-url"] is True:
        # main_pass_tweeturl(config)
    
    if config["pass-userhandle"] is False and config["pass-tweet-url"] is False:
        print("Please check your config file. Choose atleast one task.")


if __name__ == "__main__":
    
    main()

