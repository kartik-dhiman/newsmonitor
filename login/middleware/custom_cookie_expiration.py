from django.utils.deprecation import MiddlewareMixin


class AutoLogout(MiddlewareMixin):

    def process_request(self, request):
        if not request.user.is_active:
            # Can't do anything if user not active
            pass
        elif request.user.is_staff or request.user.is_superuser:
            #  30 days session for Staff and Superuser
            request.session.set_expiry(30 * 24 * 60 * 60)
        else:
            # Session Expires on browser close for Non-Staff Users
            request.session.set_expiry(0)