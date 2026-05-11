from django.contrib import admin

from core.models import(
   Message,ClientReview, BlogPost,PropertySlider
)



admin.site.register(ClientReview)
admin.site.register(BlogPost)
admin.site.register(Message)
admin.site.register(PropertySlider)