from django.core.management.base import BaseCommand
from parts.models import mongo_models
class Command(BaseCommand):
    help = 'Create MongoDB collections and insert initial data'

    def handle(self, *args, **kwargs):
        if not mongo_models.product_attribute.objects.count():


            mongo_models.product_attribute(product_code='code', tab_code='code', section_code='code', attribute_code='code').save()
            self.stdout.write(self.style.SUCCESS('PartsModel collection created in MongoDB.'))
        else:
            self.stdout.write(self.style.SUCCESS('PartsModel collection already exists in MongoDB.'))