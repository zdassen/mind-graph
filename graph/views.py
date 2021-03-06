from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse

from .models import Concern, Node
from .forms import ConcernForm, NodeEditForm,\
NodeToRootForm, SourceNodeForm, TargetNodeForm


# Create your views here.
class ConcernIndexView(generic.ListView):
    """関心事一覧"""

    # 対象のモデル
    model = Concern

    # 使用するテンプレート
    template_name = "graph/concerns/concern_list.html"

    def get_queryset(self):
        
        # 新しい順にソートする
        concern_list = Concern.objects.filter(
            user=self.request.user,
        ).order_by("-created_at")

        return concern_list


class ConcernDetailView(generic.DetailView):
    """関心事の詳細"""

    # 対象のモデル
    model = Concern

    # 使用するテンプレート
    template_name = "graph/concerns/concern_detail.html"


# ※任意のフィールドにアクセスできてしまうのでダメ@180607
def get_nodes_and_links(queryset, targets_manager_name,
    *other_fields):
    """
    多対多の関係のレコードから
        ・ノード ( id、その他の内容 ) のリスト
        ・ノード間の接続情報
    を取り出す
    """

    # ID の変換用テーブルを作成する & ノード情報をまとめる
    # データベース上のレコードの ID <=> D3.js で使用する ID
    id2js = {}
    node_dicts = []
    for i, record in enumerate(queryset):

        # テーブルに ID を登録
        id2js[record.id] = i

        # レコードの ID を設定 ( D3.js 側で使用する ID )
        node_dict = {
            "id": i,
        }

        # ノード情報を追加 ( ID 以外のフィールド情報 )
        for field in other_fields:
            node_dict[field] = getattr(record, field)

        node_dicts.append(node_dict)

    # 接続情報を作成する
    # 接続情報は id2js ( 変換テーブル ) で変換した後の ID を
    # 用いるため、再度ループ走査しなおす必要がある
    links = []
    for record in queryset:

        # RelatedManager を取得する
        targets_manager = getattr(record, targets_manager_name)
        # ※クラスの確認 ( RelatedManager であることを確認 )

        for target in targets_manager.all():

            # 接続情報を追加
            links.append({

                # 接続元の ID
                "source": id2js[record.id],

                # 接続先の ID
                "target": id2js[target.id],

            })

    payload = {
        "nodes": node_dicts,
        "links": links,
    }

    return payload


def concern_detail_json(request, pk):
    """ノード一覧とノードの接続情報 (JSONデータ)"""

    concern = get_object_or_404(Concern, pk=pk)

    # 関連するノード一覧
    nodes = concern.node_set.all().order_by("created_at")

    # ノード ID <=> D3.js が使用するノード ID
    # concern 自体を 1 個目のノードとするため 1 からスタート
    id2js = {}
    for i, node in enumerate(nodes):
        id2js[node.id] = i + 1

    # ノード情報を作成 ( concern 自体)
    node_dicts = [{
        "id": 0,
        "content": concern.content,
        "is_root": True,
        "node_type": 0,
    }]

    # ノード情報を作成 ( ノード全体 )
    node_dicts += [
        {
            "id": id2js[node.id],
            "content": node.content,
            "is_root": False,
            "nid": node.id,
            "node_type": node.node_type,
        } for node in nodes
    ]

    # 接続情報を作成する
    links = []
    for node in nodes:
        if node.to_root:
            links.append({
                "source": id2js[node.id],
                "target": 0,    # ルートに接続
                "node_type": 0,
            })
        for target in node.targets.all():
            links.append({
                "source": id2js[node.id],
                "target": id2js[target.id],
                "node_type": node.node_type,
            })

    payload = {
        "nodes": node_dicts,
        "links": links,
    }

    return JsonResponse(payload)


class ConcernFormView(object):
    """関心事の新規作成/編集"""

    # 使用するフォームクラス
    form_class = ConcernForm

    # 使用するテンプレート
    template_name = "graph/concerns/concern_form.html"

    # 作成/編集成功時のリダイレクト先
    success_url = reverse_lazy("graph:concern-index")

    def form_valid(self, form):
        """フォームの値が正常な場合の処理"""
        form.instance.user = self.request.user
        return super().form_valid(form)


class ConcernCreateView(ConcernFormView, generic.CreateView):
    """関心事の新規作成"""

    def get_context_data(self, **kwargs):
        """埋め込み変数を設定する"""
        context = super().get_context_data(**kwargs)

        context["crud_type"] = "new"
        context["button_value"] = "新規作成"

        return context


class ConcernEditView(ConcernFormView, generic.UpdateView):
    """関心事の編集"""

    def get_context_data(self, **kwargs):
        """埋め込み変数を設定する"""
        context = super().get_context_data(**kwargs)

        context["crud_type"] = "edit"
        context["button_value"] = "編集"

        return context


class NodeFormView(object):
    """ノードの新規作成/編集"""

    # 対象のモデル
    model = Node

    # 使用するテンプレート
    template_name = "graph/nodes/node_form.html"

    # 作成/編集成功時のリダイレクト先
    def get_success_url(self):
        concern = self.object.concern
        return reverse_lazy("graph:concern-detail",
            kwargs={"pk": concern.id,})

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        if "node_type" in form.fields:

            # Concern の種類に応じてノードタイプを絞り込む
            ANALYZE = 0
            SET_TARGET = 1
            concern = get_object_or_404(Concern,
                pk=self.kwargs["concern_id"])
        
            # form_valid() で使用する
            self._concern = concern

            concern_type = concern.concern_type
            if concern_type == ANALYZE:
                form.fields["node_type"].choices = (
                    self.model.NODE_TYPES[0],
                    self.model.NODE_TYPES[1],
                )
            elif concern_type == SET_TARGET:
                form.fields["node_type"].choices = (
                    self.model.NODE_TYPES[2],
                    self.model.NODE_TYPES[3],
                )

        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 対象の Concern ID を埋め込む
        # URL に必ず Concern の ID が含まれるため
        # ここでまとめて ID を埋め込むことができる
        context["concern_id"] = self.kwargs["concern_id"]

        return context

    def set_user_and_concern(self, form):
        """ユーザーと関心事をフォームにセットする"""

        # ユーザーをセットする
        form.instance.user = self.request.user

        # 関心事をセットする
        form.instance.concern = get_object_or_404(
            Concern, pk=self.kwargs["concern_id"])

        return form


class NodeCreateView(NodeFormView, generic.CreateView):
    """ノードの新規作成"""

    # 入力対象のフィールド
    fields = (
        "content",
        "to_root",
    )

    def get_context_data(self, **kwargs):
        """埋め込み変数を設定する"""
        context = super().get_context_data(**kwargs)

        # POST 先の切り替えに用いる URL 名
        context["url_name"] = "node-new"

        context["button_value"] = "新規作成"

        return context

    def form_valid(self, form):
        """フォームの値が正常な場合の処理"""
        form = self.set_user_and_concern(form)

        return super().form_valid(form)


class NodeToRootCreateView(NodeFormView, generic.CreateView):
    """ノードの新規作成 ( ルートに直接接続するもの )"""

    # 使用するフォームクラス
    form_class = NodeToRootForm

    def get_context_data(self, **kwargs):
        """埋め込み変数を設定する"""
        context = super().get_context_data(**kwargs)

        # POST 先の切り替えに用いる URL 名
        context["url_name"] = "node-new-to-root"

        context["button_value"] = "新規作成"

        return context

    def form_valid(self, form):
        """フォームの値が正常な場合の処理"""
        form = self.set_user_and_concern(form)

        # 「ルートに接続する」 フラグを設定する
        form.instance.to_root = True

        return super().form_valid(form)


class NodeEditView(NodeFormView, generic.UpdateView):
    """ノードの編集"""

    # 使用するフォームクラス
    form_class = NodeEditForm

    def get_form(self):
        form = super().get_form()
        
        # 選択肢を関連するものだけに絞り込む
        # ただし、自身以外のノードであること
        form.fields["targets"].queryset = \
            self.model.objects.select_related().filter(
                user=self.request.user,
                # concern=self.object.concern    # ※クエリが一つ減る
                concern__id=self.kwargs["concern_id"]
            ).exclude(
                pk=self.kwargs["pk"]
            )

        # 接続先を選択しておく
        form.fields["targets"].initial = tuple(
            self.object.targets.values_list("id", flat=True)
        )

        return form

    def get_context_data(self, **kwargs):
        """埋め込み変数を設定する"""
        context = super().get_context_data(**kwargs)

        # POST 先の切り替えに用いる URL 名
        context["url_name"] = "node-edit"

        context["button_value"] = "編集/更新"

        # 対象のノード ID を設定する
        context["node_id"] = self.kwargs["pk"]

        return context

    def form_valid(self, form):
        """フォームの値が正常な場合の処理"""
        form = self.set_user_and_concern(form)

        return super().form_valid(form)


class SourceNodeCreateView(NodeFormView, generic.CreateView):
    """接続元ノードの作成"""

    # 使用するフォームクラス
    form_class = SourceNodeForm

    def get_context_data(self, **kwargs):
        """埋め込み変数を設定する"""
        context = super().get_context_data(**kwargs)

        # POST 先の切り替えに用いる URL 名
        context["url_name"] = "node-new-source"

        context["button_value"] = "新規作成"

        # 接続先のノード ID を設定する
        context["node_id"] = self.kwargs["target_id"]

        return context

    def form_valid(self, form):
        """フォームの値が正常な場合の処理"""
        form = self.set_user_and_concern(form)

        self.object = form.save()

        # 接続先のノードを設定する
        target = self.model.objects.get(
            pk=self.kwargs["target_id"])
        self.object.targets.add(target)

        # return super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())


class TargetNodeCreateView(NodeFormView, generic.CreateView):
    """接続先ノードの作成"""

    # 使用するフォームクラス
    form_class = TargetNodeForm

    def get_context_data(self, **kwargs):
        """埋め込み変数を設定する"""
        context = super().get_context_data(**kwargs)

        # POST 先の切り替えに用いる URL 名
        context["url_name"] = "node-new-target"

        context["button_value"] = "新規作成"

        # 接続元のノード ID を設定する
        context["node_id"] = self.kwargs["source_id"]

        return context

    def form_valid(self, form):
        """フォームの値が正常な場合の処理"""
        form = self.set_user_and_concern(form)

        # ノードを保存する
        # ( このタイミングで id が付与されるので、
        # 以降で sources.add(source) ができるようになる 
        # なぜなら、sources.add(source) とは実際には
        # source & target 列からなる中間テーブルへの
        # レコードの挿入に過ぎないからである )
        self.object = form.save()

        # 接続元のノードを追加する
        source = self.model.objects.get(
            pk=self.kwargs["source_id"]
        )
        self.object.sources.add(source)

        # ModelFormMixin の form_valid() で再度、
        #     self.object = form.save()
        # を実行してしまうので、リダイレクトだけにする
        # 
        # return super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())