from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import CredentialRecord as Credentials
class CredentialVaultUserTestMixin(UserPassesTestMixin):
    def test_func(self):
        return super().test_func()