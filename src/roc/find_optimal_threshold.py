import numpy as np
from sklearn import metrics
import requests 
import json
import yaml
import pandas as pd
import tqdm 

def ns_nlu_hatespeech(config, text):
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
        payload_values["text"] = text
        # print(text)
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
    
def find_optimal_threshold(y_true, y_pred):
    """ Find the optimal probability cutoff point for a classification model related to event rate
    Returns
    -------     
    list type, with optimal cutoff value
    """
    # Using roc_curve function in sklearn python library to get
    # False Positive Rate, True Positive Rate and Precision
    fpr, tpr, threshold = metrics.roc_curve(y_true, y_pred)
    i = np.arange(len(tpr)) 
    roc = pd.DataFrame({'tf' : pd.Series(tpr-(1-fpr), index=i), 'threshold' : pd.Series(threshold, index=i)})
    roc_t = roc.iloc[(roc.tf-0).abs().argsort()[:1]]
    return list(roc_t['threshold']) 

# Reading config file for MODELID and ACCESS_TOKEN
with open("config.yaml", "r") as yamlfile:
    config = yaml.load(yamlfile, Loader=yaml.FullLoader)

# Reading validation data
f = open('neuralingo_nlu_hatespeech_tutorial_data_val.json')
data = json.load(f)

# Saving true labels
y_true = []
for i in data:
    if i["intent"] == "hate_and_offensive":
        y_true.append(1)
    else:
        y_true.append(0)

# Saving predicted confidence scores
y_pred = []
for i in tqdm.tqdm(data):
    _, confidence = ns_nlu_hatespeech(config, i["text"])
    y_pred.append(confidence)

# Find optimal probability threshold
threshold = find_optimal_threshold(y_true, y_pred)
print("="*100)
print("Optimal Threshold calculated based on validation dataset is : "+ str(threshold[0]))
print("="*100)
