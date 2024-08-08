import uuid

from django.db import models

# Create your models here.

class Manufacturer(models.Model):
    ID=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Code=models.CharField(max_length=50,unique=True,null=True,blank=True)
    Name=models.CharField(max_length=50,unique=True,null=True)
    isVehicleManufacturer=models.BooleanField(default=False)
    isProductManufacturer=models.BooleanField(default=False)
    Logo=models.URLField()

    def __str__(self):
        return self.Name

class ProductBrands(models.Model):
    ID=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    Code=models.CharField(max_length=50,unique=True,null=True,blank=True)
    Name=models.CharField(max_length=50,unique=True,null=True)
    Description=models.CharField(max_length=150,null=True,blank=True)
    Logo=models.URLField()
    Manufacturer=models.ForeignKey(Manufacturer,on_delete=models.CASCADE,null=True,blank=True)
    def __str__(self):
        return self.Name

