from django.contrib import admin
from . models import Product, Contact
from .models import TeamMember

admin.site.register(Product)
admin.site.register(Contact)
admin.site.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'image')