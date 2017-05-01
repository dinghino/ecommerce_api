"""
Testing module for Marshmallow-JSONApi implementation on Peewee Models.
Tests run with no flask involvment and are used to check validation
of inputs (post/put request data) and output from the Schemas dump method, that
will be used as return value for Flask-Restful endpoint handlers.
"""

from models import User, Order, Item
from schemas import UserSchema, OrderSchema
from uuid import uuid4
from tests.test_case import TestCase
from tests.test_utils import format_jsonapi_request, add_address
import simplejson as json

USER_TEST_DICT = {
    "first_name": "Monty",
    "last_name": "Python",
    "email": "montsdf@asdhon.org",
    "password": "ewrwer"
}


def get_expected_serialized_user(user):
    """
    From USER_TEST_DICT and a generated User, get a dict that should match
    the return value of the JSONApi serialization for that user.
    TODO: Implement expected orders/data serialization if user has orders.
    """
    # Copy and normalize the test user definition with the expected attributes
    # returned by the API
    user_data = USER_TEST_DICT.copy()
    del user_data['password']
    user_data['admin'] = user.admin

    return {
        'data': {
            'type': 'user',
            'id': str(user.user_id),
            'attributes': user_data,
            'links': {
                'self': '/users/{}'.format(user.user_id)
            },
            'relationships': {
                'orders': {
                    'data': []
                },
                'addresses': {
                    'data': []
                }
            },
        },
        'links': {
            'self': '/users/{}'.format(user.user_id)
        }
    }


class TestUserSchema(TestCase):
    def test_user_json__success(self):
        user = User.create(**USER_TEST_DICT, user_id=uuid4())
        parsed_user, errors = UserSchema.jsonapi(user)
        expected_result = get_expected_serialized_user(user)

        assert type(parsed_user) == str

        assert json.loads(parsed_user) == expected_result
        assert errors == {}

    def test_user_include_orders__success(self):
        user = User.create(**USER_TEST_DICT, user_id=uuid4())
        addr = add_address(user)
        o1 = Order.create(delivery_address=addr, user=user)
        o2 = Order.create(delivery_address=addr, user=user)

        parsed_user, errors = UserSchema.jsonapi(user, include_data=['orders'])

        parsed_user = json.loads(parsed_user)

        assert type(parsed_user['included']) == list
        assert len(parsed_user['included']) == 2
        assert parsed_user['included'][0]['id'] == str(o1.order_id)
        assert parsed_user['included'][1]['id'] == str(o2.order_id)

    def test_user_validate_input__success(self):
        post_data = format_jsonapi_request('user', USER_TEST_DICT)

        valid_user, errors = UserSchema.validate_input(post_data)

        assert valid_user is True
        assert errors == {}

    def test_user_validate_input_missing_attributes__fail(self):
        wrong_user_data = USER_TEST_DICT.copy()
        # password field is required on input
        del wrong_user_data['password']
        post_data = format_jsonapi_request('user', wrong_user_data)

        validated, errors = UserSchema.validate_input(post_data)

        assert validated is not True
        assert errors == {'errors': [{
            'detail': 'Missing data for required field.',
            'source': {'pointer': '/data/attributes/password'}
        }]}


class TestOrderSchema(TestCase):
    def test_order_json__success(self):
        user = User.create(**USER_TEST_DICT, user_id=uuid4())
        item1 = Item.create(
            item_id=uuid4(),
            name='Item 1',
            description='Item 1 description',
            price=5.24,
        )
        item2 = Item.create(
            item_id=uuid4(),
            name='Item 2',
            description='Item 2 description',
            price=8,
        )
        addr = add_address(user=user)
        order = Order.create(delivery_address=addr, user=user)
        order.add_item(item1, 2).add_item(item2, 5)

        # parsed = order.json(include_data=['items', 'user', 'delivery_address'])

        assert False
        # TODO: finish implementing the test

        assert type(parsed) == str

        expected_result = EXPECTED_ORDERS['order_json__success']
        parsed = sort_included(json.loads(parsed))
        assert parsed == expected_result

    def test_order_validate_input__success(self):
        data = {
            "relationships": {
                "user": {
                    "type": "user",
                    "id": "cfe57aa6-76c6-433d-93fe-443363978904"
                },
                "items": [
                    {
                        "type": "item",
                        "id": "25da606b-dbd3-45e1-bb23-ff1f84a5622a",
                        "quantity": 2
                    },
                    {
                        "type": "item",
                        "id": "08bd8de0-a4ac-459d-956f-cf6d8b8a7507",
                        "quantity": 2
                    }
                ],
                "delivery_address": {
                    "type": "address",
                    "id": "27e375f4-3d54-458c-91e4-d8a4fdf3b032"
                }
            }
        }
        post_data = format_jsonapi_request('order', data)
        isValid, errors = OrderSchema.validate_input(post_data)
        assert isValid is True
        assert errors == {}
