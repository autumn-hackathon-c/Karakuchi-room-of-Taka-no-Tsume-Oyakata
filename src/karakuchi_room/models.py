from django.db import models
from uuid import uuid4
from django.conf import settings
from django.utils.timezone import now
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)


# QuerySetベースの論理削除用クラス。
class SoftDeleteQuerySet(models.QuerySet):
    # bulk操作(複数レコードに対して一括で処理する操作のこと)でも物理削除せず、削除フラグを立てる
    def get_delete(self):
        return super().update(is_deleted=True, updated_at=now())

    # 通常表示用（未削除データのみ）
    def get_alive(self):
        return self.filter(is_deleted=False)

    # 削除済データのみ
    def get_dead(self):
        return self.filter(is_deleted=True)


# 「未削除データのみ」を扱うManager。
class SoftDeleteManager(models.Manager):
    # objectsを経由する通常のQueryは未削除データだけを返す
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)


#  個別オブジェクトの delete() も論理削除に差し替え 
class SoftDeleteModel(models.Model):
    objects = SoftDeleteManager()
    all_objects = SoftDeleteQuerySet.as_manager()

    def individual_delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.updated_at = now()
        self.save(update_fields=["is_deleted", "updated_at"])
        # 子も論理削除へ
        for rel in self._meta.related_objects:
            if rel.one_to_many or rel.one_to_one:
                accessor = rel.get_accessor_name()
                for obj in getattr(self, accessor).all():
                    obj.delete()  # 子の SoftDelete.delete() が呼ばれる

    class Meta:
        abstract = True


# カスタムユーザのマネージャークラス（ユーザ作成用のロジックを提供）
class UserManager(BaseUserManager):
    # 一般ユーザの作成
    def create_user(self, user_name, email, password, **extra_fields):
        if not user_name:
            raise ValueError("名前は必須です")
        if not email:
            raise ValueError("メールアドレスは必須です")
        if not password:
            raise ValueError("パスワードは必須です。")

        # Emailを正規化
        email = self.normalize_email(email)

        # 管理者権限なし(django管理画面の公式設定)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        # ユーザーインスタンスの作成
        user = self.model(
            user_name=user_name,
            email=email,
            # 追加の属性を柔軟に設定
            **extra_fields,
        )

        # パスワードのハッシュ化
        user.set_password(password)

        # ユーザーを保存
        user.save(using=self._db)

        return user

    # スーパーユーザ（管理者）の作成
    def create_superuser(self, user_name, email, password, **extra_fields):
        # ✅ 管理者権限あり
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        # ユーザーインスタンスの作成
        user = self.create_user(
            user_name=user_name,
            email=self.normalize_email(email),
            password=password,
            # 追加の属性を柔軟に設定
            **extra_fields,
        )

        return user


# Users テーブル
class User(AbstractBaseUser, PermissionsMixin, SoftDeleteModel):
    id = models.UUIDField(
        primary_key=True, default=uuid4, null=False, editable=False, verbose_name="ID"
    )

    user_name = models.CharField(max_length=50, null=False, verbose_name="名前")

    email = models.EmailField(
        max_length=255, unique=True, null=False, verbose_name="メールアドレス"
    )
    # default アプリ（Python側）

    # db_default データベース（SQL側）DBの DEFAULT 制約を付与するためにこちらが必要

    is_staff = models.BooleanField(
        default=False, db_default=False, verbose_name="管理者フラグ"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    is_deleted = models.BooleanField(
        default=False, db_default=False, verbose_name="削除フラグ"
    )

    # passwordカラムはAbstractBaseUser に含まれているので作成不要

    # ログイン時一意の識別子として使用される
    USERNAME_FIELD = "email"
    # superuser作成時追加で求められるフィールド
    REQUIRED_FIELDS = ["user_name"]

    # UserManagerを紐付ける。
    objects = UserManager()

    class Meta:
        db_table = "users"  # MySQLのテーブル名の指定
        verbose_name = "ユーザー"
        verbose_name_plural = "ユーザー一覧"
        ordering = ["id"]  # 左記を基準にしてデータを並び替える

    # インスタンスを文字列として表すためのメソッド
    def __str__(self):
        return f"名前: {self.user_name}"


# Surveysテーブル
class Survey(SoftDeleteModel):
    id = models.AutoField(primary_key=True, verbose_name="ID")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Userモデル（親）
        on_delete=models.CASCADE,  
        related_name="surveys",
        db_column="user_id",
        null=False,
        blank=False,
    )

    title = models.CharField(max_length=50, verbose_name="タイトル", null=False)

    description = models.TextField(blank=True, verbose_name="詳細")

    start_at = models.DateTimeField(null=True, blank=True, verbose_name="投票開始日時")
    end_at = models.DateTimeField(null=True, blank=True, verbose_name="投票終了日時")

    is_public = models.BooleanField(
        default=False, db_default=False, verbose_name="公開フラグ"
    )

    OPEN_STATUS = (
        (0, "受付中"),
        (1, "受付終了"),
    )
    is_open = models.PositiveSmallIntegerField(
        choices=OPEN_STATUS,
        default=0,
        db_default=0,
        verbose_name="投票フラグ",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    is_deleted = models.BooleanField(
        default=False, db_default=False, verbose_name="削除フラグ"
    )

    class Meta:
        db_table = "surveys"
        verbose_name = "アンケート"
        verbose_name_plural = "アンケート一覧"
        # 検索を速くするためにインデックス(目次)を設定
        indexes = [
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"タイトル: {self.title} (アンケートID={self.id})"


# Tagsテーブル
class Tag(SoftDeleteModel):
    id = models.AutoField(primary_key=True, verbose_name="ID")

    tag_name = models.CharField(max_length=50, verbose_name="タグ名", null=False)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    is_deleted = models.BooleanField(
        default=False, db_default=False, verbose_name="削除フラグ"
    )

    class Meta:
        db_table = "tags"
        verbose_name = "タグ"
        verbose_name_plural = "タグ一覧"
        indexes = [
            # 検索を速くするためにインデックス(目次)を設定
            models.Index(fields=["tag_name", "is_deleted"]),
        ]

    def __str__(self):
        return f"タグ名: {self.tag.tag_name}"


# Tag_Surveysテーブル
class TagSurvey(SoftDeleteModel):
    tag = models.ForeignKey(
        Tag,  # Tagモデル（親）
        on_delete=models.CASCADE,
        db_column="tag_id",
        related_name="tag_surveys",
        verbose_name="タグID",
        null=False,
        blank=False,
    )

    survey = models.ForeignKey(
        Survey,  # Surveyモデル（親）
        on_delete=models.CASCADE,
        db_column="survey_id",
        related_name="tag_surveys",
        verbose_name="アンケートID",
        null=False,
        blank=False,
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    is_deleted = models.BooleanField(
        default=False, db_default=False, verbose_name="削除フラグ"
    )

    class Meta:
        db_table = "tag_surveys"
        indexes = [models.Index(fields=["tag"]), models.Index(fields=["survey"])]

    def __str__(self):
        return f"タグ名: {self.tag.tag_name} / アンケートID: {self.survey.id}"


# Optionsテーブル
class Option(SoftDeleteModel):
    id = models.AutoField(primary_key=True, verbose_name="ID")

    survey = models.ForeignKey(
        Survey,  # Surveyモデル（親）
        on_delete=models.CASCADE,
        db_column="survey_id",
        related_name="options",
        verbose_name="アンケートID",
        null=False,
        blank=False,
    )

    label = models.CharField(
        max_length=255,
        verbose_name="選択項目",
        null=False,
        blank=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="作成日時",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新日時",
    )

    is_deleted = models.BooleanField(
        default=False,
        db_default=False,
        verbose_name="削除フラグ",
    )

    class Meta:
        db_table = "options"
        verbose_name = "選択肢"
        verbose_name_plural = "選択肢一覧"
        indexes = [
            models.Index(fields=["survey"]),
            models.Index(fields=["is_deleted"]),
        ]

    def __str__(self):
        return f"選択項目: {self.label} (アンケートID={self.survey_id})"


# Votesテーブル
class Vote(SoftDeleteModel):
    id = models.AutoField(primary_key=True, verbose_name="ID")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Userモデル（親）
        on_delete=models.CASCADE,
        db_column="user_id",
        related_name="votes",
        verbose_name="ユーザーID",
        null=False,
        blank=False,
    )

    survey = models.ForeignKey(
        Survey,  # Surveyモデル（親）
        on_delete=models.CASCADE,
        db_column="survey_id",
        related_name="votes",  # option.votes.all()
        verbose_name="アンケートID",
        null=False,
        blank=False,
    )

    option = models.ForeignKey(
        Option,  # Optionモデル（親）
        on_delete=models.CASCADE,
        db_column="option_id",
        related_name="votes",  # option.votes.all()
        verbose_name="選択ID",
        null=False,
        blank=False,
    )

    comment = models.TextField(
        verbose_name="コメント",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="作成日時",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新日時",
    )

    is_deleted = models.BooleanField(
        default=False,
        db_default=False,
        verbose_name="削除フラグ",
    )

    class Meta:
        db_table = "votes"
        verbose_name = "投票"
        verbose_name_plural = "投票一覧"

        # 同じユーザーが同じアンケートに複数票を入れられないように実装。
        constraints = [
            # アクティブ票（is_deleted=False）は user×survey で1件だけ
            models.UniqueConstraint(
                fields=["user", "survey", "is_deleted"],
                name="uq_vote_user_survey_active",
            ),
        ]

    def __str__(self):
        return (
            f"Vote(ID={self.id}, ユーザーID={self.user_id}, 選択項目={self.option_id})"
        )
