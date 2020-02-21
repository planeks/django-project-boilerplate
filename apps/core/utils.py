from django.conf import settings
from typing import Optional
from collections import namedtuple


SLUG_SAVE_AS_DASH = '.,/'
SLUG_ALLOWED_CHARS = r'^[a-zA-Z0-9\-]$'


Color = namedtuple('Color', 'red green blue')
RANDOM_COLORS = [
    (151, 204, 156),
    (78, 61, 35),
    (250, 69, 30),
    (175, 219, 228),
    (198, 13, 175),
    (225, 176, 235),
    (49, 252, 166),
    (243, 152, 74),
    (245, 47, 61),
    (213, 180, 15),
    (255, 158, 65),
    (135, 206, 33),
    (254, 96, 20),
    (155, 136, 2),
    (68, 228, 99),
    (102, 13, 5),
    (122, 223, 235),
    (126, 250, 113),
    (130, 87, 90),
    (172, 204, 163)]


def slugify_unicode(value, save_as_dash=SLUG_SAVE_AS_DASH, dash='-'):
    import re
    import slugify
    for k in save_as_dash:
        value = value.replace(k, dash)
    result = slugify.slugify(value, only_ascii=True)

    pattern = re.compile(SLUG_ALLOWED_CHARS)
    result = ''.join(filter(lambda x: pattern.match(x) is not None, result))
    return result


def get_unique_slug(
        value,
        model_class,
        slug_attr='slug',
        slug_func=slugify_unicode,
        ignore_slugs=[],
        query_init_expr=None):
    """ Generate unique slug for a model."""
    import itertools
    _slug = _orig = slug_func(value)
    for x in itertools.count(1):
        if query_init_expr:
            query = model_class.objects.filter(query_init_expr)
        else:
            query = model_class.objects.all()
        if not query.exclude(
                **{'%s__in' % slug_attr: ignore_slugs}).filter(**{slug_attr: _slug}).exists():
            break
        _slug = '%s-%d' % (_orig, x)
    return _slug


def markdown_to_html(source):
    import markdown
    html = markdown.markdown(
        source,
        extensions=[
            'markdown.extensions.nl2br',
            # 'urlize',
        ])
    return html


def generate_random_color(mix, id) -> Color:
    """ Generates a `Color` object. If `id=None`, then color will be generated
    randomly, in other case the result is predictable based on specified `id`.
    If `mix` is specified the result is generating with colors mixing.
    """
    import random

    if id is None:
        red = random.randint(0, 255)
        green = random.randint(0, 255)
        blue = random.randint(0, 255)
    else:
        _number = int(str(id).replace('-', ''), 16) % len(RANDOM_COLORS)
        red = RANDOM_COLORS[_number - 1][0]
        green = RANDOM_COLORS[_number - 1][1]
        blue = RANDOM_COLORS[_number - 1][2]

    # mix the color
    if mix is not None:
        red = (red + mix.red) // 2
        green = (green + mix.green) // 2
        blue = (blue + mix.blue) // 2

    color = Color(red, green, blue)
    return color


def color_to_hex(color: Color) -> str:
    return '#%02x%02x%02x' % color


def get_translated_value(struct, lang=None, default_language=None):
    from django.utils.translation import get_language
    from .models import Language
    if type(struct) is str:
        return struct
    _default_language = default_language or Language.objects.get_default_language()
    lang_code = lang or get_language()
    if lang_code in struct:
        return struct[lang_code]
    elif _default_language.language in struct:
        return struct[_default_language.language]
    elif len(struct.keys()) > 0:
        return struct[struct.keys()[0]]
    else:
        return ''


def send_mail(
        to=[],
        subject='',
        html_template='',
        txt_template='',
        context={},
        from_email=settings.DEFAULT_FROM_EMAIL):
    """Send mail to the all contacts
    """
    from django.core import mail
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string
    _to = to

    context.update({
        'SITE_URL': settings.SITE_URL,
    })

    text = render_to_string(txt_template, context)
    html = render_to_string(html_template, context)

    result = None

    with mail.get_connection() as connection:
        mail = EmailMultiAlternatives(
            subject=subject,
            body=text,
            from_email=from_email,
            to=_to,
            connection=connection,
        )
        mail.attach_alternative(html, "text/html")
        result = mail.send(fail_silently=True)
    return result


def turbolinks_redirect(destination):
    from django.http import HttpResponse
    return HttpResponse('Turbolinks.visit("%s")' % destination)


def flatten(d, parent_key='', sep='.'):
    import collections
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
