
import traceback
from app.models.orders_model import OrderBase
from app.shared_lib import utils
from app.shared_lib.mongodb import get_mongodb_service
from app.global_env import get_config

def _create_orders(order: OrderBase):
    try:
        mongodb = get_mongodb_service()
        CONFIG , TABLE = get_config()
        order_json = order.model_dump()
        print("order_json", order_json)

        # Check customer_id valid
        users_data = mongodb.find(
            collection_name=TABLE['CUSTOMER_TABLE'],
            query={"customer_id": order.customer_id},
            multiple=False)
        if not users_data:
            print("customer_id is invalid")
            return utils._response(content={'status': 'FAIL', 'messages': 'customer_id is invalid'}, status_code=400)

        province_id = order.address_delivery.province_id
        district_id = order.address_delivery.district_id
        ward_id = order.address_delivery.ward_id

        # Get province text
        province_data = mongodb.find(
            collection_name=TABLE['DICTIONARY_TABLE'],
            query={"id": province_id, "type": "address_province"},
            multiple=False)
        if not province_data:
            print("missing_province_data")
            return utils._response(content={'status': 'FAIL', 'messages': 'Something went wrong'}, status_code=400)
        
        # Get district text
        district_data = mongodb.find(
            collection_name=TABLE['DICTIONARY_TABLE'], 
            query={"id": district_id, "type": "address_district", "province_code": province_id}, 
            multiple=False)
        if not district_data:
            print("missing_district_data")
            return utils._response(content={'status': 'FAIL', 'messages': 'Something went wrong'}, status_code=400)

        # Get ward text
        ward_data = mongodb.find(
            collection_name=TABLE['DICTIONARY_TABLE'], 
            query={"id": ward_id, "type": "address_ward", "province_code": province_id, "district_code": district_id},
            multiple=False)
        if not ward_data:
            print("missing_ward_data")
            return utils._response(content={'status': 'FAIL', 'messages': 'Something went wrong'}, status_code=400)
        
        province_name = province_data.get("name_vi", {})
        district_name = district_data.get("name_vi", {})
        ward_name = ward_data.get("name_vi", {})

        full_address_name = f"{order.address_delivery.street} , {ward_name} , {district_name} , {province_name}"
        order_json['address_delivery']['full_address_name'] = full_address_name

        resp = mongodb.insert(collection_name=TABLE['ORDER_TABLE'], data=order_json)
        if not resp:
            return utils._response(content={'status': 'FAIL', 'messages': 'Something went wrong'}, status_code=400)
        
        return utils._response(content={'status': 'SUCCESS'}, status_code=200)
    except Exception as e:
        print("Exception_22", traceback.format_exc())
        raise utils._response(content={'status': 'FAIL', 'messages': 'Internal Server Error'}, status_code=500)
    

def _filter_orders(customer_id, courier_id, order_id, priority_level, product_type, status):
    try:
        mongodb = get_mongodb_service()
        CONFIG , TABLE = get_config()
        
        if not order_id and not customer_id and not order_id:
            return utils._response(content={'status': 'FAIL', 'messages': 'Missing fields required'}, status_code=400)
        
        if order_id:
            query_object = {"order_id": order_id}

        elif customer_id:
            query_object = {"customer_id": customer_id}

        else: 
            query_object = {"courier_id": courier_id}

        if priority_level:
            query_object['priority_level'] = priority_level

        if product_type:
            query_object['product_type'] = product_type

        if status:
            query_object['status'] = status

        orders_data = mongodb.find(
            collection_name=TABLE['ORDER_TABLE'],
            query=query_object,
            projection={'_id': 0},
            multiple=True)
        
        # Re-format datetime to str
        for order in orders_data:
            if 'created_at' in order or 'updated_at' in order:
                order['created_at'] = order['created_at'].strftime("%Y-%m-%d %H:%M:%S")
                order['updated_at'] = order['updated_at'].strftime("%Y-%m-%d %H:%M:%S")

        return utils._response(content={'status': 'SUCCESS', 'data': orders_data}, status_code=200)
    except Exception as e:
        print("Exception_84", traceback.format_exc())
        raise utils._response(content={'status': 'FAIL', 'messages': 'Internal Server Error'}, status_code=500)