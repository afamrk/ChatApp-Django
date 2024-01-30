from django.contrib import admin
from .models import PrivateChatRoom, PrivateChatMessage, UnreadMessages

# Register your models here.


class PrivateChatRoomAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2')


class PrivateChatMessageAdmin(admin.ModelAdmin):
    list_display = ('chat_room', 'user', 'timestamp')
    search_fields = ('chat_room__title', 'user__username')

    show_full_result_count = False


class UnreadChatRoomMessagesAdmin(admin.ModelAdmin):
    list_display = ['room','user', 'count' ]
    search_fields = ['room__user1__username', 'room__user2__username', ]
    readonly_fields = ['id',]

    class Meta:
        model = UnreadMessages


admin.site.register(UnreadMessages, UnreadChatRoomMessagesAdmin)
admin.site.register(PrivateChatMessage, PrivateChatMessageAdmin)
admin.site.register(PrivateChatRoom, PrivateChatRoomAdmin)
