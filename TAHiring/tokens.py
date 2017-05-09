from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_text

class ConfirmOfferTokenGenerator(PasswordResetTokenGenerator):
    """ Uses django's builtin password reset token generator to create a
    one-time link to a view which confirms the user's offer.
    """

    def _make_hash_value(self, tadata, timestamp):
        return force_text(tadata.full_name) + force_text(timestamp) + force_text(tadata.email)

confirm_offer_token = ConfirmOfferTokenGenerator()

