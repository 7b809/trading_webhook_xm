import os
from dotenv import load_dotenv
load_dotenv()
CLIENT_ID=os.getenv('DHAN_CLIENT_ID')
ACCESS_TOKEN=os.getenv('DHAN_ACCESS_TOKEN')
BASE_FEED_URL=os.getenv('BASE_FEED_URL')
TEST_LOG=os.getenv('TEST_LOG','true').lower()=='true'
