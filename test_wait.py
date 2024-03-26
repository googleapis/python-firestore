from google.cloud import firestore

# Project ID (replace with your project)
project_id = "sichenliu-nt-fs-audit"
collection_id = "cccc"

# Create a Firestore client
db = firestore.Client(
    project=project_id, 
    client_options={"api_endpoint"
    : "test-firestore.sandbox.googleapis.com"}
)

query_ref = db.collection(u'cccc')

def on_snapshot(docs, changes, read_time):
    print('in the callback')
    for doc in docs:
        print(u'{} => {}'.format(doc.id, doc.to_dict()))

# Watch this query
query_watch = query_ref.on_snapshot(on_snapshot)

# Wait
i = 0 
while i <10:
    print('wait')
    import time
    time.sleep(2)
    i += 1


