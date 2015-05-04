from django.core.management.base import BaseCommand

from boto.s3.storage import S3Storage


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        s3 = S3Storage(bucket='another-bucket', key='another-key',
                        secret='another-secret', location='EU')
        # ...
        print('Done. I guess.')
