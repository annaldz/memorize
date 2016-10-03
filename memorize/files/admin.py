from django.contrib import admin
from .models import FileStorage, File, Directory, DirShares, FileShares

admin.site.register(FileStorage)
admin.site.register(File)
admin.site.register(Directory)
admin.site.register(DirShares)
admin.site.register(FileShares)

# Register your models here.
