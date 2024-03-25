# Sample code for Firestore Vector.

from time import sleep

from google.cloud import firestore
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure


# # Project ID (replace with your project)
# project_id = "sichenliu-nt-fs-audit"

# # Create a Firestore client
# db = firestore.Client(
#     project=project_id, 
#     client_options={"api_endpoint": "test-firestore.sandbox.googleapis.com"}
# )

# collection_id = "ccccccccc"

# """
# Crete the single-field index to run the vector search without a pre-filter.
# $ gcloud alpha firestore indexes composite create 
#   --collection-group="cccc"  
#   --query-scope=COLLECTION 
#   --field-config field-path=singlevectorf,vector-config='{"dimension":"1", "flat": "{}"}'   
#   --project=sichenliu-nt-fs-audit
# """
# # d = 0
# d = 600200
# for i in range(0, 5):
#     data = {
#         'name': 'John Doe',
#         'age': 30,
#         'fs': i,
#         'is_active': True,
#         'singlevectorf': Vector([
#             i + i + 7.0 + d, 
#             i+ i + 1.0 + d, 
#             i + i + 2.0 + d, 
#             i+ i + 3.0 + d, 
#             i+ i + 4.0 + d, 
#             i+ i + 9.0 + d,
#             i + 1.535325235235231235 + d, 
#             i + 2.321312321321 + d])
#     }
#     # db.collection(collection_id).document("doc_{}".format(str(i))).create(data)
#     db.collection(collection_id).document("doc_{}".format(str(i))).update(data)

# results = db.collection(collection_id).find_nearest(
#         vector_field="singlevectorf", 
#         query_vector=Vector([1.0, 2.0, 3.0, 4.9, 6.7, 7.8, 7.9, 4.0]),
#         distance_measure=DistanceMeasure.EUCLIDEAN,
#         limit=5)

# docs = results.get()

# for doc in docs:
#     print(f'{doc.id} => {doc.to_dict()}')


# """
# Crete a composite index to run the vector search with a pre-filter.
# $ gcloud alpha firestore indexes composite create 
#   --collection-group="cccc"  
#   --query-scope=COLLECTION 
#   --field-config=order=ASCENDING,field-path=fs
#   --field-config field-path=singlevectorf,vector-config='{"dimension":"1", "flat": "{}"}'   
#   --project=sichenliu-nt-fs-audit
# """

# results = db.collection(u'cccc').where('fs', '==', 1).find_nearest(
#         vector_field="singlevectorff", 
#         query_vector=Vector([1.0]),
#         distance_measure=DistanceMeasure.EUCLIDEAN,
#         limit=5)

# docs = results.get()

# for doc in docs:
#     print(f'{doc.id} => {doc.to_dict()}')

## Test the order - Regular Query

def snapshot_handler(docs, changes, read_time):
   for doc in docs:
       print(u'{} => {} at {}'.format(doc.id, doc.to_dict(), read_time))


project_id = "sichenliu-nt-fs-audit"
db = firestore.Client(project=project_id)
collection_id = "kkkklol"
db.collection(collection_id).document("doc_0").update({
    "f": [2, 2, 3, 5]
})
db.collection(collection_id).document("doc_1").update({
    "f": [1, 3, 4, 6, 7, 8]
})

# for i in range(0, 5):
#     data = {
#         "f" : [1, 2 ,3]
#     }
#     db.collection(collection_id).document("doc_{}".format(str(i))).create(data)

# For watch
# collection_ref = db.collection(collection_id)
# ret = collection_ref.order_by("f").limit(6).on_snapshot(snapshot_handler)

# print(ret)
# sleep(60)

# For regular query
# [{'f': [1, 3, 4, 6, 7, 8]}, {'f': [2, 2, 3, 5]}]

collection_ref = db.collection(collection_id)
ret = collection_ref.order_by("f").limit(6).get()

print([x.to_dict() for x  in ret])