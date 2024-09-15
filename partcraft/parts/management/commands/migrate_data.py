# # migrate_data.py (custom script)
# from django.db import connections
# from parts.models import ProductAttribute  # PostgreSQL models
# from parts.mongo_models import Products  # MongoDB models
#
#
# def migrate_data():
#     # Use the 'nonrel' connection for PostgreSQL
#     with connections['nonrel'].cursor() as cursor:
#         # Fetch all unique Products from PostgreSQL
#         products_pg = ProductAttribute.objects.values('productcode').distinct()
#
#         for product_pg in products_pg:
#             # Create MongoDB Product instance
#             product_mongo = Products(
#                 Productcode=product_pg['productcode'],
#                 Tabs=[]
#             )
#
#             # Fetch related Tabs for the current Product from PostgreSQL
#             tabs_pg = ProductAttribute.objects.filter(productcode=product_pg['productcode']).values('tabcode').distinct()
#
#             for tab_pg in tabs_pg:
#                 # Create MongoDB Tab instance
#                 tab_mongo = {
#                     'Tabcode': tab_pg['tabcode'],
#                     'Sections': []
#                 }
#
#                 # Fetch related Sections for the current Tab from PostgreSQL
#                 sections_pg = ProductAttribute.objects.filter(productcode=product_pg['productcode'], tabcode=tab_pg['tabcode']).values('sectioncode').distinct()
#
#                 for section_pg in sections_pg:
#                     # Create MongoDB Section instance
#                     section_mongo = {
#                         'Sectioncode': section_pg['sectioncode'],
#                         'Attributes': []
#                     }
#
#                     # Fetch related Attributes for the current Section from PostgreSQL
#                     attributes_pg = ProductAttribute.objects.filter(
#                         productcode=product_pg['productcode'],
#                         tabcode=tab_pg['tabcode'],
#                         sectioncode=section_pg['sectioncode']
#                     ).values('attributecode').distinct()
#
#                     for attribute_pg in attributes_pg:
#                         # Add Attribute to MongoDB Section
#                         section_mongo['Attributes'].append({
#                             'Attributecode': attribute_pg['attributecode']
#                         })
#
#                     # Add Section to MongoDB Tab
#                     tab_mongo['Sections'].append(section_mongo)
#
#                 # Add Tab to MongoDB Product
#                 product_mongo.Tabs.append(tab_mongo)
#
#             # Save MongoDB Product instance
#             product_mongo.save()
#
# if __name__ == '__main__':
#     migrate_data()
#
