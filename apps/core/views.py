from django.http import JsonResponse
from .settings import LANGUAGE_CHOICES


def language_choices_view(request):
    term = request.GET.get('term', '')
    data = {
        'results': [
            {
                'id': x[0],
                'title': x[1],
            } for x in LANGUAGE_CHOICES if x[1].lower().startswith(term.lower())
        ],
        'more': True,
    }
    return JsonResponse(data)
