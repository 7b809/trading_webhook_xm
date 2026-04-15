import threading
import asyncio
import time
import logging
from dhanhq import marketfeed
from config.settings import CLIENT_ID, ACCESS_TOKEN


# ✅ LOGGER SETUP
logger = logging.getLogger("dhan_feed")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
logger.addHandler(handler)


def normalize_instruments(instruments):
    return [tuple(i) for i in instruments]


class DhanLiveFeed:
    def __init__(self, socketio):
        self.socketio = socketio
        self.feed = None
        self.running = False
        self.lock = threading.Lock()
        self.loop = None
        self.active_instruments = set()

        # ✅ NEW: user mapping
        self.user_subscriptions = {}
        self.instrument_to_users = {}

    def start(self, instruments):
        instruments = normalize_instruments(instruments)

        with self.lock:
            if self.running:
                return self._add_instruments_internal(instruments)

            self.running = True

            t = threading.Thread(target=self._start_feed, args=(instruments,))
            t.daemon = True
            t.start()

            return {"status": "started", "instruments": instruments}

    def _start_feed(self, instruments):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        try:
            self.active_instruments.update(instruments)

            self.feed = marketfeed.DhanFeed(
                CLIENT_ID,
                ACCESS_TOKEN,
                list(self.active_instruments),
                "v2"
            )

            logger.info("✅ Feed initialized")

            retry_delay = 2

            while self.running:
                try:
                    self.feed.run_forever()

                    data = self.feed.get_data()
                    if data:
                        logger.info(f"DATA: {data}")

                        # ✅ NEW: route data to specific users
                        security_id = str(data.get("security_id"))
                        exchange = data.get("exchange_segment")

                        key = (exchange, security_id)
                        users = self.instrument_to_users.get(key, set())

                        for user in users:
                            self.socketio.emit("market_data", data, room=user)

                except Exception as e:
                    err = str(e)
                    logger.error(f"Feed error: {err}")

                    if "429" in err:
                        logger.warning("⚠️ Rate limited. Sleeping 60s...")
                        time.sleep(60)
                        retry_delay = 2
                        continue

                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, 30)

        except Exception as e:
            logger.error(f"Initialization error: {e}")

    def _add_instruments_internal(self, instruments):
        new_instruments = set(instruments) - self.active_instruments

        if not new_instruments:
            return {"status": "no_new_instruments"}

        try:
            self.feed.subscribe_symbols(list(new_instruments))
            self.active_instruments.update(new_instruments)

            logger.info(f"Added instruments: {new_instruments}")

            return {"status": "added", "instruments": list(new_instruments)}

        except Exception as e:
            logger.error(f"Add error: {e}")
            return {"error": str(e)}

    # ✅ NEW: user-based subscription
    def subscribe_user(self, user_id, instruments):
        instruments = normalize_instruments(instruments)

        if user_id not in self.user_subscriptions:
            self.user_subscriptions[user_id] = set()

        self.user_subscriptions[user_id].update(instruments)

        for inst in instruments:
            key = (inst[0], inst[1])  # exchange, security_id

            if key not in self.instrument_to_users:
                self.instrument_to_users[key] = set()

            self.instrument_to_users[key].add(user_id)

        # subscribe globally
        if self.feed:
            new_global = set(instruments) - self.active_instruments

            if new_global:
                self.feed.subscribe_symbols(list(new_global))
                self.active_instruments.update(new_global)

        logger.info(f"User {user_id} subscribed to {instruments}")

        return {"status": "user subscribed", "user": user_id}

    def add_instruments(self, instruments):
        instruments = normalize_instruments(instruments)

        if self.feed:
            return self._add_instruments_internal(instruments)

        return {"error": "feed not started"}

    def remove_instruments(self, instruments):
        instruments = normalize_instruments(instruments)

        if self.feed:
            try:
                remove_set = set(instruments) & self.active_instruments

                if not remove_set:
                    return {"status": "nothing_to_remove"}

                self.feed.unsubscribe_symbols(list(remove_set))
                self.active_instruments.difference_update(remove_set)

                logger.info(f"Removed instruments: {remove_set}")

                return {"status": "removed", "instruments": list(remove_set)}

            except Exception as e:
                logger.error(f"Remove error: {e}")
                return {"error": str(e)}

        return {"error": "feed not started"}

    def stop(self):
        self.running = False

        if self.feed:
            try:
                self.feed.close_connection()
                logger.info("✅ Feed stopped")
            except Exception as e:
                logger.error(f"Stop error: {e}")