from django_elasticsearch_dsl import Document, fields, Index
from parts.models import *
from elasticsearch import Elasticsearch

PUBLISHER_INDEX = Index('product')
PUBLISHER_INDEX.settings(
    number_of_shards=1,
    number_of_replicas=1,

    analysis={
        'analyzer': {
            'custom_analyzer': {
                'type': 'custom',
                'tokenizer': 'standard',
                'filter': [
                    'lowercase',
                    'edge_ngram_filter'
                ]
            }
        },
        'filter': {
            'edge_ngram_filter': {
                'type': 'edge_ngram',
                'min_gram': 3,
                'max_gram': 20,
                'token_chars': ['letter', 'digit', 'word', 'punctuation', 'sentence']
            }
        }
    }
)


@PUBLISHER_INDEX.doc_type
class ProductDocument(Document):
    id = fields.IntegerField(attr="id")
    parts_brand = fields.TextField(
        fields={
            "raw": {
                "type": "keyword"
            }
        },
        analyzer='custom_analyzer'
    )
    parts_category = fields.TextField(
        fields={
            "raw": {
                "type": "keyword"
            }
        },
        analyzer='custom_analyzer'
    )
    subcategory_name = fields.TextField(
        fields={
            "raw": {
                "type": "keyword"
            }
        }
    )
    final_price = fields.FloatField(
        fields={
            "raw": {
                "type": "keyword"
            }
        }
    )
    parts_no = fields.TextField(
        fields={
            "raw": {
                "type": "keyword"
            }
        }
    )
    parts_offer = fields.IntegerField(
        fields={
            "raw": {
                "type": "keyword"
            }
        }
    )
    parts_fits = fields.TextField(
        fields={
            "raw": {
                "type": "keyword"
            }
        }
    )
    parts_type = fields.TextField(
        fields={
            "raw": {
                "type": "keyword"
            }
        }
    )


    class Django(object):
        model = Product

    def prepare_parts_brand(self, instance):
        return instance.parts_brand.brand_name if instance.parts_brand else None

    def prepare_parts_category(self, instance):
        return instance.parts_category.category_name if instance.parts_category else None

    def prepare_subcategory_name(self, instance):
        return instance.subcategory_name if instance.subcategory_name else None

    def prepare_final_price(self, instance):
        if instance.parts_price:
            if instance.parts_offer:
                disount_amount = instance.parts_price * (instance.parts_offer / 100)
                final_price = instance.parts_price - disount_amount
            else:
                final_price = instance.parts_price
            return final_price
        return None

    def prepare_parts_no(self, instance):
        return instance.parts_no if instance.parts_no else None

    def prepare_parts_offer(self, instance):
        return instance.parts_offer if instance.parts_offer else None

    def prepare_parts_fits(self, instance):
        return instance.parts_fits if instance.parts_fits else None

    def prepare_parts_type(self, instance):
        return instance.parts_type if instance.parts_type else None

