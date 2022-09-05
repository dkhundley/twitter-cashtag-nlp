# Importing the necessary Python libraries
import os
import json
import yaml
import requests

## SCRIPT SETUP
## ---------------------------------------------------------------------------------------------------------------------
# Loading in my personal Twitter API keys from a sensitive file not uploaded to GitHub
with open('../keys/twitter-api-keys.yaml', 'r') as f:
    twitter_keys = yaml.safe_load(f)
    bearer_token = twitter_keys['dkhundley_twitter_creds']['bearer_token']

# Setting a helper function to handle headers for OAuth authorization
def bearer_oauth(r):
    r.headers['Authorization'] = f'Bearer {bearer_token}'
    r.headers['User-Agent'] = 'v2FilteredStreamPython'
    return r

# Setting the proper API URL
twitter_api_url = 'https://api.twitter.com/2/tweets/search/stream'

# Setting parameters for new rules
new_rules = [
    {'value': '$aapl OR $tsla OR $twtr'}
]

# Structuring payload to add new rules
add_payload = {
    'add': new_rules
}

## CHECKING CURRENT RULES
## ---------------------------------------------------------------------------------------------------------------------
print('Checking the current rules...')

# Checking with the Twitter API to see which rules are currently set for the filtered stream
response = requests.get(f'{twitter_api_url}/rules', auth = bearer_oauth)

# Printing out the appropriate response, whether it be the appropriate rules or an error
if response.status_code != 200:
    raise Exception(f'Cannot get rules (HTTP {response.status_code}): {response.text}')
print('Current rules: ')
print(json.dumps(response.json()))

# Saving results to variable
current_rules = response.json()



## DELETING CURRENT RULES
## ---------------------------------------------------------------------------------------------------------------------
# Iterating through any currently existing rules to delete them
if current_rules is not None or 'data' in current_rules:

    print('Deleting old rules...')

    # Collecting the IDs of the currently existing rules
    current_rule_ids = list(map(lambda rule: rule['id'], current_rules['data']))

    # Structuring a delete payload to send to API
    delete_payload = {'delete': {'ids': current_rule_ids}}

    # Sending the delete payload to the API
    response = requests.post(f'{twitter_api_url}/rules', auth = bearer_oauth, json = delete_payload)

    # Verifying delete results
    if response.status_code != 200:
        raise Exception(f'Cannot delete rules (HTTP {response.status_code}): {response.text}')
    print(json.dumps(response.json()))



## SETTING NEW RULES
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
# response = requests.get(twitter_api_url, auth = bearer_oauth, stream = True)
# print(response.status_code)
# for response_line in response.iter_lines():
#     if response_line:
#         json_response = json.loads(response_line)
#         print(json.dumps(json_response, indent = 4, sort_keys = True))

test_counter = 0
with requests.get(twitter_api_url, auth = bearer_oauth, stream = True) as response:
    test_counter += 1
    print(f'Test counter: {test_counter}')
    print(response.status_code)
    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            print(json.dumps(json_response, indent = 4, sort_keys = True))