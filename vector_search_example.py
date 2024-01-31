# Sample code for Firestore Vector.

from google.cloud import firestore
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure


# Project ID (replace with your project)
project_id = "sichenliu-nt-fs-audit"

# Create a Firestore client
db = firestore.Client(
    project=project_id, 
    client_options={"api_endpoint": "test-firestore.sandbox.googleapis.com"}
)

"""
Crete the single-field index before runing the vector search.
$ gcloud alpha firestore indexes composite create 
  --collection-group="cccc"  
  --query-scope=COLLECTION 
  --field-config field-path=singlevectorf,vector-config='{"dimension":"1", "flat": "{}"}'   
  --project=sichenliu-nt-fs-audit
"""

for i in range(0, 5):
    data = {
        'name': 'John Doe',
        'age': 30,
        'fs': i,
        'is_active': True,
        'singlevectorf': Vector([i + 1.0])
    }
    db.collection(u'cccc').add(data)

results = db.collection(u'cccc').find_nearest(
        vector_field="singlevectorf", 
        query_vector=Vector([1.0]),
        distance_measure=DistanceMeasure.EUCLIDEAN,
        limit=5)

docs = results.get()

for doc in docs:
    print(f'{doc.id} => {doc.to_dict()}')


"""
Crete the single-field index before runing the vector search.
$ gcloud alpha firestore indexes composite create 
  --collection-group="cccc"  
  --query-scope=COLLECTION 
  --field-config=order=ASCENDING,field-path=fs
  --field-config field-path=singlevectorf,vector-config='{"dimension":"1", "flat": "{}"}'   
  --project=sichenliu-nt-fs-audit
"""

results = db.collection(u'cccc').where('fs', '==', 1).find_nearest(
        vector_field="singlevectorf", 
        query_vector=Vector([1.0]),
        distance_measure=DistanceMeasure.EUCLIDEAN,
        limit=5)

docs = results.get()

for doc in docs:
    print(f'{doc.id} => {doc.to_dict()}')