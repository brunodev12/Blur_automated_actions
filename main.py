from utils.get_access_token import getAccessToken
from services.take_bid_services import takeBidServices
from utils.get_user_assets import getUserAssets

def run():

    getAccessToken()

    user_tokens = getUserAssets()

    new_user_tokens = []

    for item in user_tokens:
        new_user_tokens.append(item)
        if len(item['tokens']) > 1:
            for token in item['tokens']:
                new_item = {'contract': item['contract'], 'tokens': [token]}
                new_user_tokens.append(new_item)

    for i in new_user_tokens:
        tokens = i['tokens']
        contract = i['contract']
        takeBidServices(tokens, contract)

if __name__ == "__main__":
    run()