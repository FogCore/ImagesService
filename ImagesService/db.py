from pymongo import MongoClient

mongo_client = MongoClient('mongodb://images_service:images_service_pwd@ImagesServiceDB:27017/images_service')
images_service_db = mongo_client.images_service
images_collection = images_service_db.images
