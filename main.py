import time
import threading
from services.list_token import listToken
from services.send_offer import sendOffer
from services.take_bid_services import takeBidServices
from utils.db_data_utils import getAllDataDB, lastSalePriceAll_utils, saveAllDataDB
from utils.get_access_token import getAccessToken
from utils.get_collections import getCollectionsData
from utils.get_user_assets import getUserAssets
from utils.beth_balance import getBETHbalance
from utils.helpers import newDataTakeBid
from utils.order_data import orderDataTakeBid, orderUserData


def startListing(user_tokens:dict):
    tokens:list[dict] = user_tokens.get('tokens', [])
    for item in tokens:
        found:bool = item['found']
        listing_enabled:bool = item.get('listing enabled', False)
        if found and listing_enabled:
            listToken(item)

def startTakingOffers(new_user_tokens:list):
    for item in new_user_tokens:
        take_bids_enabled:bool = item['take bids enabled']
        if take_bids_enabled:
            takeBidServices(item)

def startSendingOffers(item:dict):
    bought:bool = item['bought']
    itemsOwned = int(item.get('itemsOwnedByContract',0))
    min_num_assets_per_contract = int(item['min num assets per contract'])
    max_num_assets_per_contract = int(item['max num assets per contract'])
    offers_enabled:bool = item['offers enabled'] == "yes"
    if not bought and offers_enabled and itemsOwned>=min_num_assets_per_contract and itemsOwned<max_num_assets_per_contract:
        sendOffer(item)



def run():

    thread1 = threading.Thread(target=getAccessToken)
    thread2 = threading.Thread(target=getBETHbalance)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
    
    user_tokens = getUserAssets()
    collection_info = getCollectionsData()

    orderUserData(user_tokens, collection_info)
    orderDataTakeBid(user_tokens)


    new_user_tokens = newDataTakeBid(user_tokens)

    lastSalePriceAll_utils()
    getAllDataDB()

    thread1 = threading.Thread(target=startListing, args=(user_tokens,))
    thread2 = threading.Thread(target=startTakingOffers, args=(new_user_tokens,))

    thread1.start()
    time.sleep(0.25)
    thread2.start()

    thread1.join()
    thread2.join()

    chunk_size = 10

    chunks = [collection_info[i:i + chunk_size] for i in range(0, len(collection_info), chunk_size)]

    for chunk in chunks:

        threads = []
        for item in chunk:
            thread = threading.Thread(target=startSendingOffers, args=(item,))
            threads.append(thread)
            time.sleep(0.1)
            thread.start()

        for thread in threads:
            thread.join()

    saveAllDataDB()


if __name__ == "__main__":
    run()