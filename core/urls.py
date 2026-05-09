from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import(
ERPProjectByTypeView,
ERPProjectSearchByNameView,
ERPProjectByLocationView,
LatestBlogPostView,
ClientReviewCreateView,
ClientReviewListView,
MessageCreateView,
MessageListAdminView,
ERPProjectViewSet,
ERPPlotViewSet
)

router = DefaultRouter()
router.register('projects', ERPProjectViewSet)
router.register('plots', ERPPlotViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('get_type_base_projects/', ERPProjectByTypeView.as_view(), name='project-by-type'),
    path('get_name_base_projects/', ERPProjectSearchByNameView.as_view(), name='project-search-by-name'),
    path("get_projects_by_locations/", ERPProjectByLocationView.as_view()),
    path('latest_blog_posts_gets/', LatestBlogPostView.as_view(), name='latest-blog-posts'),
    path('create_client_reviews/', ClientReviewCreateView.as_view(), name='client-review-create'),
    path('get_client_reviews/', ClientReviewListView.as_view(), name='client-review-list'),
    path('send_message/', MessageCreateView.as_view(), name='send-message'),
    path('get_all_messages/', MessageListAdminView.as_view(), name='admin-message-list'),

]