from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect

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

        self.object = form.save()

        # 接続先のノードを設定する
        target = self.model.objects.get(
            pk=self.kwargs["target_id"])
        self.object.targets.add(target)

        # return super().form_valid(form)
        return HttpResponseRedirect(self.get_success_url())


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

        # 対象の Concern を設定する
        form.instance.concern = get_object_or_404(
            Concern, pk=self.kwargs["concern_id"]
        )

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

        context["crud_type"] = "edit"
        context["button_value"] = "編集/更新"

        return context