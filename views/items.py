"""
Items view: this module provides methods to interact
with items resources
"""

from models import Item as ItemModel

from flask_restful import Resource
from flask import request
import http.client as client
from utils import check_required_fields


class ItemListHandler(Resource):
    """Handler of the collection of items"""

    def get(self):
        """Retrieve every item"""
        return [o.json() for o in ItemModel.select()], client.OK

    def post(self):
        """Insert a new item"""
        request_data = request.get_json()
        check_required_fields(
            request_data=request_data,
            required_fields=['name', 'price', 'description'])

        obj = ItemModel(
            name=request_data['name'],
            price=float(request_data['price']),
            description=request_data['description'])
        obj.save()
        return obj.json(), client.CREATED


class ItemHandler(Resource):
    """Handler of a specific item"""

    def get(self, item_id):
        """Retrieve the item specified by item_id"""
        try:
            return ItemModel.select().where(
                ItemModel.id == item_id).get().json(), client.OK
        except ItemModel.DoesNotExist:
            return None, client.NOT_FOUND

    def put(self, item_id):
        """Edit the item specified by item_id"""
        try:
            obj = ItemModel.select().where(ItemModel.id == item_id).get()
        except ItemModel.DoesNotExist:
            return None, client.NOT_FOUND

        request_data = request.get_json()
        check_required_fields(
            request_data=request_data,
            required_fields=['name', 'price', 'description'])

        obj.name = request_data['name']
        obj.price = request_data['price']
        obj.description = request_data['description']
        obj.save()

        return obj.json(), client.OK

    def delete(self, item_id):
        """Remove the item specified by item_id"""
        try:
            obj = ItemModel.select().where(ItemModel.id == item_id).get()
        except ItemModel.DoesNotExist:
            return None, client.NOT_FOUND
        obj.delete_instance()
        return None, client.NO_CONTENT
