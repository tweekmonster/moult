from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django_boto.s3.storage import S3Storage

# mptt was not added to INSTALLED_APPS on purpose. It should still be picked up by moult.
# Code was taken from the package's examples.


s3 = S3Storage()


class Car(models.Model):
    photo = models.ImageField(storage=s3)


class Genre(MPTTModel):
    name = models.CharField(max_length=50, unique=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    class MPTTMeta:
        order_insertion_by = ['name']
