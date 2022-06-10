import re
import tweepy
from tweepy import OAuthHandler
import requests
import json
import yaml
import csv
import tqdm 

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
            self.api = tweepy.API(self.auth, wait_on_rate_limit=True)
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
        using NeuralSpace NLU -> Language Understanding
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
            print("Error: Language Understanding failed. Please check your ACCESS_TOKEN and MODEL_ID.")

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

            payload["text"] = self.clean_tweet(tweet)
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

    def get_tweets(self, user_handle, count_top):
        # call twitter api to fetch tweets
        fetched_tweets = self.api.user_timeline(screen_name = user_handle, count=count_top, exclude_replies=False)
        return fetched_tweets
    
    def calculate_intent(self, config, fetched_tweets, userhandle=True):
		# parsing tweets one by one
        tweets = []
        print(fetched_tweets)
        for tweet in tqdm.tqdm(fetched_tweets):
            if userhandle == True:
                tweet = tweet.text
            detected_lang = self.ns_language_detection(config, tweet)
            
            #Check if detected_lang is belongs to list of training data langauges.
            if detected_lang in config["training-data"]["languages"]:
                parsed_tweet = {}
                parsed_tweet['text'] = tweet
                intent, confidence = self.ns_nlu_hatespeech(config, tweet)
                parsed_tweet["intent"] = intent
                parsed_tweet["confidence"] = confidence
                tweets.append(parsed_tweet)
            
            else:
                print("This tweet is " +str(detected_lang) + " language.")
                print("Please add training data in this language if you wish to classify this tweet")
        
        return tweets
    
    def get_tweets_from_url(self, config):
        url = config["twitter-query"]["TWITTER_URL"]
        name = url.split('/')[-3]
        tweet_id = url.split('/')[-1]
        top_comments = config["twitter-query"]["RECENT_NUM_COMMENTS"]
        
        replies=[]
        print("here")
        for tweet in tweepy.Cursor(self.api.search,q='to:'+name, result_type='recent').items():
            if hasattr(tweet, 'in_reply_to_status_id_str'):
                if (tweet.in_reply_to_status_id_str==tweet_id):
                    if len(replies) < top_comments:
                        replies.append(tweet._json['text'])
                        print(len(replies))
        return replies
    
        
def main_pass_userhandle(config):
    # creating object of TwitterClient Class
    api = TwitterClient(config)
    
    user_handle = config["twitter-query"]["USER_HANDLE"]
    count_top = config["twitter-query"]["RECENT_NUM_TWEETS"]

    tweets = api.get_tweets(
        user_handle, count_top
    )
    tweets = api.calculate_intent(config, tweets, userhandle=True)

    print("Here are the " + 
        str(config["twitter-query"]["RECENT_NUM_TWEETS"]) +
        " most recent tweets by " + 
        str(config["twitter-query"]["USER_HANDLE"])
    )
    
    hate_count = 0
    confidence_score = 0
    tweets_all = []
    for i, tweet in enumerate(tweets):
        tweet_info = []
        tweet_info.append("Tweet: " + str(i+1))
        tweet_info.append(config["twitter-query"]["USER_HANDLE"])
        print("----> Tweet: ", i+1)
        if tweet["intent"] == "hate_and_offensive":
            if tweet["confidence"] >= config["control-precision"]["threshold-roc"]:
                tweet_info.append("hate_and_offensive")
                tweet_info.append(tweet["confidence"])
                tweet_info.append(tweet["text"])
                hate_count +=1
                confidence_score += tweet["confidence"]
                print("Intent predicted ->  hate and offensive")
        else:
            tweet_info.append("no_hate")
            tweet_info.append(tweet["confidence"])
            tweet_info.append(tweet["text"])
            print("Intent predicted ->  no hate")
        tweets_all.append(tweet_info)

    print("="*100)
    print(str(hate_count)+" tweets out of "+ str(len(tweets)) +" have been classified as hate and offensive!")
    if hate_count > 0:
        print("Average predicted confidence scores of hate tweets is : " + str(confidence_score/hate_count))
    print("="*100)
    
    if config["report"]["download-report"] is True:
        with open(config["report"]["report-filename-pass-userhandle"], 'w', encoding='UTF8', newline='') as f:
            header = ['tweet_no.', 'Twitter UserHandle', 'Predicted Intent', 'Confidence of Predicted Intent', 'Tweet']
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(tweets_all)
        print("Report has been saved!")

def main_pass_tweeturl(config):
    # creating object of TwitterClient Class
    api = TwitterClient(config)
    tweet_replies = api.get_tweets_from_url(config)
    tweets = api.calculate_intent(config, tweet_replies, userhandle=False)

    print("Here are the " + 
        str(config["twitter-query"]["RECENT_NUM_COMMENTS"]) +
        " most recent tweets")
    hate_count = 0
    confidence_score = 0
    tweets_all = []
    for i, tweet in enumerate(tweets):
        print("----> Tweet: ", i+1)
        tweet_info = []
        tweet_info.append("Tweet: " + str(i+1))
        tweet_info.append(config["twitter-query"]["TWITTER_URL"])
        if tweet["intent"] == "hate_and_offensive":
            if tweet["confidence"] >= config["control-precision"]["threshold-roc"]:
                tweet_info.append("hate_and_offensive")
                tweet_info.append(tweet["confidence"])
                tweet_info.append("This tweet cannot be displayed since it contains hate and offensive text")
                hate_count +=1
                confidence_score += tweet["confidence"]
                print("Intent predicted ->  hate and offensive")
        else:
            tweet_info.append("no_hate")
            tweet_info.append(tweet["confidence"])
            tweet_info.append(tweet["text"])
            print("Intent predicted ->  no hate")
        tweets_all.append(tweet_info)
    
    print("="*100)
    print(str(hate_count)+" tweets out of "+ str(len(tweets)) +" have been classified as hate and offensive!")
    if hate_count > 0:
        print("Average predicted confidence scores of hate tweets is : " + str(confidence_score/hate_count))
    print("="*100)
    
    if config["report"]["download-report"] is True:
        with open(config["report"]["report-filename-pass-url"], 'w', encoding='UTF8', newline='') as f:
            header = ['tweet_no.', 'Twitter URL', 'Predicted Intent', 'Confidence of Predicted Intent', 'Comment']
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(tweets_all)
        print("Report has been saved!")
    
def main():
    with open("config.yaml", "r") as yamlfile:
        config = yaml.load(yamlfile, Loader=yaml.FullLoader)
    
    if config["pass-userhandle"] is True:
        print("Extracting the tweets ...")
        main_pass_userhandle(config)
    
    if config["pass-tweet-url"] is True:
        main_pass_tweeturl(config)
    
    if config["pass-userhandle"] is False and config["pass-tweet-url"] is False:
        print("Please check your config file. Choose atleast one task.")


if __name__ == "__main__":
    print("#"*100)
    print("NeuralSpace Twitter HateSpeech Bot")
    print("#"*100)
    
    main()

