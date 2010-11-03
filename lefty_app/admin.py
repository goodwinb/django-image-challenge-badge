from django.contrib import admin
from lefty.lefty_app.models import Badge, Challenge, ChallengeImage, Image, UserProfile, Feedback


class BadgeAdmin(admin.ModelAdmin):
    pass


class ChallengeAdmin(admin.ModelAdmin):
    pass


class ChallengeImageAdmin(admin.ModelAdmin):
    pass


class FeedbackAdmin(admin.ModelAdmin):
    pass


def approve(modeladmin, request, queryset):
    queryset.update(approved=True)
approve.short_description = "Mark images as approved"
    
    
class ImageAdmin(admin.ModelAdmin):
    # search_fields = ["title"]
    list_display = ["__unicode__", "approved", "title", "user", "tags", "challenges_",
        "thumbnail_small_", "date_created", "hot_tag",] #'tags_' 'size'
    list_filter = ["tags", "challenges", "user", "approved"]
    actions = [approve]

class UserProfileAdmin(admin.ModelAdmin):
    pass

admin.site.register(Badge, BadgeAdmin)
admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(ChallengeImage, ChallengeImageAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Feedback, FeedbackAdmin)
