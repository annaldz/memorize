from django.contrib.auth.models import User
from files.models import Directory
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User)
    home_dir = models.ForeignKey('files.Directory')
