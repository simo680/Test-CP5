import allure
import requests
import pprint
from pydantic import BaseModel, ValidationError


class Order(BaseModel):
    id: int
    petId: int
    quantity: int
    shipDate: str
    status: str
    complete: bool


class BaseRequest:
    def __init__(self, base_url):
        self.base_url = base_url

    def _request(self, url, request_type, data=None, expected_error=False):
        stop_flag = False
        while not stop_flag:
            if request_type == 'GET':
                response = requests.get(url)
            elif request_type == 'POST':
                response = requests.post(url, json=data)
            elif request_type == 'PUT':
                response = requests.put(url, json=data)
            else:
                response = requests.delete(url)

            if not expected_error and response.status_code == 200:
                stop_flag = True
            elif expected_error:
                stop_flag = True

        allure.attach(f'{request_type} example: {url}', name='Request URL',
                      attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response.status_code), name='Status Code', attachment_type=allure.attachment_type.TEXT)
        allure.attach(response.text, name='Response Data', attachment_type=allure.attachment_type.TEXT)
        return response

    def get(self, endpoint, endpoint_id, expected_error=False):
        url = f'{self.base_url}/{endpoint}/{endpoint_id}'
        response = self._request(url, 'GET', expected_error=expected_error)
        return response.json()

    def post(self, endpoint, endpoint_id, body):
        url = f'{self.base_url}/{endpoint}/{endpoint_id}'
        response = self._request(url, 'POST', data=body)
        response_data = response.json()
        return response_data.get('message', response_data)

    def delete(self, endpoint, endpoint_id):
        url = f'{self.base_url}/{endpoint}/{endpoint_id}'
        response = self._request(url, 'DELETE')
        return response.json()['message']

    def put(self, endpoint, endpoint_id, body):
        url = f'{self.base_url}/{endpoint}/{endpoint_id}'
        response = self._request(url, 'PUT', data=body)
        return response.json()


BASE_URL = 'https://petstore.swagger.io/v2'


@allure.title("Get store inventory")
def test_get_store_inventory():
    base_request = BaseRequest(BASE_URL)
    inventory = base_request.get('store', 'inventory')
    pprint.pprint(inventory)


@allure.title("Place order in store")
def test_place_order():
    base_request = BaseRequest(BASE_URL)
    data = {
        'id': 1,
        'petId': 1,
        'quantity': 1,
        'shipDate': '2023-10-07T10:00:00.000Z',
        'status': 'placed',
        'complete': False
    }
    try:
        order = Order(**data)
        new_order = base_request.post('store', 'order', body=order.dict())
        pprint.pprint(new_order)
    except ValidationError as e:
        pprint.pprint(e.errors())


@allure.title("Update order")
def test_update_order():
    base_request = BaseRequest(BASE_URL)
    data = {
        'id': 1,
        'petId': 1,
        'quantity': 2,
        'shipDate': '2023-10-08T10:00:00.000Z',
        'status': 'approved',
        'complete': True
    }
    try:
        order = Order(**data)
        updated_order = base_request.put('store', 'order/1', body=order.dict())
        if updated_order:
            pprint.pprint(updated_order)
        else:
            raise ValueError("Failed to update order.")
    except ValidationError as e:
        pprint.pprint(e.errors())


@allure.title("Delete order")
def test_delete_order():
    base_request = BaseRequest(BASE_URL)
    deleted_order = base_request.delete('store', 'order/1')
    pprint.pprint(deleted_order)
