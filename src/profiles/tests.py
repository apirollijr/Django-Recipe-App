from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Profile


User = get_user_model()


class ProfileModelTests(TestCase):
	def test_str(self):
		user = User.objects.create_user(username="alice", password="testpass123")
		profile = Profile.objects.create(user=user, bio="Home cook")
		self.assertEqual(str(profile), "alice")
