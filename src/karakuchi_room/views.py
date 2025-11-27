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

from .models import Tag, TagSurvey

# タグを表示、選択するためにmodels.pyから中間テーブルとそれに紐づいているテーブルをインポート

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
    UserFormPublished,
)
from django.utils import timezone
from django.db import transaction
from karakuchi_room.models import User, Survey, Vote, Option
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib import messages
import logging
import os
import json
from openai import OpenAI
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

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
# models.pyでSurveyとtagを紐付けているので、アンケートに紐づいているタグはここで呼び出せる
# {% for tag in survey.tag.all %}から{{ tag.tag_name }}を呼び出せる
class SurveyListView(LoginRequiredMixin, ListView):
    model = Survey
    template_name = "karakuchi_room/surveys.html"
    context_object_name = "survey_list"

    # しほ：タグを一覧表示
    def get_context_data(self, **kwargs):
        # 親クラス(listView)がコンテキストに渡そうとしているデータを受け取り可能にしている
        context = super().get_context_data(**kwargs)
        # 親クラス(ListView)が作ったcontext(survey_listなど)を取得している
        context["all_tags"] = Tag.objects.filter(is_deleted=False)
        # ここでTagのデータを自分で追加している
        # filter(is_deleted=False)は論理削除されていないタグの一覧とういう意味
        context["selected_tag_ids"] = self.request.GET.getlist("tag")
        # タグで絞り込みを行った時ににUIで再描写した時に選んだタグをチェック状態で残す
        # これがないと再描写した時にチェックが外れてしまう
        # getlist("tag")：ユーザが選択したタグのIDのリストを取得
        return context

    def get_queryset(self):
    
        user = self.request.user
        # 現在ログイン中のユーザーを取得
        now = timezone.now()
        # 今の日時を取得
        # 投票受付中の絞り込みで使用

        # しほ修正：アンケートの変数名を統一など
        surveys = Survey.objects.filter(is_deleted=False).filter(
            # 論理削除されていない全アンケート一覧を取得(ここで公開済/一時保存も取得できる)
            # 変数名分けてはダメ。
            Q(is_public=True) | Q(user=user)
        )
        # is_public=True：公開されているアンケート
        # user=user：自分が作ったアンケートを全て取得(一時保存も含む)

        # ↓アンケートの変数名がバラバラでで分かれていて混乱して検索できない原因になっていた
        # 変数名は検索機能がなくても絶対統一すべき！！！！
        # これはDjangoに限らず、エンジニア共通の鉄則！！！！
        # ①可読性が一気に下がる
        # ②バグが起きやすくなる
        # ③実務では段階的に絞るのが基本
        # 実務では変数名を変えての絞り込みは行われない。


        # しほ：アンケート検索機能
        keyword = self.request.GET.get("q")
        # URLのクエリパラメーター(?q=検索ワード)を取得
        # 例：/survey/?q=好きな食べ物とアクセスされた時(keyword="好きな食べ物")
        # もし何も入力されていなければNoneが入る
        if keyword:
            # 検索ワードが入力されていたら検索条件で絞り込みを行う
            # 検索フォームが空の場合はフィルターをかけずにスルー
            surveys = surveys.filter(
                # ↑surveysのオブジェクトの中から、この条件に合うものだけを残して！という命令文
                # フィールド名　= フィールド名.filter(...条件)
                Q(title__icontains=keyword) | Q(description__icontains=keyword)
            )
            # そもそもQオブジェクトとは？
            # Qオブジェクトを使うとOR条件や複雑な条件が書けるようになる
            # 例：AかBのどちらか、Aかつ(BかC)、NOT A、みたいなSQLのWHERE条件を自由に組み立てたもの

            # title__icontainsの意味
            # title→モデルのフィールド名（Surveyモデルのtitleフィールド(アンケートタイトル))
            # __(ダブルアンダースコア)はDjangoのフィルタのルール指定
            # icontains(アイコンテインズ)→大文字、小文字を区別しない部分一致検索
            # description→説明文にキーワードが一致していたらヒットする

        # しほ：タグ検索
        tag_ids = self.request.GET.getlist("tag")
        # URLのクエリパラメータ(tag=1&tag=3)ここではリストとして取得
        # get()は1つしか取れないけど、タグは複数選ばれる可能性があるのでgetlist()を使う
        if tag_ids:
            # タグが選ばれていたら絞り込みを行う
            surveys = surveys.filter(tag_survey__in=tag_ids).distinct()
            # tag_survey(アンケートに紐付くタグ)の中に、選択されたタグID(tag_ids)が含まれているアンケートだけを残す
            # .distinct()をつけることで同じアンケートがヒットしないようにしている
            #  models.ManyToManyField(多対多)ではアンケートが重複して返ることがあるので
            # distinct()をつけることで重複を防ぐ

        # しほ追記：自分のアンケートのみを絞り込み
        if self.request.GET.get("own_only") == "1":
            # self.request.GET.getはDjango が用意してくれてる「GETパラメータ辞書」
            # .get("own_only") は URL のクエリパラメータから "own_only" の値を取得する
            # → チェックが入っていれば "1"、入っていなければパラメータが付かないので None になる
            surveys = surveys.filter(user=user)
            # (user=user)は自分のアンケートのみにチェックという意味

        # しほ追記：投票受付中のみを絞り込み
        if self.request.GET.get("open_only") == "1":
            # ユーザが投票受付中のみ表示にチェックを入れたかどうか
            # start_at と end_at の両方がnullの場合でも検索できるように設定
            surveys = surveys.filter(
                (Q(start_at__lte=now) | Q(start_at__isnull=True)),
                (Q(end_at__gte=now) | Q(end_at__isnull=True)),
            )
            # start_atはアンケートモデル(surveys)の開始日時フィールド
            # __lteはDjangoの演算子(<= 現在時刻以下)
            # nowはtimezone.now()を継承している。これは現在日時を取得している
            # つまり、start_time__lte=nowは開始日時が現在より前または同じアンケートに絞り込み
            # end_atはアンケートモデル(surveys)の終了日時フィールド
            # __gteはDjangoの演算子(=> 現在時刻以上)
            # つまり、end_time__gte=nowは終了日時が現在より後または同じアンケートに絞り込み
            # この組み合わせで投票受付中のアンケートだけが絞り込まれる

        # しほ修正：アンケートの変数名をsurveysに統一
        # ここでやりたいことはアンケート一覧の各アンケートについて、自分が投票済みかを判定する
        # ここで判定することで他の方のアンケートの詳細を見ることができる
        surveys = surveys.annotate(
            # annotate(アノテイト)とは？
            # DjangoのQuerySetのメソッド。SQLでいうSELECT ... , (サブクエリ) AS has_voted と同じイメージ
            # ここではレコード(surveys)にフィールド(has_vote)をつけている
            has_voted=Exists(
                # Exists()は投票したかどうかうぃTrue/Falseで返す
                Vote.objects.filter(
                    survey=OuterRef("pk"),
                    # OuterRef("pk") は 「外側の QuerySet（surveys）の現在のアンケートの主キー(ID)」 を指す
                    user=user,
                    # 現在ログインしているユーザーの投票かどうか
                    # 自分が投票済みかを確認する
                    is_deleted=False,
                    # 論理削除されていない投票だけを取得
                )
            )
        )

        return surveys.order_by("-id")
        # order_byは並び順を指定するためのDjangoのクエリセットメソッド
        # -idと書くとidの降順(新しいアンケート順),-をつけない時は古い順になる


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

        # # これまでの投票一覧（このアンケートの全投票）
        ctx["vote_list"] = (
            Vote.objects.filter(survey=survey, is_deleted=False)
            .select_related("user", "option")
            .order_by("-created_at")
        )

        # # 選択項目ごとの票数（このアンケート内）
        # ctx["option_vote_counts"] = (
        #     Vote.objects.filter(survey=survey, is_deleted=False)
        #     .values("option__id", "option__label")
        #     .annotate(vote_count=Count("id"))
        #     .order_by("option__id")
        # )

        # 選択項目ごとの票数（このアンケート内）Option を起点に、すべての選択肢を取得しつつ投票数（0票も含む）を集計
        ctx["option_vote_counts"] = (
            Option.objects.filter(
                survey=survey, is_deleted=False
            )  # 論理削除されていないオプションを取得
            .annotate(
                vote_count=Count("votes", filter=Q(votes__is_deleted=False))
            )  # 投票数を集計（論理削除されていないもの）
            .order_by("id")  # オプションIDで並び替え
        )

        # コメント付きの投票を取得(コメントなしの投票を除外)
        ctx["vote_with_comment"] = (
            Vote.objects.filter(survey=survey, is_deleted=False)
            .exclude(comment__isnull=True)
            .exclude(comment="")
            .select_related("option")
            .order_by("-created_at")
        )

        # Chart.js 用の配列を作る 選択肢と凡例の色を対応付ける
        labels = []
        vote_counts = []
        colors = []
        # 固定パレット
        COLOR_PALETTE = ["#34d399", "#f87171", "#60a5fa", "#fbbf24"]

        option_color_map = {}  # option_id → 色マップ

        for idx, opt in enumerate(ctx["option_vote_counts"]):
            labels.append(opt.label)
            vote_counts.append(opt.vote_count)
            color = COLOR_PALETTE[idx % len(COLOR_PALETTE)]
            colors.append(color)
            option_color_map[opt.id] = color

        ctx["chart_labels"] = labels
        ctx["chart_counts"] = vote_counts
        ctx["chart_colors"] = colors
        ctx["option_color_map"] = option_color_map

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
                # Survey(アンケート)保存
                survey = form.save(commit=False)
                user = (
                    self.request.user
                    if self.request.user.is_authenticated
                    else get_guest_user()
                )
                survey.user = user
                survey.save()  # ←ここでsurvey.idが確定
                formset.instance = survey  # Option の親を設定
                formset.save()

                # しほ：ここからタグ保存処理
                selected_tags = form.cleaned_data.get("tag_survey", [])
                # フォームの入力チェック（バリデーション）
                # tag_surveyのフォームが空の場合は[]を返す
                # []を返すことでループのエラーを防ぐ
                for tag in selected_tags:
                    # フォームでユーザーが選択したTag(タグ)モデルのそのものの(インスタンス)のリストを取り出している
                    TagSurvey.objects.get_or_create(survey=survey, tag=tag)
                    # 中間テーブル(TagSurvey)に同じ組み合わせデータがすでにあるかを確認している
                    # 例えばsurvey=アンケート１＋tag=雑談
                    # 同じ組み合わせデータが中間テーブル(TagSurvey)にない場合は新規作成される。(True)
                    # 既に同じデータがある場合は新規作成されない(False)

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
        ctx["all_tags"] = Tag.objects.filter(is_deleted=False)
        # しほ：論理削除されていないタグの一覧を表示
        return ctx

    # 公開済みは常に公開のままに固定するなら明示しておく
    def form_valid(self, form):
        self.object = form.save(commit=False)

        # POSTフォームセットを必ず自前で生成
        formset = OptionFormSetForDraft(
            self.request.POST, instance=self.object, prefix="options"
        )

        # form はすでに valid。formset だけ検証すればOK
        if not formset.is_valid():
            return self.form_invalid(form)

        with transaction.atomic():  # どちらか失敗すればロールバック
            # UpdateView: 既存 self.object を更新
            # フォームから is_public の値を反映（ラジオで公開に切り替え可能にするため）
            self.object.is_public = bool(form.cleaned_data.get("is_public", False))
            # user は上書きしない（作成者そのまま）
            self.object.save()

            formset.instance = self.object

            # commit=False にして、削除対象・更新対象を分ける
            opts = formset.save(commit=False)

            # 削除マークが付いたものを論理削除
            for obj in formset.deleted_objects:
                obj.is_deleted = True
                obj.save()

            # 更新／新規のものを保存
            for opt in opts:
                opt.is_deleted = False  # 削除マークがないものは有効化
                opt.survey = self.object
                opt.save()

            # しほ：ここからタグの追加、削除
            # 選択されたタグを再保存
            selected_tags = form.cleaned_data.get("tag_survey", [])
            # フォームの入力チェック（バリデーション）
            # tag_surveyのフォームが空の場合は[]を返す
            # []を返すことでループのエラーを防ぐ
            TagSurvey.objects.filter(survey=self.object).delete()
            # 中間テーブル(TagSurvey)から今編集しているアンケート(self.object)に紐づくタグを全て取得している
            # .delete()で検索したアンケートに紐づいているタグを削除している
            # アンケート＋タグでセットになって保存しているので紐づいているタグを一旦クリアにすることでタグの追加、削除することができる
            for tag in selected_tags:
                # `tag` にはユーザーが選んだ Tag モデルのインスタンス
                # （例：<Tag id=1 name="雑談">）がそのまま入っている
                TagSurvey.objects.get_or_create(survey=self.object, tag=tag)
                # これは追加、削除があった場合の保存処理
                # 中間テーブル(TagSurvey)に同じレコード(組み合わせ)がないかを確認(survey=self.object, tag=tag)
                # 存在しなければ新しく作成、存在すれば作らない(get_or_create)

            # 　フォームセット(選択肢)も再保存
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
    survey.delete()

    messages.success(request, "削除しました。")
    return redirect("survey-list")


# 投票画面(Votes)
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


# これは後で使うかも
# TagSurvey.objects.filter(survey=survey).delete()
# 編集対応するなら削除機能も必要
# models.pyで指定している中間テーブル名(TagSurvey)でアンケートに紐づいているタグを削除


# ユーザー詳細
class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "karakuchi_room/users_detail.html"


# ユーザー編集
class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserFormPublished
    template_name = "karakuchi_room/users_edit.html"

    def form_valid(self, form):
        user = form.save(commit=False)

        # パスワード1に入力があれば更新する
        password = form.cleaned_data.get("password1")
        if password:
            user.set_password(password)

        # user_name / email / password をまとめて保存
        user.save()

        # ログアウト防止
        update_session_auth_hash(self.request, user)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("survey-list")


# コメント生成AI機能（新SDK対応版）
@csrf_exempt
def soften_comment(request):
    """コメントを柔らかい表現に変換し、誹謗中傷をチェックする"""

    client = OpenAI(api_key=os.environ["API_KEY"])

    data = json.loads(request.body)
    text = data.get("text", "")

    if not text.strip():
        return JsonResponse({"error": "文章が入力されていません。"}, status=400)

    # -----------------------------
    # 柔らかい表現への書き換え（GPT）
    # -----------------------------
    prompt = f"""
以下のルールに従って、入力された文章のみを柔らかく書き換えてください。
・回答文は書かないこと（「こんな感じで書き換えました！」などのコメント不要）
・書き換え後の文章だけを出力すること
・文章の意味や主張は変えないこと（内容を追加したり削除したりしない）
・“柔らかくする” とは表現を少し優しくする程度にとどめること
・絵文字を入れること
・丁寧になりすぎて元の意図が失われるような完全書き換えは禁止
・攻撃的・失礼な要素があればすべて取り除くこと 
・ネガティブな意見は相手が受け止めやすいように表現を書き換えてください。

元の文章：
{text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    soft_text = response.choices[0].message.content

    return JsonResponse({"soft_text": soft_text})


# アンケートの絞り込み
class SurveyListview(ListView):
    model = Survey
