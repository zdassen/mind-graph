from django.contrib import admin

from .models import Concern, Node


# Register your models here.
models = (Concern, Node)
for model in models:
    admin.site.register(model)