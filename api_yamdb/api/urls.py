from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                       ReviewViewSet, TitleViewSet, UsersViewSet, signup_post,
                       token_post)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = 'api'

router = DefaultRouter()
router.register('users', UsersViewSet, basename='users')
router.register(r'titles', TitleViewSet)
router.register(r'genres', GenreViewSet)
router.register(r'categories', CategoryViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/auth/token/', token_post, name='token'),
    path('v1/auth/signup/', signup_post, name='signup'),
    path('v1/', include(router.urls)),
]
