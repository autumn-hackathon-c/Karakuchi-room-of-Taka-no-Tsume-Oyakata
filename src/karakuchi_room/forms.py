from django import forms
# djangoのフォームフレームワーク全体を使うためのインポート
# HTMLの<form>をpythonで扱えるようにする
from django.contrib.auth.forms import AuthenticationForm
# Django標準の「ログイン用フォーム」クラスのAuthenticationFormをインポート
# ユーザー名とパスワード認証(ログイン)するためのフォーム

from django.contrib.auth import get_user_model
# get_user_modelをインポートすることで
# settings.pyのAUTH_USER_MODELに設定された 
# カスタムユーザーモデル を安全に参照できる
# authenticateは入力されたユーザー名とパスワードが正しいか判定する関数

from django.contrib.auth.forms import UserCreationForm
# UserCreationFormはユーザー登録用フォームをインポートしている

User = get_user_model()
# UserCreationFormをそのまま使うとエラーが出るからget_user_model()を使って
# 現在のUserモデルを取得して変数Userに入れている


# 新規登録フォーム
# これはsetting.pyでカスタムユーザーを定義しているので必要
# AUTH_USER_MODEL = "karakuchi_room.User"←これ
# これを書かないとデフォルトのユーザーモデルが使われてエラーが出る
# (karakuchi_room.User)に対して動作するようになる
class CustomUserCreationForm(UserCreationForm):
# UserCreationForm(django標準)を継承して
# 自分用にカスタマイズできるフォームにしている
    class Meta:
    # ModelForm系で使う内部クラスMetaの開始
    # ここで「どのモデルに対応させるか」「どのフィールドを使うか」を定義する
        model = User
        # get_user_model()の返り値に設定する
        # 使用するDBの表を指定している
        fields = ("user_name", "email")
        # フォームに表示したい追加フィールド
        # パスワードは自動的に追加されるから
        # ここに書く必要はないし、書くべきでもない
        # 指定するフィールド名は、実際にカスタムUserモデルで定義されている
        # フィールド名と一致している必要がある




class UserForm(forms.ModelForm):
# forms.MOdelFormはDjangoのModelFormを継承している
# ModelFormはDjangoに紐づいたフォームを簡単に作成するためのクラス
    class Meta:
    # ModelForm系で使う内部クラスMetaの開始
    # ここで「どのモデルに対応させるか」「どのフィールドを使うか」を定義する    
        model = User
        # Userはget_user_model()の返り値
        # modelのフィールド情報を参照して自動的にフォームフィールドを作る
        fields = ["user_name"]
        # フォームに含めるモデルフィールドを指定している
        # ここではuser_nameだけをフォームに表示、処理するという意味
        # models.pyに記述しているフィールド名と一致していることが条件。
        # これが一致してないとFieldErrorになる
        widgets = {
        # widgets = {}はDjangoのフォームのウィジェット
        # ウィジェット(widget)とはDjangoのフォームフィールドがHTML上でどのように
        # 表示、レンダリングされるかを制御するクラス    
            "user_name": forms.TextInput(attrs={"class": "form-control"}),
        }
        # フォームの user_name 入力欄を、HTML の <input type="text"> にする
        # Bootstrap の form-control を付けて見た目を綺麗にする

# ログインフォーム
class LoginForm(AuthenticationForm):
# AuthenticationFormを継承してLoginFormという変数に格納する      
# 継承により継承により AuthenticationForm の認証ロジック（入力値の検証・ユーザー特定など）をそのまま使いつつ、
# フィールドの見た目（widget）や追加バリデーションを上書き・拡張できる
    username = forms.CharField(
    # usernameというフォームフィールドを定義(Djangoの標準ログインフォーム)
    # forms.CharFieldは文字列入力用のフィールド
    # DjangoではHTMLの<input>としてレンダリングされる
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    # widget=は「画面に表示するときの 見た目・入力方式 を指定しますよ」という宣言
    # forms.TextInputはテキスト入力用の <input type="text"> を使ってください。とうい意味
    # attrs=はHTMLに属性を追加
    # ここではclass属性に"form-control" を付けて 
    # Bootstrap のデザインが適用されるように指示している
    # この一行があることでDjangoが自動で
    # こんな感じのHTMLを生成してくれる
    # <input type="text" class="form-control">
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )



        