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

    # # # # # Node モデル # # # # #

    # ノードの新規作成 ( 接続元にも接続先にもならないノード )
    # ex: /graph/concerns/42/nodes/new/
    path("concerns/<int:concern_id>/nodes/new/",
        views.NodeCreateView.as_view(),
        name="node-new"
    ),

    # 接続元ノードの作成
    # ex: /graph/concerns/42/nodes/42/new_source/
    path("concerns/<int:concern_id>/nodes/<int:target_id>/new_source/",
        views.SourceNodeCreateView.as_view(),
        name="node-new-source"
    ),

    # 接続先ノードの作成
    # ex: /graph/concerns/42/nodes/42/new_target/
    path("concerns/<int:concern_id>/nodes/<int:source_id>/new_target/",
        views.TargetNodeCreateView.as_view(),
        name="node-new-target"
    ),

    # ノードの編集
    # ex: /graph/concerns/42/nodes/edit/42/
    path("concerns/<int:concern_id>/nodes/edit/<int:pk>/",
        views.NodeEditView.as_view(),
        name="node-edit"
    ),

]