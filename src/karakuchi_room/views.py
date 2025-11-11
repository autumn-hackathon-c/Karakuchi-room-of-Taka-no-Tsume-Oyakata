from django.views.generic import ListView, DetailView, CreateView, UpdateView
# 会員登録する」ためにCreateViewが必要
# CREATEVIEWは汎用的なビューだからdjango.views.genericの中のCreateViewになる
# ここはトイトイさんとコンフリクト起こすかも

from django.contrib.auth.views import LoginView
# LoginViewをインポートする事でテンプレート名や
# リダイレクト先を指定するだけでログイン画面を作成できる
# django.contrib.auth.viewは認証用ビュー群


from django.contrib.auth.mixins import LoginRequiredMixin
# 裏側のロジック(view)でコントロールする
# ログインしているユーザーだけにアクセスを許可する


from django.urls import reverse_lazy
# reverse_lazyをインポートすることでリダイレクト先を指定できる

from .forms import CustomUserCreationForm, LoginForm
# 同じアプリケーション内のforms.pyからCustomUserFormとLoginFormをインポート

# from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect

from .forms import (
    SurveyCreateForm,
    OptionFormSet,
    SurveyFormDraft,
    OptionFormSetForDraft,
    SurveyFormPublished,
    OptionFormSetForPublished,
    VoteForm,
    VoteDetailForm,
    VoteFormPublished,
)
from django.utils import timezone
from django.db import transaction
from karakuchi_room.models import Survey, Vote
from django.contrib.auth import get_user_model
from django.contrib import messages
import logging

from django.db.models import Count, Exists, OuterRef, Q

"""
Count    : レコードの件数を数える
Exists   : サブクエリで「該当するレコードが存在するか」を調べる
OuterRef : サブクエリの中で外側のクエリ（親クエリ）の値を参照する
Q        : 複雑な条件を OR / AND / NOT で組み合わせる
"""


# 新規登録
class SignUpView(CreateView):
    template_name = "karakuchi_room/signup.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")


# ログイン
class MyLoginView(LoginView):
    template_name = "karakuchi_room/login.html"
    redirect_authenticated_user = True
    form_class = LoginForm


# ログ出力するために記載
logger = logging.getLogger(__name__)


# アンケート一覧画面
class SurveyListView(LoginRequiredMixin, ListView):
    model = Survey
    template_name = "karakuchi_room/surveys.html"

    def get_queryset(self):
        # 現在ログイン中のユーザーを取得
        current_user = self.request.user

        # ベース条件：削除されていないもの
        base_survey = Survey.objects.filter(is_deleted=False)

        # 公開アンケート or 自分が作ったアンケート（下書き含む）
        surveys_with_vote_status = base_survey.filter(
            Q(is_public=True) | Q(user=current_user)
        )

        # 各アンケートに「このユーザーが既に投票しているか」をフラグとして付与する
        surveys_with_vote_status = surveys_with_vote_status.annotate(
            has_voted=Exists(
                Vote.objects.filter(
                    survey=OuterRef("pk"),  # 対象のアンケートに対応する投票
                    user=current_user,  # 現在のログインユーザーによる投票
                    is_deleted=False,  # 有効な投票のみ対象
                )
            )
        )

        # 投票状況付きのアンケート一覧を新しい順で返す
        return surveys_with_vote_status.order_by("-id")


# アンケート詳細画面
class SurveyDetailView(LoginRequiredMixin, DetailView):
    model = Survey
    template_name = "karakuchi_room/surveys_detail.html"

    # 以下、選択項目を表示させるための設定
    ## テンプレート変数名を指定
    context_object_name = "survey"

    ## アンケートに紐づく選択肢（Option)や投票(Votes)を取得する。
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # この詳細ページのアンケート
        survey = self.object
        user = self.request.user

        # 選択肢（Option）一覧はそのまま
        ctx["option_list"] = self.object.options.filter(is_deleted=False)

        # 投票（Vote）をテンプレに渡す（未ログインなら None）
        user_vote = None
        if user.is_authenticated:
            # 未ログインなら None のまま
            user_vote = Vote.objects.filter(
                survey=survey, user=user, is_deleted=False
            ).first()

        ctx["vote"] = user_vote  # ← これまでの ctx["vote"] と同じ意味

        # これまでのコメント一覧（このアンケートの全投票）
        ctx["vote_list"] = (
            Vote.objects.filter(survey=survey, is_deleted=False)
            .select_related("user", "option")
            .order_by("-created_at")
        )

        # 選択項目ごとの票数（このアンケート内）
        ctx["option_vote_counts"] = (
            Vote.objects.filter(survey=survey, is_deleted=False)
            .values("option__id", "option__label")
            .annotate(vote_count=Count("id"))
            .order_by("option__id")
        )

        return ctx


# ゲストユーザー（ログイン機能ができるまで暫定的に記載）
def get_guest_user():
    User = get_user_model()
    guest, _ = User.objects.get_or_create(
        username="guest",
        defaults={"email": "guest@example.com", "is_active": True},
    )
    return guest


# アンケート新規作成
class SurveyCreateView(LoginRequiredMixin, CreateView):
    model = Survey
    # ModelForm を使う
    form_class = SurveyCreateForm
    template_name = "karakuchi_room/surveys_create.html"
    success_url = None

    # SurveyフォームとOptionフォームセットをテンプレートに渡す
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx["formset"] = OptionFormSet(self.request.POST)
        else:
            ctx["formset"] = OptionFormSet()
        return ctx

    # SurveyとOptionをまとめて保存
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():  # どちらか失敗すればロールバック
                survey = form.save(commit=False)
                user = (
                    self.request.user
                    if self.request.user.is_authenticated
                    else get_guest_user()
                )
                survey.user = user
                survey.save()
                formset.instance = survey  # Option の親を設定
                formset.save()

            messages.success(self.request, "アンケートを作成しました。")
            return redirect("survey-list")

        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "入力内容にエラーがあります。")
        return super().form_invalid(form)


# アンケート編集画面(一時保存)
class SurveyTemporaryUpdateView(LoginRequiredMixin, UpdateView):
    model = Survey
    form_class = SurveyFormDraft
    template_name = "karakuchi_room/surveys_edit_save_temporary.html"

    # 下書きだけを対象にする（公開済みは404）
    def get_queryset(self):
        return Survey.objects.filter(is_public=False)

    def get_success_url(self):
        return reverse_lazy("survey-detail", kwargs={"pk": self.object.pk})

    # SurveyフォームとOptionフォームセットをテンプレートに渡す
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        formset = OptionFormSetForDraft(self.request.POST or None, instance=self.object)
        ctx["formset"] = formset
        return ctx

    # 公開済みは常に公開のままに固定するなら明示しておく
    def form_valid(self, form):
        ctx = self.get_context_data()
        formset = ctx["formset"]

        # form はすでに valid。formset だけ検証すればOK
        if not formset.is_valid():
            return self.form_invalid(form)

        with transaction.atomic():  # どちらか失敗すればロールバック
            # UpdateView: 既存 self.object を更新
            self.object = form.save(commit=False)
            # フォームから is_public の値を反映（ラジオで公開に切り替え可能にするため）
            self.object.is_public = bool(form.cleaned_data.get("is_public", False))
            # user は上書きしない（作成者そのまま）
            self.object.save()
            formset.instance = self.object
            formset.save()

            messages.success(self.request, "アンケートを作成しました。")
            return redirect("survey-detail", pk=self.object.pk)


# アンケート編集画面(公開済)
class SurveyUpdateView(LoginRequiredMixin, UpdateView):
    model = Survey
    form_class = SurveyFormPublished
    template_name = "karakuchi_room/surveys_edit_published.html"

    # 公開済みだけを対象にする（下書きは404）
    def get_queryset(self):
        return Survey.objects.filter(is_public=True)

    def get_success_url(self):
        return reverse_lazy("survey-detail", kwargs={"pk": self.object.pk})

    # SurveyフォームとOptionフォームセットをテンプレートに渡す
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        formset = OptionFormSetForPublished(
            self.request.POST or None,
            instance=self.object,
        )
        for f in formset.forms:
            f.fields["label"].disabled = True  # ← 選択項目の編集：無効化
        ctx["formset"] = formset
        return ctx

    # 公開済みは常に公開のままに固定するなら明示しておく
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]

        # form はすでに valid。formset だけ検証すればOK
        if not formset.is_valid():
            return self.form_invalid(form)

        with transaction.atomic():  # どちらか失敗すればロールバック
            survey = form.save(commit=False)
            user = (
                self.request.user
                if self.request.user.is_authenticated
                else get_guest_user()
            )
            survey.user = user
            survey.save()
            formset.instance = survey  # Option の親を設定
            formset.save()

            messages.success(self.request, "アンケートを作成しました。")
            return redirect("survey-detail", pk=self.object.pk)


# アンケート削除(DeleteViewは別途削除用のページが必要なので、今回は別の方法で実装)
def survey_delete(request, pk):
    survey = get_object_or_404(Survey, pk=pk)
    # ソフトデリートではなく「物理削除」にする
    """
    物理削除にした理由
    
    ソフトデリートだと以下のパターンでエラーが出るから
    • 投票
	• その投票を削除（/votes/delete/ or 画面の削除ボタン）
	• 再度投票
	• もう一度削除 ←ここでエラーが出る。
    """
    Survey.objects.filter(pk=survey.pk).delete()

    messages.success(request, "削除しました。")
    return redirect("survey-list")


# 投票画面(Votes)


# アンケート詳細画面
class VoteDetailView(DetailView):
    model = Vote
    template_name = "karakuchi_room/votes_detail.html"
    context_object_name = "vote"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # このURLの Vote インスタンス
        vote = self.object

        # そのVoteが属しているアンケート
        survey = vote.survey

        # この投票が属しているアンケート
        ctx["survey"] = survey

        # 詳細用フォーム（surveyは self.survey を渡す）
        # DetailViewは「form_class = VoteDetailForm」と書いても反映されない。
        ctx["form"] = VoteDetailForm(instance=vote, survey=survey)

        # そのアンケートに紐づく選択肢一覧
        ctx["option_list"] = survey.options.filter(is_deleted=False)

        # この投票で選ばれた選択肢
        ctx["selected_option"] = vote.option

        return ctx


# 投票作成画面
class VoteCreateView(CreateView):
    model = Vote
    template_name = "karakuchi_room/votes_create.html"
    form_class = VoteForm

    def dispatch(self, request, *args, **kwargs):
        survey = get_object_or_404(Survey, pk=self.kwargs["survey_id"])

        # end_at を使って受付終了を判定
        now = timezone.now()
        if survey.end_at and survey.end_at <= now:
            return redirect("survey-detail", pk=survey.pk)

        self.survey = survey

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # この投票が属しているアンケート
        ctx["survey"] = self.survey

        # そのアンケートに紐づく選択肢一覧
        ctx["option_list"] = self.survey.options.filter(is_deleted=False)

        return ctx

    def form_valid(self, form):
        # ここで「すでに有効な投票があるか」をチェック
        already_voted = Vote.objects.filter(
            user=self.request.user,
            survey=self.survey,
            is_deleted=False,
        ).exists()

        # すでに投票している場合
        if already_voted:
            messages.error(self.request, "このアンケートには既に投票済みです。")
            return redirect("survey-detail", pk=self.survey.pk)

        # まだ投票していない場合だけ保存
        # 作成するVoteにsurveyを紐づけ
        form.instance.user = self.request.user
        form.instance.survey = self.survey
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("survey-detail", kwargs={"pk": self.object.survey.pk})


# 投票編集画面
class VoteUpdateView(LoginRequiredMixin, UpdateView):
    model = Vote
    template_name = "karakuchi_room/votes_edit.html"
    form_class = VoteFormPublished
    context_object_name = "vote"

    def dispatch(self, request, *args, **kwargs):
        # pk から Vote を取得
        vote = self.get_object()
        survey = vote.survey

        # 受付終了なら編集させずにアンケート詳細画面へ
        if survey.end_at and survey.end_at <= timezone.now():
            return redirect("survey-detail", pk=survey.pk)

        # あとで使いたければ保持しておく
        self.survey = survey
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["survey"] = self.survey
        ctx["option_list"] = self.survey.options.filter(is_deleted=False)
        return ctx

    def get_success_url(self):
        return reverse_lazy("survey-detail", kwargs={"pk": self.survey.pk})


# 投票削除(DeleteViewは別途削除用のページが必要なので、今回は別の方法で実装)
def vote_delete(request, pk):
    vote = get_object_or_404(Vote, pk=pk)

    # ソフトデリートではなく「物理削除」にする
    """
    物理削除にした理由
    
    ソフトデリートだと以下のパターンでエラーが出るから
    • 投票
	• その投票を削除（/votes/delete/ or 画面の削除ボタン）
	• 再度投票
	• もう一度削除 ←ここでエラーが出る。
    """
    Vote.objects.filter(pk=vote.pk).delete()

    messages.success(request, "削除しました。")
    return redirect("survey-list")
