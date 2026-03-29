"""
Template tags for handling image URLs
"""
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def image_url(context, url):
    """
    Rasm URL ni to'liq URL ga aylantiradi.
    Agar URL allaqachon http bilan boshlansa, o'zgartirmaydi.
    """
    if not url:
        return ''

    if isinstance(url, str):
        if url.startswith('http://') or url.startswith('https://'):
            return url

        base_url = context.get('base_url', '')
        if base_url:
            if url.startswith('/'):
                return base_url + url
            else:
                return base_url + '/' + url

        # Fallback: return as-is
        return url

    return str(url) if url else ''


@register.filter
def fix_image(url, base_url=''):
    """
    Filter versiyasi - rasm URL ni to'liq qiladi
    Usage: {{ image_path|fix_image:base_url }}
    """
    if not url:
        return ''

    if isinstance(url, str):
        if url.startswith('http://') or url.startswith('https://'):
            return url

        if base_url:
            if url.startswith('/'):
                return base_url + url
            else:
                return base_url + '/' + url

    return str(url) if url else ''
