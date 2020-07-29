import unittest

from flask import url_for
from flask_testing import TestCase
from flask_login import login_user, current_user, logout_user, login_required

from application import app, db, bcrypt
from application.models import Users, Posts
from os import getenv

class TestBase(TestCase):

    def create_app(self):

        # pass in configurations for test database
        config_name = 'testing'
        app.config.update(SQLALCHEMY_DATABASE_URI=getenv('TEST_DB_URI'),
                SECRET_KEY=getenv('TEST_SECRET_KEY'),
                WTF_CSRF_ENABLED=False,
                DEBUG=True
                )
        return app

    def setUp(self):
        """
        Will be called before every test
        """
        # ensure there is no data in the test database when the test starts
        db.session.commit()
        db.drop_all()
        db.create_all()

        # create test admin user
        hashed_pw = bcrypt.generate_password_hash('admin2016')
        admin = Users(first_name="admin", last_name="admin", email="admin@admin.com", password=hashed_pw)

        # create test non-admin user
        hashed_pw_2 = bcrypt.generate_password_hash('test2016')
        employee = Users(first_name="test", last_name="user", email="test@user.com", password=hashed_pw_2)

        # save users to database
        db.session.add(admin)
        db.session.add(employee)
        db.session.commit()

    def tearDown(self):
        """
        Will be called after every test
        """
        db.session.remove()
        db.drop_all()

class TestViews(TestBase):

    def test_homepage_view(self):
        """
        Test that homepage is accessible without login
        """
        response = self.client.get(url_for('home'))
        self.assertEqual(response.status_code, 200)

    def test_loginpage_view(self):
        response = self.client.get(url_for('login'))
        self.assertEqual(response.status_code, 200)

class TestPosts(TestBase):

    def test_add_new_post(self):
        """
        Test that when I add a new post, I am redirected to the homepage with the new post visible
        """
        with self.client:
            # logs in a user to be able to test functions that require a logged in user
            self.client.post(url_for('login'), data=dict(email="admin@admin.com", password="admin2016"), follow_redirects=True)
            response = self.client.post(
                '/post',
                data=dict(
                    title="Test Title",
                    content="Test Content"
                ),
                follow_redirects=True
            )
            self.assertIn(b'Test Title', response.data)

class TestLogin(TestBase):

    def test_login(self):
        with self.client:
            response = self.client.post(
                '/login',
                data=dict(
                    email="admin@admin.com",
                    password="admin2016"
                ),
                follow_redirects=True
            )
            self.assertEqual(current_user.email, "admin@admin.com")

class TestLogout(TestBase):

    def test_logout(self):
        with self.client:
            response = self.client.get(
                '/logout',
                follow_redirects=True
            )
            self.assertFalse(current_user.is_authenticated)

class TestRegister(TestBase):

    def test_register(self):
        with self.client:
            response = self.client.post(
                '/register',
                data=dict(
                    first_name="John",
                    last_name="Doe",
                    email="John@Doe.com",
                    password="testuser1",
                    confirm_password="testuser1"
                ),
                follow_redirects=True
            )
            self.assertTrue(response.status_code, 200)
