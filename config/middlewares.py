from django.utils.translation import activate
from django.conf import settings


class ActivateLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language = request.META.get('HTTP_ACCEPT_LANGUAGE')
        if language:
            language = language.split(',')[0]  # Extract the first language in case of multiple
            activate(language)
        else:
            activate(settings.LANGUAGE_CODE)  # Use default language if Accept-Language header is not present

        response = self.get_response(request)
        return response
