# graph/forms.py
from django import forms

# モデルのインポート
from .models import Concern, Node


class ConcernForm(forms.ModelForm):
    """関心事の作成/編集に使用するフォームクラス"""

    class Meta:
        model = Concern
        fields = (
            "content",
            "concern_type",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content"].widget.attrs["autofocus"] = ""


class NodeEditForm(forms.ModelForm):
    """ノードの作成/編集に使用するフォームクラス"""

    class Meta:
        model = Node
        fields = (
            "concern",
            "targets",
            "content",
            "to_root",
            "node_type",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # content にフォーカスさせる
        self.fields["content"].widget.attrs["autofocus"] = ""


class NodeToRootForm(NodeEditForm):
    """ルートノードに接続するフォーム用のクラス"""

    class Meta:
        model = Node
        fields = (
            "content",
        )


class SourceNodeForm(NodeEditForm):
    """「このノードに接続する」フォーム用のフォーム"""

    class Meta:
        model = Node
        fields = (
            "content",
            "node_type",
        )


class TargetNodeForm(NodeEditForm):
    """「接続先のノードを追加」するためのフォーム"""

    class Meta:
        model = Node
        fields = (
            "content",
        )