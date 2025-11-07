"""
get_user_modelをインポートすることで
settings.pyのAUTH_USER_MODELに設定された
カスタムユーザーモデル を安全に参照できる
"""

from django.contrib.auth import get_user_model, authenticate
from django import forms
from django.forms import inlineformset_factory
from .models import Survey, Option


from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

"""
djangoのフォームフレームワーク全体を使うためのインポート
HTMLの<form>をpythonで扱えるようにする
UserCreationFormはユーザー登録用フォームをインポートしている
Django標準の「ログイン用フォーム」クラスのAuthenticationFormをインポート
ユーザー名とパスワード認証(ログイン)するためのフォーム
"""


User = get_user_model()
"""
UserCreationFormをそのまま使うとエラーが出るからget_user_model()を使って
現在のUserモデルを取得して変数Userに入れている
新規登録フォーム
これはsetting.pyでカスタムユーザーを定義しているので必要
AUTH_USER_MODEL = "karakuchi_room.User"←これ
これを書かないとデフォルトのユーザーモデルが使われてエラーが出る
これを書く事で(karakuchi_room.User)に対して動作するようになる
"""


class CustomUserCreationForm(UserCreationForm):
    # UserCreationForm(django標準)を継承して
    # 自分用にカスタマイズできるフォームにしている

    class Meta:
        # ModelForm系で使う内部クラスMetaの開始
        # ここで「どのモデルに対応させるか」「どのフィールドを使うか」を定義する

        model = User

        """"
        # get_user_model()の返り値に設定する
        # 使用するDBの表を指定している
        """

        fields = ("user_name", "email")

        """
        # フォームに表示したい追加フィールド
        # パスワードは自動的に追加されるから
        # ここに書く必要はないし、書くべきでもない
        # 指定するフィールド名は、実際にカスタムUserモデルで定義されている
        # models.pyのフィールド名と一致している必要がある
        """


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
        # フォームに含めるモデルフィールドを指定している
        # ここではuser_nameだけをフォームに表示、処理するという意味
        # models.pyに記述しているフィールド名と一致していることが条件。
        # これが一致してないとFieldErrorになる
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
    # 継承によりAuthenticationForm の認証ロジック（入力値の検証・ユーザー特定など）をそのまま使いつつ、
    # フィールドの見た目（widget）や追加バリデーションを上書き・拡張できる

    # ここで初期化しないとDjangoがうまく動作しない
    # 初期化する事でLoginViewから渡されるrequestをフォームに保存できる
    # request→authenticate(self.request, username=email, password=password)
    # これがあるおかげでフィールドの書き換えができる

    def __init__(self, request=None, *args, **kwargs):
        # def __init__(...)はpythonの初期化関数
        # LoginFormが生成された瞬間に実行される
        # selfはクラス自身を指している(LoginForm)
        # selfを通じて、LoginFormインスタンス(実体(usernameなど))に対して設定している
        # requestは行き先が書かれたメモみたいなもの
        # request=Noneを設定する事でrequestを渡されなかった時のためのデフォルト値(None)をつけている
        # AuthenticationForm（Django 標準ログインフォーム）は、場合によっては、requestを受け取るがすべてのケースで request を渡すとは限らない。
        # form = LoginForm()←これ。requestが来なくてもフォームを作れるようにしている
        # request=Noneとすることでrequestがなくてもエラーにしないようにしている
        # args(アーグス)は位置引数をまとめて受け取る
        # 例：func(10, 20, 30)順番に渡しているので名前がないのでargs
        # argsはタプル()で渡す
        # **kwargs(クワーグス)はキーワード引数をまとめて受け取る
        # 例：func(name="shiho", age=35)名前つきで渡しているからkwargs
        # kwargsは関数側で**kwargsを使って受け取った時に辞書になる{...}
        # この２つ(argsと**kwargs)はAuthenticationForm（親クラス）が受け取る引数を そのまま渡すために必要
        # 一言で言うと継承したフォームが受け取る引数を壊さず正しく親に渡すために必要！

        self.request = request

        """
        # 受け取ったrequestをインスタンス変数として保持している
        # request を自分で保持しておく（後で authenticate に渡すため）。
        """
        super().__init__(request, *args, **kwargs)

        """
        # ここで親クラスのinitにも渡している
        # super()とは親クラス(スーパークラス)を参照するための組み込み関数
        # ここで親クラスに定義されたメソッド（ここでは__init__）を呼び出して、親クラスの初期化処理を実行させるために使う
        # まとめ
        # 呼び出し側が LoginForm(request, data=request.POST) のとき：
        # request を self.request に保存
        # super().__init__ はAuthenticationForm.__init__(request,　data=request.POST) を呼ぶ
        """

        # ここからはUIを変更している
        self.fields["username"].label = "メールアドレス"

        """
        # フォームインスタンス(self)のfieldsの辞書からusernameフィールドを取り出して、その表示ラベルをメールアドレスに変更している
        # {{ form.username.label }}とHTMLに入力するとメールアドレスと出る(UIだけを変えている)
        """

        self.fields["username"].widget.attrs.update(
            {
                #  self.fields['username'].widgetはそのフィールドがHTMLに変換される
                # .attrs(アトリブツ)はウィジェットに付与するHTML属性(辞書)を保持するプロパティ
                # .attrsに設定した内容はレンダリング時に<input...>の属性として出力される
                # .update({...})は既存の attrs 辞書に対して、指定したキーと値を追加、上書きする
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
            # user_cacheはログインしようとしているユーザーを一時的に保存じておくための変数
            # DjangoのAuthenticationForm（標準のログインフォーム）が内部で 同じ属性名(user_cache)を使っている
            # authenticate() を実行して「このユーザーは存在するか？」「パスワードは正しいか？」を確認している
            # ここでusername=emailとする事でauthenticate に渡す username 引数に email をセットしている
            # これでメールアドレスをusernameとして認証してくれる(djangoのフォーム名は固定)
            # 認証が成功したらユーザオブジェクトが返ってくる
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
            # self.はLoginFormのこと
            # confirm_login_allowedこれはDjango標準のログインフォームに定義されているメソッド
            # そのユーザーがログインしても良い状態か追加チェックするために使用される
            # これは上で認証が成功した後の追加チェックのためのもの
            """

        return self.cleaned_data


"""
        # return self.cleaned_dataはフォームに入力されたデータが、
        # バリデーションを追加した後のデータが入ってる辞書
        # これを書かないとcleaned_dataが戻らない
        # cleaned_data を Django に返して、フォームを正常終了させるための返り値
        # まとめ
        # 1.ユーザーがフォームにデータを入力して送信
        # 2.Djangoがフォームの.clean()を呼ぶ
        # 3.clean() 内で独自処理（authenticate など）を実行
        # 4.問題がなければ、self.cleaned_data を返す → フォームが「有効」になる
    """


# Django のフォームクラスを使用するために ModelForm を継承


# アンケート新規作成
class SurveyCreateForm(forms.ModelForm):
    # Metaクラスの中で、「どのモデルを使うか」「どのフィールドを操作するか」を定義
    class Meta:
        # このフォームが対応するモデルは Survey モデル
        model = Survey

        # フォームで入力／編集するフィールド
        # モデルにあるフィールドのうち、これだけをフォームに表示する
        fields = ["title", "description", "end_at", "is_public"]

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


# ✅ Surveyに紐づくOptionのフォームセットを作成
OptionFormSet = inlineformset_factory(
    parent_model=Survey,
    model=Option,
    fields=["label"],
    extra=4,  # 表示する空フォーム数
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
        choices=[(1, "公開する"), (0, "一時保存にする")],
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


# ✅ Surveyに紐づくOptionのフォームセットを作成
OptionFormSetForDraft = inlineformset_factory(
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

    class Meta:
        model = Survey
        fields = [
            "title",
            "description",
            "end_at",
        ]  # is_public はフォームに出さない等

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # フィールド自体を disabled(無効) にする。
        self.fields["title"].disabled = True
        self.fields["description"].disabled = True


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
