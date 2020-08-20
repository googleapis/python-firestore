import argparse
import logging
import sys
import threading

from google.cloud import firestore_v1
from google.cloud.firestore_v1 import watch


logger = logging.getLogger("listen_document")


def main(parsed):
    callback_done = threading.Event()
    callback_done.clear()
    db = firestore_v1.Client()
    doc_ref = db.collection(parsed.collection).document(parsed.document)

    notified = 0

    def callback(doc_snapshot, changes, read_time):
        nonlocal notified

        logger.info(f"Notified: {read_time.isoformat()}")

        if len(changes) > 0:
            notified += 1
            for change in changes:
                logger.info(f"Change: {change.type:20} [{notified:6}]")
                if change.type == watch.ChangeType.REMOVED:
                    logger.info(f"Deleted")
                    callback_done.set()
    
    logger.info(f"Watching: {doc_ref.path}")
    doc_ref.on_snapshot(callback)

    logger.info("Waiting...")
    callback_done.wait()


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    parser = argparse.ArgumentParser(description="Listen to changes to a document")
    parser.add_argument("--collection", default="repro_gcf_18", help="ID of collection")
    parser.add_argument("--document", default="watch_me", help="ID of document")
    parsed = parser.parse_args()
    main(parsed)
