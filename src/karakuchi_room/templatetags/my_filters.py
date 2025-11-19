# Django のテンプレート言語では、変数で辞書のキーを指定してその値を取得する組み込み機能は制限されている
# そのためカスタムテンプレートを定義して使用する必要がある
from django import template

register = template.Library()


@register.filter
def dict_get(d, key):
    """
    辞書 d から key に対応する値を返す。
    key が存在しなければ None を返す（必要ならデフォルトを変える）
    """
    try:
        return d.get(key)
    except Exception:
        return None
