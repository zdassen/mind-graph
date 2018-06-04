from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.urls import reverse_lazy

from .models import Concern, Node


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


class ConcernFormView(object):
    """関心事の新規作成/編集"""

    # 対象のモデル
    model = Concern

    # 入力/編集対象のフィールド
    fields = (
        "content",
        "concern_type",
    )

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


class NodeCreateView(NodeFormView, generic.CreateView):
    """ノードの詳細"""

    # 入力対象のフィールド
    fields = (
        "content",
    )

    def get_context_data(self, **kwargs):
        """埋め込み変数を設定する"""
        context = super().get_context_data(**kwargs)

        context["crud_type"] = "new"
        context["button_value"] = "新規作成"

        return context

    def form_valid(self, form):
        """フォームの値が正常な場合の処理"""
        form.instance.user = self.request.user

        # 対象の Concern を設定する
        form.instance.concern = get_object_or_404(
            Concern, pk=self.kwargs["concern_id"])

        return super().form_valid(form)


class SourceNodeCreateView(NodeFormView, generic.CreateView):
    """接続元ノードの作成"""

    # 入力対象のフィールド
    fields = (
        "targets",
        "content",
    )

    def get_form(self):
        """フォームを取得する"""
        form = super().get_form()

        # 選択肢を Concern に関するものだけにする
        form.fields["targets"].queryset = \
            self.model.objects.filter(
                user=self.request.user,
                concern__id=self.kwargs["concern_id"]
            )

        # 接続先ノードを選デフォルトで選択する
        form.fields["targets"].initial = \
            (self.kwargs["target_id"],)

        return form

    def get_context_data(self, **kwargs):
        """埋め込み変数を設定する"""
        context = super().get_context_data(**kwargs)

        context["crud_type"] = "new"
        context["button_value"] = "新規作成"

        return context

    def form_valid(self, form):
        """フォームの値が正常な場合の処理"""
        form.instance.user = self.request.user

        # 対象の Concern を設定する
        form.instance.concern = get_object_or_404(
            Concern, pk=self.kwargs["concern_id"])

        return super().form_valid(form)


class TargetNodeCreateView(NodeFormView, generic.CreateView):
    """接続先ノードの作成"""

    # 入力対象のフィールド
    fields = (
        "content",
    )

    def get_context_data(self, **kwargs):
        """埋め込み変数を設定する"""
        context = super().get_context_data(**kwargs)

        context["crud_type"] = "new"
        context["button_value"] = "新規作成"

        return context

    def form_valid(self, form):
        """フォームの値が正常な場合の処理"""
        form.instance.user = self.request.user

        # 接続元のノードを設定する
        form.instance.targets_set = self.model.objects.filter(
            user=self.request.user,
            pk=self.kwargs["source_id"]
        )

        # 対象の Concern を設定する
        form.instance.concern = get_object_or_404(
            Concern, pk=self.kwargs["concern_id"])

        return super().form_valid(form)


class NodeEditView(NodeFormView, generic.UpdateView):
    """ノードの編集"""

    # 編集対象のフィールド
    fields = (
        "concern",
        "targets",
        "content",
    )

    def get_form(self):
        form = super().get_form()

        # 接続先を選択しておく
        form.fields["targets"].initial = \
            (self.object.targets.values)
        #
        # ※ここが途中
        #

        return form

    def get_context_data(self, **kwargs):
        """埋め込み変数を設定する"""
        context = super().get_context_data(**kwargs)

        context["crud_type"] = "edit"
        context["button_value"] = "編集/更新"

        return context