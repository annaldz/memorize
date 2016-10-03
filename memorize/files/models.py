from django.db import models
from django.contrib.auth.models import User
import hashlib
import time

# Object for physical file on disk 
class FileStorage(models.Model):
    def _createHash():
        hash = hashlib.sha1()
        salt = str(time.time() - 3947) + 'KJdjh78%^(#DDf3'
        hash.update(salt.encode('utf-8'))
        return  hash.hexdigest()[:15]

    file_hash  = models.CharField(max_length=15, default=_createHash, unique=True)
    name = models.CharField(max_length=15)
    file_type = models.CharField(max_length=25, default = 'UNKNOWN_TYPE')
    size = models.BigIntegerField()
    upload_t = models.DateTimeField()
    counter = models.IntegerField(default = 1)
    orig_owner = models.ForeignKey(User)
    is_pic=models.BooleanField(default=False)

# Logical file abstraction for given user
class File(models.Model):
    def _createDownloadHash():
        hash = hashlib.sha1()
        salt = str(time.time() + 123) + '123JJDASsd&^@7DA'
        hash.update(salt.encode('utf-8'))
        return  hash.hexdigest()[:25]

    file_id = models.ForeignKey('FileStorage')
    download_hash = models.CharField(max_length=25, default=_createDownloadHash, unique=True)
    owner = models.ForeignKey(User)
    created_t = models.DateTimeField()
    dir_id = models.ForeignKey('Directory')

# Logical directory abstration for given user
class Directory(models.Model):
    def _createDirHash():
        hash = hashlib.sha1()
        salt = str(time.time() + 123) + '123asdasd^@7DA'
        hash.update(salt.encode('utf-8'))
        return  hash.hexdigest()[:25]

    dir_name = models.CharField(max_length=150)
    parent_id = models.ForeignKey('Directory', null=True)
    hash = models.CharField(max_length=25, default=_createDirHash, unique=True)
    owner = models.ForeignKey(User)
    created_t = models.DateTimeField()
    full_path = models.CharField(max_length=150)

# Classes for sharing files
# Abstract 
class Sharing(models.Model):
    shared_with = models.ForeignKey(User)
    created_t = models.DateTimeField()

    class Meta:
        abstract = True

# Share directory class
class DirShares(Sharing):
    share_id = models.ForeignKey('Directory')

# Share file class
class FileShares(Sharing):
    share_id = models.ForeignKey('File')

    
