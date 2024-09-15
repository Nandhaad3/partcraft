# from djongo import models as mongo_models
# from .models import *
# from mongoengine import Document, fields
# import uuid
#
# class product_attribute(Document):
#     product_code = fields.StringField(required=True)
#     tab_code = fields.StringField(required=True)
#     section_code = fields.StringField()
#     attribute_code = fields.StringField(required=True)
#
#     meta = {
#         'collection': 'product_attributes',
#         'db_alias': 'nonrel'
#     }
#     def __str__(self):
#         return self.product_code
#
# class product_document(Document):
#     TYPE_CHOICE = ('Internal', 'External')
#     product_code = fields.StringField(required=True)
#     document_id = fields.StringField(required=True)
#     document_name = fields.StringField(required=True)
#     document_url = fields.StringField(required=True)
#     document_type = fields.StringField(choices=TYPE_CHOICE, required=True)
#
#     meta = {
#         'collection': 'product_documents',
#         'db_alias': 'nonrel'
#     }
#     def __str__(self):
#         return self.product_code
#
#
# class Attributes(me.Document):
#     Attributecode = me.StringField(max_length=10)
#     meta = {
#         'collection': 'attributes',
#         'db_alias': 'nonrel'
#     }
# class Sections(me.Document):
#     Sectioncode = me.StringField(max_length=10, null=True, blank=True)
#     Attributes = me.ListField(me.Document(Attribute))
#     meta = {
#         'collection': 'sections',
#         'db_alias': 'nonrel'
#     }
# class Tabs(me.Document):
#     Tabcode = me.StringField(max_length=10)
#     Sections = me.ListField(me.Document(Sections))
#     meta = {
#         'collection': 'tabs',
#         'db_alias': 'nonrel'
#     }
#
# class Products(me.Document):
#     Productcode = me.StringField(max_length=10)
#     Tabs = me.ListField(me.Document(Tabs))
#     meta = {
#         'collection': 'products',
#         'db_alias': 'nonrel'
#     }