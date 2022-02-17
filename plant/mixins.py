from django.conf import settings
import os
import json


class TemplateTitleMixin(object):
    title = None

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = self.get_title()
        return context

    def get_title(self):
        return self.title


class ZipcodeCityStateMixin(object):
    def _get_citystate_from_zipcode(self, zipcode, zipcode_data):
        """Translates zipcode to city, state string"""
        if zipcode in zipcode_data:
            city_state = (
                f'{zipcode_data[zipcode]["city"]}, '
                f'{zipcode_data[zipcode]["state"]}'
            )
        else:
            city_state = "Contact seller"
        return city_state

    def _get_zipcode_data(object):
        if not settings.DEBUG:
            file_path = os.path.join(settings.STATIC_ROOT, 'zipcode_data.json')
        else:
            file_path = 'static/zipcode_data.json'
        zipcode_file = open(file_path)
        zipcode_data = json.load(zipcode_file)
        return zipcode_data
