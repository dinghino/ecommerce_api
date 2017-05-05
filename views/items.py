"""
Items view: this module provides methods to interact
with items resources
"""

import uuid

from flask import request
from flask_restful import Resource
import http.client as client

from models import Item

from utils import generate_response


class ItemsHandler(Resource):
    """Handler of the collection of items"""

    def get(self):
        """Retrieve every item"""
        data = Item.json_list(Item.get_all())
        return generate_response(data, client.OK)

    def post(self):
        """
        Insert a new item, the item_id identifier is forwarded
        from the one generated from the database
        """
        request_data = request.get_json()

        errors = Item.validate_input(request_data)
        if errors:
            return errors, client.BAD_REQUEST

        data = request_data['data']['attributes']

        if int(data['availability']) < 0:
            return None, client.BAD_REQUEST

        item = Item.create(
            item_id=uuid.uuid4(),
            name=data['name'],
            price=float(data['price']),
            description=data['description'],
            availability=int(data['availability']),
        )

        return generate_response(item.json(), client.CREATED)


class ItemHandler(Resource):
    """Handler of a specific item"""

    def get(self, item_id):
        """Retrieve the item specified by item_id"""
        try:
            item = Item.get(Item.item_id == item_id)
            return generate_response(item.json(), client.OK)
        except Item.DoesNotExist:
            return None, client.NOT_FOUND

    def patch(self, item_id):
        """Edit the item specified by item_id"""
        try:
            obj = Item.get(Item.item_id == item_id)
        except Item.DoesNotExist:
            return None, client.NOT_FOUND

        request_data = request.get_json()

        errors = Item.validate_input(request_data, partial=True)
        if errors:
            return errors, client.BAD_REQUEST

        data = request_data['data']['attributes']

        name = data.get('name')
        price = data.get('price')
        description = data.get('description')
        availability = data.get('availability')

        if name:
            obj.name = name

        if price:
            obj.price = price

        if description:
            obj.description = description

        if availability:
            obj.availability = availability

        obj.save()

        return generate_response(obj.json(), client.OK)

    def delete(self, item_id):
        """Remove the item specified by item_id"""
        try:
            item = Item.get(Item.item_id == item_id)
        except Item.DoesNotExist:
            return None, client.NOT_FOUND

        item.delete_instance()
        return None, client.NO_CONTENT
