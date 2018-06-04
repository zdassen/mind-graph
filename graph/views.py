from django.shortcuts import render
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
        form.instance.user = self.request.user
        return super().form_valid(form)


class ConcernCreateView(ConcernFormView, generic.CreateView):
    """関心事の新規作成"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["crud_type"] = "new"
        context["button_value"] = "新規作成"

        return context


class ConcernEditView(ConcernFormView, generic.UpdateView):
    """関心事の編集"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["crud_type"] = "edit"
        context["button_value"] = "編集"

        return context