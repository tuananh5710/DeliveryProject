import traceback, json
from app.shared_lib import utils
from app.shared_lib.mongodb import get_mongodb_service
from app.models.resources_model import map_address_type, AddressResources
from app.global_env import get_config
import hashlib

# def _get_resources(address_resources: AddressResources):
#     try:
#         mongodb = get_mongodb_service()
#         CONFIG , TABLE = get_config()

#         address_type = address_resources.address_type
#         address_id = address_resources.address_id

#         if address_type in ['district', 'ward'] and not address_id:
#             return utils._response(content={'status': 'FAIL', 'messages': 'Missing fields required'}, status_code=400)

#         if address_type == "province":
#             query_object = {"type": map_address_type(address_type)}
#         elif address_type == "district":
#             query_object = {"type": map_address_type(address_type), "province_code": address_id}
#         else:
#             query_object={"type": map_address_type(address_type), "district_code": address_id}

#         data = mongodb.find(
#             collection_name=TABLE['DICTIONARY_TABLE'],
#             query=query_object,
#             projection={'_id': 0},
#             multiple=True)

#         return utils._response(content={'status': 'SUCCESS', 'data': data}, status_code=200)
#     except Exception as e:
#         print("Exception_84", traceback.format_exc())
#         raise utils._response(content={'status': 'FAIL', 'messages': 'Internal Server Error'}, status_code=500)

async def _get_resources(address_resources: AddressResources):
    try:
        mongodb = get_mongodb_service()
        CONFIG, TABLE = get_config()
        from app.main import redis

        print("get_resources", address_resources.model_dump())
        
        address_id = address_resources.address_id if address_resources.address_id else ''
        cache_key = f"resources:{address_resources.address_type}:{address_id}"
        hashed_key = hashlib.sha256(cache_key.encode()).hexdigest()
        print("hashed_key", hashed_key)
        cached_data = await redis.get(hashed_key)
        if cached_data:
            return utils._response(content={'status': 'SUCCESS', 'data': json.loads(cached_data)}, status_code=200)

        mongodb = get_mongodb_service()
        CONFIG, TABLE = get_config()

        address_type = address_resources.address_type
        address_id = address_resources.address_id

        if address_type in ['district', 'ward'] and not address_id:
            return utils._response(content={'status': 'FAIL', 'messages': 'Missing fields required'}, status_code=400)

        if address_type == "province":
            query_object = {"type": map_address_type(address_type)}
        elif address_type == "district":
            query_object = {"type": map_address_type(address_type), "province_code": address_id}
        else:
            query_object = {"type": map_address_type(address_type), "district_code": address_id}

        data = mongodb.find(
            collection_name=TABLE['DICTIONARY_TABLE'],
            query=query_object,
            projection={'_id': 0},
            multiple=True)

        await redis.set(hashed_key, json.dumps(data), ex=3600)

        return utils._response(content={'status': 'SUCCESS', 'data': data}, status_code=200)
    except Exception as e:
        print("Exception_84", traceback.format_exc())
        raise utils._response(content={'status': 'FAIL', 'messages': 'Internal Server Error'}, status_code=500)