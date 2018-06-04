# graph/urls.py
from django.urls import path

from . import views


app_name = "graph"

urlpatterns = [

    # # # # # Concern モデル # # # # #

    # 関心事の一覧
    # ex: /graph/concerns/
    path("concerns/",
        views.ConcernIndexView.as_view(),
        name="concern-index"
    ),

    # 関心事の詳細
    # ex: /graph/concerns/42/
    path("concerns/<int:pk>/",
        views.ConcernDetailView.as_view(),
        name="concern-detail"
    ),

    # 関心事の新規作成
    # ex: /graph/concerns/new/
    path("concerns/new/",
        views.ConcernCreateView.as_view(),
        name="concern-new"
    ),

    # 関心事の編集
    # ex: /graph/concerns/edit/42/
    path("concerns/edit/<int:pk>/",
        views.ConcernEditView.as_view(),
        name="concern-edit"
    ),

]