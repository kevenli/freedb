from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
#from graphene_django.views import GraphQLView
from django.contrib.auth.decorators import login_required
from . import views
#from .schema import schema

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('db', views.DatabaseList.as_view(), name='db_list'),
    path('db/<str:database_name>', views.DatabaseIndex.as_view(),
         name='database_index'),
    path('db/<str:database_name>/<str:collection_name>',
         views.CollectionView.as_view(), name='collection_view'),
    path('db/<str:database_name>/<str:collection_name>/<str:row_id>',
         views.CollectionRowView.as_view(), name='collection_row_view'),
    path('api/databases', views.DatabaseList.as_view(), name='api_db_list'),
    path('api/databases/<str:db_name>', views.DatabaseInstance.as_view(),
         name='api_db_instance'),
    path('api/databases/<str:db_name>/collections', views.DatabaseCollectionList.as_view(),
         name='api_db_collections'),
    path('api/databases/<str:db_name>/collections/<str:col_name>', views.DatabaseCollectionInstance.as_view(),
         name='api_db_collection'),
    path('api/databases/<str:db_name>/collections/<str:col_name>/documents', views.DatabaseCollectionDocuments.as_view(),
             name='api_db_collection_docs'),


    # path('api/v1/image/upload', views.ApiUploadView.as_view(), name='ims_upload'),
    # path('api/v1/image/crop', views.ApiImageCropView.as_view()),
    # path('api/v1/image/<int:image_id>', views.ApiImageView.as_view()),
    # path('api/v1/albums', views.APIAlbumsView.as_view()),
    # path('api/v1/album/<int:album_id>', views.ApiAlbumInfo.as_view()),
    # path('image/<int:image_id>', views.ImageView.as_view(), name='ims_view_image'),
    # # path('dashboard', views.dashboard, name='ims.dashboard'),
    # path('upload', views.UploadView.as_view(), name='upload'),
    # # path('upload?aid=<int:album_id>', views.UploadView.as_view(), name='ims.upload_to_album'),
    # path('album/<int:album_id>', views.AlbumView.as_view(), name='ims.album_view'),
    # path('albums/create', views.CreateAlbumView.as_view(), name='create_album'),
    # path('albums/find.json', views.AlbumsFindJsonView.as_view(), name='find_album_json'),
    # path('albums/search', views.AlbumsSearchView.as_view(), name='ims.search_albums'),
    # path('albums', views.AlbumIndexView.as_view(), name='ims.album_list'),
    # path(r'graphql', login_required(GraphQLView.as_view(graphiql=True, schema=schema))),
    # path('', views.HomeView.as_view(), name='ims_home')
    # # path('images/<int:image_id>', views.ImageView.as_view(), name='ims_view_image')
]