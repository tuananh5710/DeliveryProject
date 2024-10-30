import traceback, uuid
from app.shared_lib import utils
from app.shared_lib.mongodb import get_mongodb_service
from app.models.couriers_model import CourierBase
from app.models.orders_model import Priority, UpdateOffersRequest, StatusOrder, CompleteOfferRequest
from app.shared_lib.s3_helper import get_s3_service
from app.global_env import get_config

def _check_courier_id_valid(courier_id):
    mongodb = get_mongodb_service()
    CONFIG , TABLE = get_config()
    courier_data = mongodb.find(
        collection_name=TABLE['COURIER_TABLE'],
        query={"courier_id": courier_id},
        multiple=False)
    if courier_data:
        return courier_data
    return None

def _couriers_complete_offer(complete_offer: CompleteOfferRequest):
    try:
        mongodb = get_mongodb_service()
        CONFIG , TABLE = get_config()
        
        # Check image base64 string valid
        image_base64 = complete_offer.image
        image_type = utils._is_valid_image_base64(image_base64)
        if not image_type:
            print("image is invalid")
            return utils._response(content={'status': 'FAIL', 'messages': 'image is invalid'}, status_code=400)

        # Check courier_id valid
        is_courier = _check_courier_id_valid(complete_offer.courier_id)
        if not is_courier:
            return utils._response(content={'status': 'FAIL', 'messages': 'courier_id is invalid'}, status_code=400)

        # Check order_id valid to process
        order_data = mongodb.find(
            collection_name=TABLE['ORDER_TABLE'],
            query={"order_id": complete_offer.offer_id, "status": StatusOrder.DELIVERED.value},
            multiple=False)
        print("order_data", order_data)
        if not order_data:
            print("order_id is invalid")
            return utils._response(content={'status': 'FAIL', 'messages': 'order_id is invalid'}, status_code=400)

        # Upload base64 image to s3
        path_s3 = f"OFFERS/IMAGE/{complete_offer.offer_id}"
        file_name = f"{str(uuid.uuid4())}.{image_type}"
        s3 = get_s3_service()
        resp_upload = s3.upload_base64_file(CONFIG['BUCKET_NAME'], image_base64, path_s3, file_name)
        print("resp_upload", resp_upload)
        if not len(resp_upload):
            print("Upload s3 fail")
            return utils._response(content={'status': 'FAIL', 'messages': 'Something went wrong'}, status_code=400)

        resp_update = mongodb.update(
            collection_name=TABLE['ORDER_TABLE'],
            query={'order_id': complete_offer.offer_id, 'status': StatusOrder.DELIVERED.value},
            new_values={'$set': {'image_link': resp_upload, 'status': StatusOrder.COMPLETE.value}, '$push': {'history_logs': {'update_time': utils._get_current_datetime(strf_time=True),'status': StatusOrder.COMPLETE.value}}},
            multiple=False
        )
        if not resp_update:
            print("Update database fail")
            return utils._response(content={'status': 'FAIL', 'messages': 'Something went wrong'}, status_code=400)
        
        return utils._response(content={'status': 'SUCCESS'}, status_code=200)
    except Exception as e:
        print("Exception_couriers_fetch_offer", traceback.format_exc())
        raise utils._response(content={'status': 'FAIL', 'messages': 'Internal Server Error'}, status_code=500)

def _couriers_update_offers(update_offers: UpdateOffersRequest):
    try:
        mongodb = get_mongodb_service()
        CONFIG , TABLE = get_config()
        print("list_offers", update_offers.model_dump())
        print("type", type(update_offers.model_dump()))
        length_offers = len(update_offers.list_offers)
        current_status = update_offers.current_status

        if current_status not in [StatusOrder.PROCESSING.value, StatusOrder.IN_TRANSIT.value]:
            print("current_status not allowed")
            return utils._response(content={'status': 'FAIL', 'messages': 'Something went wrong'}, status_code=400)
        
        # Check courier_id valid
        is_courier = _check_courier_id_valid(update_offers.courier_id)
        if not is_courier:
            return utils._response(content={'status': 'FAIL', 'messages': 'courier_id is invalid'}, status_code=400)

        pipeline = [
            {
                '$match': {
                    'order_id': {'$in': update_offers.list_offers},
                    'status': current_status
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'order_id': 1,
                    'customer_id': 1,
                    'priority_level': 1,
                    'created_at': 1,
                    'updated_at': 1,
                    'delivery_schedule': 1,
                    'address_delivery': 1,
                    'product_type': 1,
                    'status': 1
                }
            }
        ]
        result = list(mongodb.aggregate(collection_name=TABLE['ORDER_TABLE'], query=pipeline))
        if len(result) != length_offers:
            print("Length offers submit from front-end invalid when compare vs back-end")
            return utils._response(content={'status': 'FAIL', 'messages': 'Something went wrong'}, status_code=400)
        
        if current_status == StatusOrder.PROCESSING.value:
            next_status = StatusOrder.IN_TRANSIT.value
        elif current_status == StatusOrder.IN_TRANSIT.value:
            next_status = StatusOrder.DELIVERED.value
        
        result_update = mongodb.update(
            collection_name=TABLE['ORDER_TABLE'],
            query={'order_id': {'$in': update_offers.list_offers}},
            new_values={'$set': {'status': next_status, 'courier_id': update_offers.courier_id}, '$push': {'history_logs': {'update_time': utils._get_current_datetime(strf_time=True),'status': next_status}}},
            multiple=True
        )
        print("result_update", result_update)
        return utils._response(content={'status': 'SUCCESS', 'data': update_offers.list_offers}, status_code=200)
    except Exception as e:
        print("Exception_couriers_fetch_offer", traceback.format_exc())
        raise utils._response(content={'status': 'FAIL', 'messages': 'Internal Server Error'}, status_code=500)

def _couriers_fetch_offer(courier_id: str, page_number: int):
    try:
        mongodb = get_mongodb_service()
        CONFIG , TABLE = get_config()
        # page_number: int start from 1
        page_size = 10 # limit page_size = 10
        if page_number < 1:
            return utils._response(content={'status': 'FAIL', 'messages': 'Something went wrong'}, status_code=400)
        
        # Check courier_id valid
        courier_data = _check_courier_id_valid(courier_id)
        if not courier_data:
            return utils._response(content={'status': 'FAIL', 'messages': 'courier_id is invalid'}, status_code=400)

        deliver_province_id = courier_data.get("deliver_address", {}).get("province_id", "")
        deliver_district_id = courier_data.get("deliver_address", {}).get("district_id", "")

        # Calculate skip & limit
        skip = (page_number - 1) * page_size
        limit = page_size

        pipeline = [
            {
                '$match': {
                    'priority_level': {'$in': [Priority.IMMEDIATE.value, Priority.PRIORITY.value, Priority.STANDARD.value]},
                    'address_delivery.province_id': deliver_province_id,
                    'address_delivery.district_id': deliver_district_id
                }
            },
            {
                '$addFields': {
                    'priority': {
                        '$switch': {
                            'branches': [
                                {'case': {'$eq': ['$priority_level', Priority.IMMEDIATE.value]}, 'then': 1},
                                {'case': {'$eq': ['$priority_level', Priority.PRIORITY.value]}, 'then': 2},
                                {'case': {'$eq': ['$priority_level', Priority.STANDARD.value]}, 'then': 3}
                            ]
                        }
                    }
                }
            },
            {
                '$sort': {'priority': 1}
            },
            {
                '$group': {
                    '_id': '$priority_level',
                    'records': {'$push': '$$ROOT'},
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'priority_level': '$_id',
                    'records': {
                        '$slice': [
                            '$records',
                            {'$cond': [{'$gte': [{'$size': '$records'}, 10]}, 10, {'$size': '$records'}]}
                        ]
                    }
                }
            },
            {
                '$unwind': '$records'
            },
            {
                '$sort': {'records.priority': 1}
            },
            {
                '$project': {
                    '_id': 0,
                    'order_id': '$records.order_id',
                    'customer_id': '$records.customer_id',
                    'priority_level': '$records.priority_level',
                    'created_at': '$records.created_at',
                    'updated_at': '$records.updated_at',
                    'delivery_schedule': '$records.delivery_schedule',
                    'address_delivery': '$records.address_delivery',
                    'product_type': '$records.product_type',
                    'status': '$records.status',
                    'priority': '$records.priority'
                }
            },
            {
                '$skip': skip
            },
            {
                '$limit': limit
            }
        ]

        result = list(mongodb.aggregate(collection_name=TABLE['ORDER_TABLE'], query=pipeline))
        print("result", result)
        for item in result:
            if 'created_at' in item or 'updated_at' in item:
                item['created_at'] = item['created_at'].strftime("%Y-%m-%d %H:%M:%S")
                item['updated_at'] = item['updated_at'].strftime("%Y-%m-%d %H:%M:%S")
        return utils._response(content={'status': 'SUCCESS', 'data': result}, status_code=200)
    except Exception as e:
        print("Exception_couriers_fetch_offer", traceback.format_exc())
        raise utils._response(content={'status': 'FAIL', 'messages': 'Internal Server Error'}, status_code=500)


def _create_couriers(courier: CourierBase):
    try:
        mongodb = get_mongodb_service()
        CONFIG , TABLE = get_config()
        # Check email or phone exist
        users_data = mongodb.find(
            collection_name=TABLE['COURIER_TABLE'],
            query={
                "$or": [
                    {"email": courier.email},
                    {"phone": courier.phone}
                ]
            }, 
            multiple=True)
        if len(users_data):
            print("phone or email already exist")
            return utils._response(content={'status': 'FAIL', 'messages': 'Phone or Email currently used'}, status_code=400)

        # Check courier deliver address valid
        address_data = mongodb.find(
            collection_name=TABLE['DICTIONARY_TABLE'], 
            query={"type": "address_ward", "province_code": courier.deliver_address.province_id, "district_code": courier.deliver_address.district_id}, 
            multiple=False)
        if not address_data:
            print("invalid_deliver_address")
            return utils._response(content={'status': 'FAIL', 'messages': 'Invalid deliver address'}, status_code=400)
        
        resp_insert = mongodb.insert(collection_name=TABLE['COURIER_TABLE'], data=courier.model_dump())
        if not resp_insert:
            return utils._response(content={'status': 'FAIL', 'messages': 'Something went wrong'}, status_code=400)

        print("Create success", courier.courier_id)
        return utils._response(content={'status': 'SUCCESS'}, status_code=200)

    except Exception as e:
        print("Exception_create_couriers", traceback.format_exc())
        raise utils._response(content={'status': 'FAIL', 'messages': 'Internal Server Error'}, status_code=500)
    
