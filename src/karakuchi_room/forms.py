"""
get_user_modelをインポートすることで
settings.pyのAUTH_USER_MODELに設定された
カスタムユーザーモデル を安全に参照できる
"""

from django.contrib.auth import get_user_model, authenticate
from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet, HiddenInput
from django.forms import ValidationError
from .models import Survey, Option, Vote, Tag


from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

"""
UserCreationFormはユーザー登録用フォームをインポートしている
Django標準の「ログイン用フォーム」クラスのAuthenticationFormをインポート
ユーザー名とパスワード認証(ログイン)するためのフォーム
"""


User = get_user_model()

"""
カスタムユーザを使用するにはget_user_modelが必要
これがないとUserCreationFormの標準ユーザを使用してしまいエラーになる
"""


class CustomUserCreationForm(UserCreationForm):
    # UserCreationForm(django標準)を継承して
    # 自分用にカスタマイズできるフォームにしている

    class Meta:
        # ModelForm系で使う内部クラスMetaの開始
        # ここで「どのモデルに対応させるか」「どのフィールドを使うか」を定義する

        model = User
        # get_user_model()の返り値に設定する
        # 使用するDBの表を指定している

        fields = ["user_name", "email"]
        # フォームに表示したい追加フィールド(user_nameはカスタムフィールド)

        widgets = {
            "user_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.TextInput(attrs={"class": "form-control"}),
        }

    # フォーム専用フィールドは以下で設定する
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ウィジェットを明示的に設定する
        self.fields["password1"].widget = forms.PasswordInput(
            attrs={"class": "form-control"}
        )
        self.fields["password2"].widget = forms.PasswordInput(
            attrs={"class": "form-control"}
        )


# この UserForm の目的は、Django の User モデル（models.pyで定義した user_name を持つユーザー）に対応したフォームを簡単に作ること
# これ→ REQUIRED_FIELDS = ["user_name"](superuser作成時追加で求められるフィールド)


class UserForm(forms.ModelForm):
    # forms.MOdelFormはDjangoのModelFormを継承している
    # ModelFormはDjangoに紐づいたフォームを簡単に作成するためのクラス

    class Meta:
        # ModelForm系で使う内部クラスMetaの開始
        # ここで「どのモデルに対応させるか」「どのフィールドを使うか」を定義する
        model = User
        """
        # Userはget_user_model()の返り値
        # modelのフィールド情報を参照して自動的にフォームフィールドを作る
        """

        fields = ["user_name"]
        """
        # models.pyに定義しているカスタムフィールドを記述
        # htmlでユーザーを表示させる時などに使用する→{{ user.user_name }}
        """

        widgets = {
            """    
        # widgets = {}はDjangoのフォームのウィジェット
        # ウィジェット(widget)とはDjangoのフォームフィールドがHTML上でどのように
        # 表示、レンダリングされるかを制御するクラス 
        """
            "user_name": forms.TextInput(attrs={"class": "form-control"}),
        }

        # フォームの user_name 入力欄を、HTML の <input type="text"> にする
        # Bootstrap の form-control を付けて見た目を綺麗にする


# ログインフォーム
# このLoginFormの目的はDjangoの標準ログインフォームAuthenticationForm をメールログイン仕様にカスタマイズしている。


class LoginForm(AuthenticationForm):
    # AuthenticationFormを継承してLoginFormという変数に格納する
    # AuthenticationFormの標準認証はusernameとpassword

    def __init__(self, request=None, *args, **kwargs):
        # フィールドを設定するために初期化

        self.request = request

        """
        # 受け取ったrequestをインスタンス変数として保持している
        # request を自分で保持しておく（後で authenticate に渡すため）。
        """
        super().__init__(request, *args, **kwargs)

        """
        受け取ったrequestを親クラス(__init__)に渡している
        """

        # ここからはUIを変更している
        self.fields["username"].label = "メールアドレス"

        """
        # フォームインスタンス(self)のfieldsの辞書からusernameフィールドを取り出して、その表示ラベルをメールアドレスに変更している
        # {{ form.username.label }}とHTMLに入力するとメールアドレスと出る(UIだけを変えている)
        """

        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control",
                # ここではclass属性に"form-control" を付けて
                # Bootstrap のデザインが適用されるように指示している
                "autocomplete": "username",
                # HTML の <input> タグには autocomplete という属性がある
                # autocompleteはブラウザは前に同じ名前の入力欄に入れた内容を記憶していて、
                # 次にフォームを表示した時に候補を自動で出したり、入力済みにしてくれる機能
                # username=emailでフィールド名は固定されている
                # なのでusernameで入力していてもブラウザで見た時はemailになる
            }
        )

        self.fields["password"].widget.attrs.update(
            {
                "class": "form-control",
                "autocomplete": "current-password",
            }
        )
        # ここまでがUIを変更している

    # ここからはフィールドの設定
    def clean(self):
        email = self.cleaned_data.get("username")

        # self.cleaned_dataはLoginFormの各フィールドにユーザーが入力した値が入っている辞書
        # usernameを取り出してemailという変数に代入している

        password = self.cleaned_data.get("password")

        if email and password:
            # emailとpasswordの両方が入力されている場合にだけ認証が進むようにしている

            self.user_cache = authenticate(
                self.request, username=email, password=password
            )

            """
            # ログイン認証
            # ここでusername=emailとする事でauthenticate に渡す username 引数に email をセットしている
    
            """

            if self.user_cache is None:
                # 認証が失敗していたら
                raise forms.ValidationError("メールアドレスが正しくありません")

            """
            # raiseとはエラーを意図的に発生させるキーワード
            # forms.ValidationErrorとはフォームの入力に問題がある時にエラーの文字列を出すコード
            # テンプレート側では{{ form.non_field_errors }}これを書く事でブラウザに表示される
            """
            self.confirm_login_allowed(self.user_cache)

            """
            # confirm_login_allowedこれはDjango標準のログインフォームに定義されているメソッド
            # そのユーザーがログインしても良い状態か追加チェックするために使用される
            # これは上で認証が成功した後の追加チェックのためのもの
            """

        return self.cleaned_data


# タグ名だけを表示するためのカスタムフィールドを作成
class TagMultipleChoiceField(forms.ModelMultipleChoiceField):
    # forms.ModelMultipleChoiceFieldはチェックボックスや複数選択のセレクトボックスで使用される
    # ここではタグを複数選択させるために使っている
    def label_from_instance(self, obj):
        # objには Tag のインスタンスが入る
        return obj.tag_name  # タグ名だけをラベルにする


# Django のフォームクラスを使用するために ModelForm を継承


# アンケート新規作成
class SurveyCreateForm(forms.ModelForm):
    # しほ：タグをチェックボックスで選択できるように追加
    tag_survey = TagMultipleChoiceField(
        queryset=Tag.objects.filter(is_deleted=False),
        # 論理削除されていないタグのみを表示
        widget=forms.SelectMultiple(
            attrs={"class": "form-select"}
        ),  # セレクトボックスで表示
        required=False,
        # requiredは入力必須かどうかを指定している
        # ここをFalseにすることでタグを選択しなくてもフォームは通る
    )

    # Metaクラスの中で、「どのモデルを使うか」「どのフィールドを操作するか」を定義
    class Meta:
        # このフォームが対応するモデルは Survey モデル
        model = Survey

        # フォームで入力／編集するフィールド
        # モデルにあるフィールドのうち、これだけをフォームに表示する
        fields = ["title", "description", "end_at", "is_public", "tag_survey"]
        # しほ：アンケート作成のUIでタグを選べるようにするためにフィールドを追加(tag_survey)

        # 各フィールドに対して使用するウィジェット（入力フォームの種類）を指定
        widgets = {
            # 「title」はテキスト入力欄にする
            # attrs={} で HTML の属性を追加
            # class="form-control" → Bootstrap用のCSS
            "title": forms.TextInput(attrs={"class": "form-control"}),
            # 「description」はテキストエリア（複数行入力）
            # Bootstrap の form-control を適用してスタイルを整える
            "description": forms.Textarea(attrs={"class": "form-control"}),
            # 「start_at」もいずれ記載する可能性あり
            # 「end_at」は日付＋時間を選択する input にする
            # type="datetime-local" → ブラウザの日時選択UIが使える
            # class="form-control" → Bootstrapスタイル
            "end_at": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            # 「is_public」はラジオボタンにする
            # (1, "公開する") = value=1, 表示ラベル「公開する」
            # (0, "一時保存する") = value=0, 表示ラベル「一時保存する」
            # choices=... で選択肢を指定
            "is_public": forms.RadioSelect(
                choices=[(1, "公開する"), (0, "一時保存する")]
            ),
        }

#. アンケート新規作成(バリデーションチェック)  
class ValidationFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        valid_count = 0

        for form in self.forms:
            if form.cleaned_data.get("DELETE", False):
                continue
            label = form.cleaned_data.get("label")
            if label:
                valid_count += 1

        if valid_count < 2:
            raise ValidationError("選択肢は2つ以上必要です。")

        if valid_count > 4:
            raise ValidationError("選択肢は最大4つまでです。")
            


# ✅ Surveyに紐づくOptionのフォームセットを作成
OptionFormSet = inlineformset_factory(
    parent_model=Survey,
    model=Option,
    formset=ValidationFormSet,
    fields=["label"],
    extra=2,  # 表示する空フォーム数
    max_num=4,
    can_delete=False,
    widgets={
        "label": forms.TextInput(
            attrs={"class": "form-control", "placeholder": "選択肢を入力"}
        )
    },
)


# アンケート編集機能(一時保存)
class SurveyFormDraft(forms.ModelForm):
    # フォームから来た値を True/False に変換する関数
    # "1" / "true" → True、それ以外 → False
    def to_bool(v):
        return str(v) in ("1", "true", "True")

    # ラジオ → True/False 変換を安全に（0/1を布教）
    is_public = forms.TypedChoiceField(
        choices=[(0, "一時保存にする"), (1, "公開する")],
        # coerce：フォームの入力値を「どんな型に変換するか」決める関数
        coerce=to_bool,
        # ラジオボタンUI
        widget=forms.RadioSelect,
    )

    # ウィジェットのフォーマットと入力フォーマットを明示
    end_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
                "class": "form-control",
            },
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M"],
    )

    class Meta:
        model = Survey
        fields = ["title", "description", "end_at", "is_public"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
        }


# DELETEフィールドを隠しフィールドに書き換え、JSで操作する
class MyInlineFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        if "DELETE" in form.fields:
            form.fields["DELETE"].widget = HiddenInput()

    def clean(self):
        super().clean()

        valid_count = 0  # 有効な選択肢の数

        for form in self.forms:
            # クリーニング前のフォームは無視
            if not hasattr(form, "cleaned_data"):
                continue

            # 削除対象ならスキップ
            if form.cleaned_data.get("DELETE", False):
                continue

            # label が空ならスキップ
            label = form.cleaned_data.get("label")
            if not label:
                continue

            valid_count += 1

        # ▼ ここからバリデーション ▼

        if valid_count < 2:
            raise ValidationError("選択肢は2つ以上必要です。")

        if valid_count > 4:
            raise ValidationError("選択肢は最大4つまでです。")


# ✅ Surveyに紐づくOptionのフォームセットを作成
OptionFormSetForDraft = inlineformset_factory(
    parent_model=Survey,
    model=Option,
    fields=["label"],
    extra=0,  # 表示する空フォーム数(編集画面のため空はなし)
    max_num=4,
    formset=MyInlineFormSet,
    can_delete=True,  # 論理削除のチェックに使う
    widgets={
        "label": forms.TextInput(
            attrs={"class": "form-control", "placeholder": "選択肢を入力"}
        )
    },
)


# アンケート編集機能(公開)
class SurveyFormPublished(forms.ModelForm):
    # ウィジェットのフォーマットと入力フォーマットを明示

    end_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
                "class": "form-control",
            },
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M"],
    )

    # チェックボックス用のフィールド（DBには直接ない仮想フィールド）
    stop_vote = forms.BooleanField(
        required=False,
        label="投票受付を停止する",
        widget=forms.CheckboxInput(
            attrs={"class": "form-check-input", "id": "stop_vote"}
        ),
    )

    class Meta:
        model = Survey
        fields = [
            "title",
            "description",
            "end_at",
        ]  # is_public はフォームに出さない等
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # フィールド自体を disabled(無効) にする。
        self.fields["title"].disabled = True
        self.fields["description"].disabled = True

        # is_open: 0=受付中, 1=受付終了
        # 既に存在していて、is_open=1（受付終了）のときだけチェックON
        if self.instance and self.instance.pk:
            self.fields["stop_vote"].initial = self.instance.is_open == 1
        else:
            # 新規作成などの場合は常にチェックOFF
            self.fields["stop_vote"].initial = False

    def save(self, commit=True):
        # まず title/description/end_at を通常どおり保存
        survey = super().save(commit=False)

        stop = self.cleaned_data.get("stop_vote", False)

        # ★ stop_vote = True → 受付終了(1)、False → 受付中(0)
        survey.is_open = 1 if stop else 0

        # ✅ デバッグ出力
        print(f"[DEBUG] stop_vote={stop} → is_open={survey.is_open}")

        if commit:
            survey.save()
        return survey


# ✅ Surveyに紐づくOptionのフォームセットを作成
OptionFormSetForPublished = inlineformset_factory(
    parent_model=Survey,
    model=Option,
    fields=["label"],
    extra=0,  # 表示する空フォーム数(編集画面のため空はなし)
    can_delete=False,
    widgets={
        "label": forms.TextInput(
            attrs={"class": "form-control", "placeholder": "選択肢を入力"}
        )
    },
)


# ✅ 投票作成機能
class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ["option", "comment"]
        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "（任意）理由やコメントがあれば入力してください",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        survey = kwargs.pop("survey", None)
        super().__init__(*args, **kwargs)
        if survey is not None:
            # このアンケートの選択肢だけ選べるように絞り込み
            self.fields["option"].queryset = Option.objects.filter(
                survey=survey,
                is_deleted=False,
            )


# ✅ 投票詳細機能
class VoteDetailForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ["option", "comment"]
        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "（任意）理由やコメントがあれば入力してください",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        survey = kwargs.pop("survey", None)
        super().__init__(*args, **kwargs)
        if survey is not None:
            # このアンケートの選択肢だけ選べるように絞り込み
            self.fields["option"].queryset = Option.objects.filter(
                survey=survey,
                is_deleted=False,
            )

        # フィールド自体を disabled(無効) にする。
        self.fields["comment"].disabled = True


# 投票編集機能
class VoteFormPublished(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ["option", "comment"]
        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "（任意）理由やコメントがあれば入力してください",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        survey = kwargs.pop("survey", None)
        super().__init__(*args, **kwargs)
        if survey is not None:
            self.fields["option"].queryset = Option.objects.filter(
                survey=survey,
                is_deleted=False,
            )
