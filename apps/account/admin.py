from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserToken, UserLocation, NewBlock, Advice, Call, Banner, Carta
from .forms import UserCreationForm, UserChangeForm
from modeltranslation.admin import TranslationAdmin


# admin.site.unregister(Group)  # "Groups" bo‘limini admin paneldan o‘chiradi


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = (
        'name', 'phone', 'created_date')
    readonly_fields = ('last_login', 'modified_date', 'created_date')
    list_filter = ('is_superuser', 'is_staff', 'is_active')
    date_hierarchy = 'created_date'
    fieldsets = (
        (None, {'fields': ('name', 'phone', 'password', 'avatar', 'user_permissions',)}),
        (_('Permissions'), {'fields': ('is_superuser', 'is_staff', 'is_active', 'groups',)}),
        (_('Important dates'), {'fields': ('last_login', 'modified_date', 'created_date')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('name', 'phone', 'password1', 'password2')}),
    )
    search_fields = ('name', 'phone')
    ordering = ('name',)
    filter_horizontal = ('user_permissions', 'groups')

@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_used', 'token', 'created_date')
    date_hierarchy = 'created_date'
    list_filter = ('is_used',)
    search_fields = ('user__phone', 'user__name', 'token')


admin.site.register(User, UserAdmin)

admin.site.index_title = _('Optom_app administration')
admin.site.site_header = _('Optom_app')


@admin.register(UserLocation)
class UserLocationAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'latitude', 'longitude', 'floor', 'apartment')
    search_fields = ('user__username', 'latitude', 'longitude')
    list_filter = ('user',)
    ordering = ('user',)


@admin.register(NewBlock)
class NewBlockAdmin(TranslationAdmin):
    list_display = ('title', 'created_date')
    search_fields = ('title', 'description')
    list_filter = ('created_date',)


@admin.register(Advice)
class AdviceAdmin(TranslationAdmin):
    list_display = ('id', 'title', 'description')
    search_fields = ('title',)


@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'telegram', 'instagram', 'tiktok', 'facebook')
    search_fields = ('phone',)


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['id', 'image']
    search_fields = ['id']


@admin.register(Carta)
class CartaAdmin(admin.ModelAdmin):
    list_display = ("user_carta_name", "bank_name", "carta_number", "bank_number")
    search_fields = ("user_carta_name", "bank_name", "carta_number")
    list_filter = ("bank_name",)
