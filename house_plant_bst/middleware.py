import zoneinfo

from django.utils import timezone
from plant.mixins import ZipcodeCityStateMixin


class TimezoneMiddleware(ZipcodeCityStateMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            zipcode_data = self.get_zipcode_data()
            tzname = self.get_timezone_from_zipcode(
                request.user.location, zipcode_data
            )
        else:
            tzname = 'UTC'
        if tzname:
            timezone.activate(zoneinfo.ZoneInfo(tzname))
        else:
            timezone.deactivate()
        return self.get_response(request)
