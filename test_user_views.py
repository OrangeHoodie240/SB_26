"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        user1 = User(username='name1', email='email1@email.com', password='password1')
        db.session.add(user1)

        user2 = User(username='name2', email='email2@email.com', password='password2')
        db.session.add(user2)
        
        user3 = User(username='name3', email='email3@email.com', password='password3')
        db.session.add(user3)

        db.session.commit() 

        follows1 = Follows(user_being_followed_id=user2.id, user_following_id=user1.id)
        db.session.add(follows1)
        follows2 = Follows(user_being_followed_id=user3.id, user_following_id=user1.id)
        db.session.add(follows2)
        follows3 = Follows(user_being_followed_id=user1.id, user_following_id=user2.id)
        db.session.add(follows3)
        follows4 = Follows(user_being_followed_id=user1.id, user_following_id=user3.id)
        db.session.add(follows4)


        db.session.commit()


    # When you’re logged in, can you see the follower / following pages for any user?
    def test_logged_in_see_anyones_followers(self):
        user1 = User.query.filter(User.username=='name1').one()

        with self.client as c: 
            with c.session_transaction() as session: 
                session[CURR_USER_KEY] = self.testuser.id
            resp = c.get(f'/users/{user1.id}/followers')

            self.assertEqual(resp.status_code, 200)
            
            html = resp.get_data(as_text=True)
            self.assertIn('@name2', html)
            self.assertIn('@name3', html)


    def test_logged_in_see_anyones_following(self):
        user1 = User.query.filter(User.username=='name1').one()

        with self.client as c: 
            with c.session_transaction() as session: 
                session[CURR_USER_KEY] = self.testuser.id
            resp = c.get(f'/users/{user1.id}/following')

            self.assertEqual(resp.status_code, 200)
            
            html = resp.get_data(as_text=True)
            self.assertIn('@name2', html)
            self.assertIn('@name3', html)

    # When you’re logged out, are you disallowed from visiting a user’s follower / following pages?

    def test_logged_out_wont_see_anyones_followers(self):
        user1 = User.query.filter(User.username=='name1').one()

        with self.client as c: 
            resp = c.get(f'/users/{user1.id}/followers')

            self.assertNotEqual(resp.status_code, 200)
            
            html = resp.get_data(as_text=True)
            self.assertNotIn('@name2', html)
            self.assertNotIn('@name3', html)


    def test_logged_out_wont_see_anyones_following(self):
        user1 = User.query.filter(User.username=='name1').one()

        with self.client as c: 
            resp = c.get(f'/users/{user1.id}/following')

            self.assertNotEqual(resp.status_code, 200)
            
            html = resp.get_data(as_text=True)
            self.assertNotIn('@name2', html)
            self.assertNotIn('@name3', html)

    def test_add_user(self):
        before_count = User.query.count() 
        
        with self.client as c: 
            resp = c.post('/signup', data={'username': 'name4', 'email': 'email4@email.com', 'password': 'password4'})

            self.assertEqual(resp.status_code, 302)
            
            after_count = User.query.count() 
            self.assertEqual(before_count + 1, after_count)

    def test_deletes_user(self):
        user = User(username='name4', email='email4@email.com', password='password4')
        db.session.add(user)
        db.session.commit() 

        before_count = User.query.count() 
        with self.client as c: 
            with c.session_transaction() as session: 
                session[CURR_USER_KEY] = user.id
            
            resp = c.post('/users/delete')

            self.assertEqual(resp.status_code, 302)

            after_count = User.query.count() 
            self.assertEqual(after_count, before_count - 1)
