from django.contrib import admin
from .models import Theme, Question, Answer, Results_details
# Register your models here.
admin.site.register(Theme)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Results_details)
