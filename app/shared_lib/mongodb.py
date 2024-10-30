from pymongo import MongoClient
from dependency_injector import containers, providers
import os

class MongoDBService:
    def __init__(self, client: MongoClient, db_name: str):
        self.client = client
        self.db_name = db_name

    def get_collection(self, collection_name: str):
        #Load a collection
        db = self.client[self.db_name]
        return db[collection_name]

    def insert(self, collection_name, data):
        #Insert a document or documents
        collection = self.get_collection(collection_name)
        if isinstance(data, list):
            return collection.insert_many(data).inserted_ids
        else:
            return collection.insert_one(data).inserted_id

    def find(self, collection_name, query=None, projection=None, multiple=False):
        #Fetch documents
        collection = self.get_collection(collection_name)
        if multiple:
            return list(collection.find(query, projection))
        else:
            return collection.find_one(query, projection)

    def find_one(self, collection_name, query=None, projection=None):
        # Fetch one document
        collection = self.get_collection(collection_name)
        if projection is None:
            projection = {}
        return collection.find_one(query, projection)

    def update(self, collection_name, query, new_values, multiple=False):
        #Update documents
        collection = self.get_collection(collection_name)
        if multiple:
            return collection.update_many(query, new_values, upsert=True)
        else:
            return collection.update_one(query, new_values, upsert=True)

    def delete(self, collection_name, query, multiple=False):
        # Delete documents
        collection = self.get_collection(collection_name)
        if multiple:
            return collection.delete_many(query)
        else:
            return collection.delete_one(query)

    def aggregate(self, collection_name, query):
        """Perform aggregation on a collection."""
        collection = self.get_collection(collection_name)
        return list(collection.aggregate(query, allowDiskUse=True))


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    client = providers.Singleton(MongoClient, config.connection_str)
    mongodb_service = providers.Factory(MongoDBService, client=client, db_name=config.main_db)

def get_mongodb_service():
    container = Container()
    container.config.connection_str.override(os.getenv("CONNECTION_STR"))
    container.config.main_db.override(os.getenv("MAIN_DB"))
    container.init_resources()
    return container.mongodb_service()

