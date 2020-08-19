import argparse
import logging
import sys

from google.cloud import firestore


logger = logging.getLogger("delete_document")


def main(parsed):
    db = firestore.Client()
    doc_ref = db.collection(parsed.collection).document(parsed.document)
    
    logger.info(f"Deleting: {doc_ref.path}")

    doc_ref.delete()


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    parser = argparse.ArgumentParser(description="Listen to changes to a document")
    parser.add_argument("--collection", default="repro_gcf_18", help="ID of collection")
    parser.add_argument("--document", default="watch_me", help="ID of document")
    parsed = parser.parse_args()
    main(parsed)
