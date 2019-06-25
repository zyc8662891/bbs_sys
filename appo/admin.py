from django.contrib import admin

# Register your models here.
from appo.models import *

admin.site.register(User)
admin.site.register(Blog)
admin.site.register(Article)
admin.site.register(ArticleDetail)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(UpOrDown)
admin.site.register(Comment)