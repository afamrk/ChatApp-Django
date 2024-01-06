from django.contrib import admin
from .models import PrivateChatRoom, PrivateChatMessage

# Register your models here.


class PrivateChatRoomAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2')


class PrivateChatMessageAdmin(admin.ModelAdmin):
    list_display = ('chat_room', 'user', 'timestamp')
    search_fields = ('chat_room__title', 'user__username')

    show_full_result_count = False


admin.site.register(PrivateChatMessage, PrivateChatMessageAdmin)
admin.site.register(PrivateChatRoom, PrivateChatRoomAdmin)
