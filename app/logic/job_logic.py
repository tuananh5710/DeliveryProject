import traceback
from datetime import datetime

from app.models.orders_model import DeliveryType, StatusOrder
from app.global_env import get_config
from app.shared_lib.mongodb import get_mongodb_service
from app.shared_lib.utils import _get_current_datetime

def scheduled_job():
    print(f"Job is running at {datetime.now()}")
    try:
        mongodb = get_mongodb_service()
        CONFIG , TABLE = get_config()
        today = _get_current_datetime(strf_time=True, datetime_format="%Y-%m-%d")
        # Query get orders delivery_schedule today
        pipeline_orders_today = [
            {
                '$match': {
                    'delivery_type': DeliveryType.SCHEDULE.value,
                    'status': StatusOrder.PROCESSING.value,
                    'delivery_schedule': today
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'order_id': 1,
                    'customer_id': 1,
                    'delivery_schedule': 1,
                    'province_id': '$address_delivery.province_id',
                    'district_id': '$address_delivery.district_id'
                }
            },
            {
                '$group': {
                    '_id': {
                        'province_id': '$province_id',
                        'district_id': '$district_id'
                    },
                    'orders': {
                        '$push': '$order_id'
                    }
                }
            }
        ]


        orders_today = list(mongodb.aggregate(collection_name=TABLE['ORDER_TABLE'], query=pipeline_orders_today))
        print("orders_today", orders_today)

        for order in orders_today:
            # Find courier match with delivery address of orders
            pipeline_find_courier = [
                {
                    '$match': {
                        'deliver_address.province_id': order.get("_id", {}).get("province_id", ""),
                        'deliver_address.district_id': order.get("_id", {}).get("district_id", ""),
                    }
                },
                {
                    '$project': {
                        '_id': 0,
                        'courier_id': 1,
                        'name': 1,
                        'age': 1,
                        'email': 1,
                        'phone': 1,
                        'date_of_birth': 1,
                        'deliver_address': 1,
                        'created_at': 1,
                        'updated_at': 1
                    }
                },
                {
                    '$limit': 1
                }
            ]
            courier_data = list(mongodb.aggregate(collection_name=TABLE['COURIER_TABLE'], query=pipeline_find_courier))
            courier_data = courier_data[0]
            # Update change status processing -> in_transit
            resp_update = mongodb.update(
                collection_name=TABLE['ORDER_TABLE'],
                query={'order_id': {'$in': order.get("orders")}},
                new_values={'$set': {'status': StatusOrder.IN_TRANSIT.value, 'courier_id': courier_data['courier_id']}, '$push': {'history_logs': {'update_time': _get_current_datetime(strf_time=True),'status': StatusOrder.IN_TRANSIT.value}}},
                multiple=True
            )
            print("resp_update", resp_update)
    except Exception as e:
        print("Exception_scheduled_job", traceback.format_exc())
        pass