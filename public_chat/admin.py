from django.contrib import admin
from .models import PublicChatMessages, PublicChatRoom

# Register your models here.


class PublicChatRoomAdmin(admin.ModelAdmin):
    list_display = ('title', )


class PublicChatMessageAdmin(admin.ModelAdmin):
    list_display = ('chat_room', 'user', 'timestamp')
    search_fields = ('chat_room__title', 'user__username')

    show_full_result_count = False


admin.site.register(PublicChatMessages, PublicChatMessageAdmin)
admin.site.register(PublicChatRoom, PublicChatRoomAdmin)
