from config.settings import BASE_FEED_URL

def build_feed_url(client_id,exchange,security_id,request_code):
    return f"{BASE_FEED_URL}/marketfeed?client_id={client_id}&exchange={exchange}&security_id={security_id}&request_code={request_code}"
