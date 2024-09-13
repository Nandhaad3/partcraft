from djongo import models as mongo_models
from .models import *
from mongoengine import Document, fields
import uuid

class product_attribute(Document):
    product_code = fields.StringField(required=True)
    tab_code = fields.StringField(required=True)
    section_code = fields.StringField()
    attribute_code = fields.StringField(required=True)

    meta = {
        'collection': 'product_attributes',
        'db_alias': 'nonrel'
    }
    def __str__(self):
        return self.product_code

