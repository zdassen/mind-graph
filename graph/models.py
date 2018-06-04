from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class BaseModel(models.Model):
    """基本モデル"""

    # ユーザー
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    # 作成日時
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # 更新日時
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        abstract = True


class Concern(BaseModel):
    """関心事"""

    # 内容
    content = models.CharField(
        max_length=40
    )

    # 関心事のタイプ
    # 0 .. なぜなぜ分析
    # 1 .. 目標設定
    ANALYZE = 0
    SET_TARGET = 1
    NODE_TYPES = (
        (ANALYZE, "なぜなぜ分析"),
        (SET_TARGET, "目標設定")
    )
    
    concern_type = models.IntegerField(
        choices=NODE_TYPES
    )

    def __str__(self):
        return "%s" % self.content


class Node(BaseModel):
    """ノード"""

    # 関心事
    concern = models.ForeignKey(
        Concern,
        on_delete=models.CASCADE
    )

    # 自身から接続しているノード
    targets = models.ManyToManyField(
        "self",
        related_name="sources",    # 逆参照する場合の名前
        symmetrical=False,
        # null=True,    # ※ManyToManyField では不要
        blank=True
    )

    # 内容
    content = models.CharField(
        max_length=40
    )

    def __str__(self):
        return "%s" % self.content