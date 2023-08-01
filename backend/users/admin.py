from django.contrib import admin
from django.contrib.auth import get_user_model

from users.models import Subscription

User = get_user_model()


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "author",
        "subscriber",
    )
    list_filter = (
        "author",
        "subscriber",
    )

    class Meta:
        ordering = ["-id"]


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "email",
    )
    list_filter = (
        "username",
        "email",
    )


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
