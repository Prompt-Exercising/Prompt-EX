from django.urls import path

from .views import (
    CommunityDeleteView,
    CommunityDetailView,
    CommunityListView,
    CommunityPostView,
    FitplanListView,
    FitplanPostView,
)

urlpatterns = [
    path("", FitplanListView.as_view(), name="fitplan_list"),
    path("post", FitplanPostView.as_view(), name="fitplan_post"),
    path("community/", CommunityListView.as_view(), name="community_list"),
    path("community/post", CommunityPostView.as_view(), name="community_post"),
    path(
        "community/<int:community_id>/",
        CommunityDetailView.as_view(),
        name="community_detail",
    ),
    path(
        "community/<int:community_id>/delete",
        CommunityDeleteView.as_view(),
        name="community_delete",
    ),
]
