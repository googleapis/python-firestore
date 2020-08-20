import argparse
import datetime
import logging
import random
import sys
import time

from google.cloud import firestore


logger = logging.getLogger("update_document")


def update_once(doc_ref, updates, count):
    logger.info(f"Updating: {doc_ref.path}  [{updates:6}/{count}]")

    now = datetime.datetime.utcnow()
    data = {
        "desc": "Test updating",
        "now": now.isoformat(),
    }
    doc_ref.set(data)


def main(parsed):
    db = firestore.Client()
    doc_ref = db.collection(parsed.collection).document(parsed.document)

    updates = 1
    update_once(doc_ref, updates, parsed.count)

    while updates < parsed.count:
        # Uniform spread over +/- jitter
        jitter = random.uniform(-parsed.jitter, parsed.jitter)
        to_sleep = parsed.interval + jitter
        logger.info(f"Sleeping: {to_sleep:.3f}")
        time.sleep(to_sleep)
        updates += 1
        update_once(doc_ref, updates, parsed.count)


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    parser = argparse.ArgumentParser(description="Listen to changes to a document")
    parser.add_argument("--collection", default="repro_gcf_18", help="ID of collection")
    parser.add_argument("--document", default="watch_me", help="ID of document")
    parser.add_argument("--count", type=int, default=1, help="Count of updates")
    parser.add_argument("--interval", type=float, default=10.0, help="Interval (sec)")
    parser.add_argument("--jitter", type=float, default=1.0, help="Jitter (sec)")
    parsed = parser.parse_args()
    main(parsed)
