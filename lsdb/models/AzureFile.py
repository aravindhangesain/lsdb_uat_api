from django.db import models
from datetime import datetime
import hashlib

# May want to limit these to secure hashes later
# Full List:{'sha256', 'whirlpool', 'sha384', 'sha3_256', 'sha3_384',
# 'sha1', 'sha3_224', 'sha512_224', 'blake2s', 'shake_128', 'blake2b',
# 'md5-sha1', 'md4', 'ripemd160', 'sha512_256', 'sha3_512', 'sha512',
# 'md5', 'shake_256', 'sm3', 'sha224'}

algorithms_available = [
    ['md5','md5'],
    ['sha1','sha1'],
    ['sha256','sha256'],
    ['sha3_512','sha3_512'],
    ['sha512','sha512'],
]

class AzureFile(models.Model):
    file = models.FileField(blank=False, null=False)
    name = models.CharField(max_length=512, blank=True, null=True)
    uploaded_datetime = models.DateTimeField(auto_now_add=True)
    hash_algorithm = models.CharField(max_length=32, blank=False, null=False,
        default='sha256',
        choices=algorithms_available)
    hash = models.CharField(max_length=256, blank=False, null=False)
    length = models.BigIntegerField(blank=False, null=False)
    # TODO: Determine if we need this, Optional now
    blob_container = models.CharField(max_length=32, blank=True, null=True, default=None)
    expires = models.BooleanField(blank=False, null=False, default=False)

    class Meta:
        ordering = ('name',)
        unique_together = ['name','hash','blob_container']
        indexes = [
            models.Index(fields=unique_together)
        ]
    def __str__(self):
        return "{}".format(self.file.name)
# hash on upload:
# https://gist.github.com/Alir3z4/725297248a59cae05a50b15dd79fb4d0
