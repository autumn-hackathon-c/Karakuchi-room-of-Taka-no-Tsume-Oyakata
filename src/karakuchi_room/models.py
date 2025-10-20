from django.db import models
from uuid import uuid4
from django.conf import settings
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)

# カスタムユーザのマネージャークラス（ユーザ作成用のロジックを提供）
class UserManager(BaseUserManager):
    # 一般ユーザの作成
    def create_user(self, user_name, email_address, password, **extra_fields  ):
        if not user_name:
            raise ValueError("名前は必須です")
        if not email_address:
            raise ValueError("メールアドレスは必須です")
        if not password:
            raise ValueError("パスワードは必須です。")
        
        # Emailを正規化
        email_address=self.normalize_email(email_address)

        # ユーザインスタンスの作成
        user = self.model(
            user_name=user_name,
            email_address=email_address,
            #追加の属性を柔軟に設定
             **extra_fields  
        )
        
        # パスワードのハッシュ化
        user.set_password(password)
        
        # ユーザーを保存
        user.save(using=self._db)
        
        return user

    # スーパーユーザ（管理者）の作成
    def create_superuser(self, user_name, email_address, password,**extra_fields):
        
        # ユーザインスタンスの作成
        user = self.create_superuser(
            user_name=user_name,
            email_address=self.normalize_email(email_address),
            password=password,
            #追加の属性を柔軟に設定
             **extra_fields  
        )

        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

#Users テーブル
class User(AbstractBaseUser, PermissionsMixin):


    id = models.UUIDField(
        primary_key=True, 
        default=uuid4, 
        null=False,
        editable=False, 
        verbose_name="ID"
    )

    user_name = models.CharField(
        max_length=50,
        null=False,
        verbose_name="名前"
    )

    email_address = models.EmailField(
        max_length=255,
        unique=True,
        null=False,
        verbose_name="メールアドレス"
    )

    is_admin = models.BooleanField(
        default=False,
        verbose_name="管理者フラグ"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="作成日時"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新日時"
    )

    is_deleted = models.BooleanField(
        default=False,
        verbose_name="削除フラグ"
    )
    
    #passwordカラムはAbstractBaseUser に含まれているので作成不要
    
    # ログイン時一意の識別子として使用される
    USERNAME_FIELD = "email_address"
    # superuser作成時追加で求められるフィールド
    REQUIRED_FIELDS = ["user_name"]
    
    #UserManagerを紐付ける。
    objects = UserManager()

    class Meta:
        db_table = "users" # MySQLのテーブル名の指定
        verbose_name = "ユーザー"
        verbose_name_plural = "ユーザー一覧"
        ordering = ["id"]  # 左記を基準にしてデータを並び替える

    def __str__(self):
        return self.user_name
    

#Surveysテーブル
class Survey(models.Model):
    """
    Users(親) : Post(子) = 1 : N
    親は settings.AUTH_USER_MODEL（= users テーブル）を参照
    """
    id = models.AutoField(
        primary_key=True,
        verbose_name="ID"
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,     # ← 親ユーザー削除を禁止（論理削除に合わせる）
        related_name="surveys",  # user.posts で辿れる
        db_column="user_id" ,    # 物理列名を user_id に固定
        null = False
    )

    title = models.CharField(
        max_length=50,
        verbose_name="タイトル",
        null = False
    )
    
    description = models.TextField(
        blank=True, 
        verbose_name="詳細"
    )

    start_at = models.DateTimeField(
        null=True,
        blank=True, 
        verbose_name="投票開始日時"
    )
    end_at = models.DateTimeField(
        null=True, 
        blank=True, 
        verbose_name="投票終了日時"
    )

    is_public = models.BooleanField(
        default=False, 
        verbose_name="公開フラグ"
    )

    OPEN_STATUS = (
        (0, "受付中"),
        (1, "受付終了"),
    )
    is_open = models.PositiveSmallIntegerField(
        choices=OPEN_STATUS,
        default=0,
        verbose_name="投票フラグ",
    )

    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="作成日時"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="更新日時"
    )
    is_deleted = models.BooleanField(
        default=False, 
        verbose_name="削除フラグ"
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
        return f"{self.title} (id={self.id})"

    


