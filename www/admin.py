from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Item)
admin.site.register(Department)
admin.site.register(Category)
admin.site.register(License)
admin.site.register(ItemAssignment)
admin.site.register(Profile)
admin.site.register(ItemHistory)

