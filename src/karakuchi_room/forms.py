from django import forms
from django.forms import inlineformset_factory
from .models import Survey, Option


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
        fields = ["title", "description", "end_at"]  # is_public はフォームに出さない等

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # フィールド自体を disabled(無効) にする。
        self.fields["title"].disabled = True
        self.fields["description"].disabled = True
