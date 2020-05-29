from django.contrib import admin

from web.models import SiteUser, Board, Post

admin.site.register(SiteUser)
admin.site.register(Board)
admin.site.register(Post)
