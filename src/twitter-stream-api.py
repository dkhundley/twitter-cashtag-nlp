# Importing the necessary Python libraries
import os
import json
import yaml
import requests



## SCRIPT SETUP
## ---------------------------------------------------------------------------------------------------------------------
# Loading in my personal Twitter bearer token form a sensitive file not uploaded to GitHub
with open('../keys/twitter-api-keys.yaml', 'r') as f:
    twitter_keys = yaml.safe_load(f)
    bearer_token = twitter_keys['dkhundley_twitter_creds']['bearer_token']

# Setting up a helper function to handle headers for OAuth autharization
def bearer_oauth(r):
    r.headers['Authorization'] = f'Bearer {bearer_token}'
    r.headers['User-Agent'] = 'v2FilteredStreamPython'
    return r

# Setting the proper API URL
twitter_api_url = 'https://api.twitter.com/2/tweets/search/stream'

# Setting operaters for for new rules
new_rules = [
    {'value': '$aapl OR $tsla OR $twtr'}
]

# Structuring payload to add new rules
add_payload = {
    'add': new_rules
}



## CHECKING CURRENT STREAM RULES
## ---------------------------------------------------------------------------------------------------------------------
print('Checking the current rules...')

# Checking with the Twitter API to see which rules currently are set for the the filtered stream
response = requests.get(f'{twitter_api_url}/rules', auth = bearer_oauth)

# Printing out the approrpiate response, whether it be the appropriate rules or an error
if response.status_code != 200:
    raise Exception(f'Cannot get rules (HTTP {response.status_code}): {response.text}')
print('Current rules: ')
print(json.dumps(response.json()))

# Saving the results to a variable
current_rules = response.json()



## DELETING CURRENT RULES
## ---------------------------------------------------------------------------------------------------------------------
# Iterating through any currently existing rules in order to delete them
if current_rules is not None or 'data' in current_rules:

    print('Deleting current rules...')

    # Collecting the IDs of the currently existing rules
    current_rule_ids = list(map(lambda rule: rule['id'], current_rules['data']))

    # Structuring a delete payload to the API
    delete_payload = {'delete': {'ids': current_rule_ids}}

    # Sending the delete payload to the API
    response = requests.post(f'{twitter_api_url}/rules', auth = bearer_oauth, json = delete_payload)

    # Verifying the delete results
    if response.status_code != 200:
        raise Exception(f'Cannot delete rules (HTTP {response.status_code}): {response.text}')
    print(json.dumps(response.json()))



## ADDING NEW RULES
## ---------------------------------------------------------------------------------------------------------------------
print('Adding new rules...')

# Sending the add payload to the API
response = requests.post(f'{twitter_api_url}/rules', auth = bearer_oauth, json = add_payload)

# Printing out the results appropriately
if response.status_code != 201:
    raise Exception(f'Cannot add rules (HTTP {response.status_code}): {response.text}')
print(json.dumps(response.json()))



## STARTING TWEET STREAM
## ---------------------------------------------------------------------------------------------------------------------
print('Starting tweet stream with new rules in effect...')

# Initializing the tweet counter
tweet_counter = 0

# Starting the tweet stream
response = requests.get(twitter_api_url, auth = bearer_oauth, stream = True)

# Printing out stream results until 20 tweets have been surfaced
for response_line in response.iter_lines():
    if response_line:
        if tweet_counter >= 20:
            break
        else:
            tweet_counter +=1
            print(f'Tweet counter: {tweet_counter}')
            json_response = json.loads(response_line)
            print(json.dumps(json_response, indent = 4, sort_keys = True))