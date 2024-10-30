
import traceback, os
from app.shared_lib import utils
from app.shared_lib.mongodb import get_mongodb_service
from app.models.customers_model import CustomerBase
from app.global_env import get_config



def _create_users(customers: CustomerBase):
    try:
        mongodb = get_mongodb_service()
        CONFIG , TABLE = get_config()
        # Check email or phone exist
        users_data = mongodb.find(
            collection_name=TABLE["CUSTOMER_TABLE"],
            query={
                "$or": [
                    {"email": customers.email},
                    {"phone": customers.phone}
                ]
            }, 
            multiple=True)
        if len(users_data):
            print("phone or email already exist")
            return utils._response(content={'status': 'FAIL', 'messages': 'Phone or Email currently used'}, status_code=400)

        resp_insert = mongodb.insert(collection_name=TABLE['CUSTOMER_TABLE'], data=customers.model_dump())
        if not resp_insert:
            return utils._response(content={'status': 'FAIL', 'messages': 'Something went wrong'}, status_code=400)

        print("Create success", customers.customer_id)
        return utils._response(content={'status': 'SUCCESS'}, status_code=200)

    except Exception as e:
        print("Exception_22", traceback.format_exc())
        raise utils._response(content={'status': 'FAIL', 'messages': 'Internal Server Error'}, status_code=500)
    
