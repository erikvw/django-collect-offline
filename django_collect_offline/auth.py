from django.contrib.auth.models import User

from rest_framework_httpsignature.authentication import SignatureAuthentication


class OfflineSignatureAuthentication(SignatureAuthentication):

    # The HTTP header used to pass the consumer key ID.
    API_KEY_HEADER = 'X-Api-Key'

    # A method to fetch (User instance, user_secret_string) from the
    # consumer key ID, or None in case it is not found.
    def fetch_user_data(self, username, api_key):
        try:
            user = User.objects.get(username=username, api_key=api_key)
            return (user, user.secret)
        except User.DoesNotExist:
            return None
