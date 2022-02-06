from django.db import IntegrityError, transaction
from django.test import TestCase
from django.contrib.auth import get_user_model


def sample_user(
    username='test_user',
    password='testpass',
    email='test@gmail.com',
    first_name='test_first',
    last_name='test_last',
    location='98406',
):
    """Helper function to create sample user"""
    return get_user_model().objects.create_user(
        username=username,
        password=password,
        email=email,
        first_name=first_name,
        last_name=last_name,
        location=location,
    )


class UserModelTests(TestCase):
    def test_create_user_successful(self):
        """Test creating new user is successful"""
        username = 'test_user'
        password = 'testpass'
        email = 'test@gmail.com'
        first_name = 'test_first'
        last_name = 'test_last'
        location = '98406'
        user = get_user_model().objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            location=location,
        )
        self.assertEqual(user.email, email)
        self.assertEqual(user.username, username)
        self.assertEqual(user.first_name, first_name)
        self.assertEqual(user.last_name, last_name)
        self.assertEqual(user.location, location)
        self.assertTrue(user.check_password(password))

    def test_new_user_invalid_username_none(self):
        """Test creating a user with no username raises error"""
        with self.assertRaises(ValueError):
            sample_user(username=None)

    def test_new_user_invalid_username_duplicate(self):
        """Test creating a user with duplicate username raises error"""
        sample_user()
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                sample_user()
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                sample_user(username='Test_User')

    def test_new_user_required_fields(self):
        """Test creating a new user with missing fields raises error"""
        with self.assertRaises(ValueError):
            sample_user(email=None)
        with self.assertRaises(ValueError):
            sample_user(first_name=None)
        with self.assertRaises(ValueError):
            sample_user(last_name=None)
        with self.assertRaises(ValueError):
            sample_user(location=None)
