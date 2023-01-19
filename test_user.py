try:
    import unittest
    from app import app
    from unittest.mock import Mock, patch
    from flask_jwt_extended import create_access_token, create_refresh_token
    import json
    from user.api import hashing_password
    import redis
except Exception as e:
    print('Some modules are missing {}'.format(e))


class ApiTest1(unittest.TestCase):
    client=app.test_client()
    with app.app_context():
        jwt_redis_blocklist = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)
        access_token = dict(Authorization='Bearer ' + create_access_token(identity=1))
        refresh_token = dict(Authorization='Bearer ' + create_refresh_token(identity=1))

    @patch('user.api.checking_mail_exist')
    @patch('user.api.checking_username_exist')
    @patch('user.api.saving_user_to_db')
    def test_signup1(self, mock_saving_user_to_db, mock_checking_username_exist, mock_checking_mail_exist):
        signup_obj = {
            "email_id": "",
            "username": "testuser",
            "password": "Admin@123"}
        mock_saving_user_to_db.return_value = {"data": {"message": "user created"}}, 200
        mock_checking_username_exist.return_value = None
        mock_checking_mail_exist.return_value = None
        response = self.client.post("/user/signup", json=signup_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error')
        self.assertTrue(b'email cannot be empty')

    @patch('user.api.checking_mail_exist')
    @patch('user.api.checking_username_exist')
    @patch('user.api.saving_user_to_db')
    def test_signup2(self, mock_saving_user_to_db, mock_checking_username_exist, mock_checking_mail_exist):
        signup_obj = {
            "email_id": "testuser@yahoo.com",
            "username": "",
            "password": "Admin@123"}
        mock_saving_user_to_db.return_value = {"data": {"message": "user created"}}, 200
        mock_checking_username_exist.return_value = None
        mock_checking_mail_exist.return_value = None
        response = self.client.post("/user/signup", json=signup_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'username cannot be empty' in response.data)

    @patch('user.api.checking_mail_exist')
    @patch('user.api.checking_username_exist')
    @patch('user.api.saving_user_to_db')
    def test_signup3(self, mock_saving_user_to_db, mock_checking_username_exist,mock_checking_mail_exist):
        signup_obj = {
                      "email_id": "testuser@gmail.com",
                      "username": "testuser",
                      "password": "Admin@123"}
        mock_saving_user_to_db.return_value={"data": {"message": "user created"}}, 200
        mock_checking_username_exist.return_value=None
        mock_checking_mail_exist.return_value=None
        response=self.client.post("/user/signup", json=signup_obj)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'user created' in response.data)

    @patch('user.api.checking_mail_exist')
    @patch('user.api.checking_username_exist')
    @patch('user.api.saving_user_to_db')
    def test_signup4(self, mock_saving_user_to_db, mock_checking_username_exist, mock_checking_mail_exist):
        signup_obj = {
            "email_id": "",
            "username": "Testuser@1",
            "password": "Admin@123"}
        mock_saving_user_to_db.return_value = {"data": {"message": "user created"}}, 200
        mock_checking_username_exist.return_value = None
        mock_checking_mail_exist.return_value = None
        response = self.client.post("/user/signup", json=signup_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'email cannot be empty' in response.data)

    @patch('user.api.checking_mail_exist')
    @patch('user.api.checking_username_exist')
    @patch('user.api.saving_user_to_db')
    def test_signup5(self, mock_saving_user_to_db, mock_checking_username_exist, mock_checking_mail_exist):
        signup_obj = {
            "email_id": "testuser@gmail.com",
            "username": "Testuser1",
            "password": "Admin@123"}
        mock_saving_user_to_db.return_value = {"data": {"message": "user created"}}, 200
        mock_checking_username_exist.return_value = "user"
        mock_checking_mail_exist.return_value = None
        response = self.client.post("/user/signup", json=signup_obj)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'username already exists' in response.data)

    @patch('user.api.checking_mail_exist')
    @patch('user.api.checking_username_exist')
    @patch('user.api.saving_user_to_db')
    def test_signup6(self, mock_saving_user_to_db, mock_checking_username_exist, mock_checking_mail_exist):
        signup_obj = {
            "email_id": "testuser@gmail.com",
            "username": "Testuser1",
            "password": "Admin@123"}
        mock_saving_user_to_db.return_value = {"data": {"message": "user created"}}, 200
        mock_checking_username_exist.return_value = None
        mock_checking_mail_exist.return_value = "email"
        response = self.client.post("/user/signup", json=signup_obj)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'email already exists' in response.data)

    def test_hashing_password(self):
        self.assertNotEqual(hashing_password("password"), "password")

    @patch('user.api.checking_userpassword')
    @patch('user.api.password_match')
    @patch('user.api.checking_username_exist')
    def test_login1(self, mock_checking_username_exist, mock_password_match, mock_checking_userpassword):
        login_obj = {
            "username": "vigdelh11",
            "password": "Admin@123"}
        mock_checking_username_exist.return_value = None
        mock_password_match.return_value = True
        mock_checking_userpassword.return_value = {"data": {"message": "Login successful"},
                                                   "tokens": {"access_token": "access token",
                                                              "refresh_token": "refresh token"}}, 200
        response = self.client.post("/user/login", json=login_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'username does not exist' in response.data)

    @patch('user.api.checking_userpassword')
    @patch('user.api.password_match')
    @patch('user.api.checking_username_exist')
    def test_login2(self, mock_checking_username_exist, mock_password_match, mock_checking_userpassword):
        login_obj = {
            "username": "vigdelh11",
            "password": "Admin@123"}
        mock_checking_username_exist.return_value = "user"
        mock_password_match.return_value = False
        mock_checking_userpassword.return_value = {"data": {"message": "Login successful"},
                                                   "tokens": {"access_token": "access token",
                                                              "refresh_token": "refresh token"}}, 200
        response = self.client.post("/user/login", json=login_obj)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'incorrect password' in response.data)

    @patch('user.api.checking_userpassword')
    @patch('user.api.password_match')
    @patch('user.api.checking_username_exist')
    def test_login3(self, mock_checking_username_exist, mock_password_match, mock_checking_userpassword):
        login_obj = {
            "username": "vigdelh11",
            "password": "Admin@123"}
        mock_checking_username_exist.return_value = "user"
        mock_password_match.return_value = True
        mock_checking_userpassword.return_value={"data": {"message": "Login successful"},"tokens": {"access_token": "access token","refresh_token": "refresh token"}}, 200
        response = self.client.post("/user/login", json=login_obj)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'access token' in response.data)
        self.assertTrue(b'refresh token' in response.data)
        self.assertTrue(b'data' in response.data)


    def test_refresh1(self):
        response = self.client.get("/user/refresh", headers=self.refresh_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'access_token' in response.data)
        self.assertTrue(b'data' in response.data)

    def test_refresh2(self):
        response = self.client.get("/user/refresh")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content_type, "application/json")

    @patch('user.api.saving_new_password')
    @patch('user.api.matching_password')
    def test_resetpassword1(self, mock_matching_password, mock_saving_new_password):
        reset_password_obj = {
            "current_password": "Admin@123",
            "new_password": "Admin@1234"}
        mock_matching_password.return_value = True
        mock_saving_new_password.return_value = {"data": {"message": "password changed successfully"}}, 200

        response = self.client.put("/user/reset_password", json=reset_password_obj, headers= self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'data' in response.data)
        self.assertTrue(b'password changed successfully' in response.data)

    @patch('user.api.saving_new_password')
    @patch('user.api.matching_password')
    def test_resetpassword2(self, mock_matching_password, mock_saving_new_password):
        reset_password_obj = {
            "current_password": "",
            "new_password": "Admin@1234"}
        mock_matching_password.return_value = True
        mock_saving_new_password.return_value = {"data": {"message": "password changed successfully"}}, 200

        response = self.client.put("/user/reset_password", json=reset_password_obj, headers=self.access_token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'data' in response.data)
        self.assertTrue(b'provide current password' in response.data)

    @patch('user.api.saving_new_password')
    @patch('user.api.matching_password')
    def test_resetpassword3(self, mock_matching_password, mock_saving_new_password):
        reset_password_obj = {
            "current_password": "Admin@1234",
            "new_password": ""}
        mock_matching_password.return_value = True
        mock_saving_new_password.return_value = {"data": {"message": "password changed successfully"}}, 200

        response = self.client.put("/user/reset_password", json=reset_password_obj, headers=self.access_token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'data' in response.data)
        self.assertTrue(b'provide new password' in response.data)

    @patch('user.api.saving_new_password')
    @patch('user.api.matching_password')
    def test_resetpassword4(self, mock_matching_password, mock_saving_new_password):
        reset_password_obj = {
            "current_password": "Admin@1234",
            "new_password": "Admin@1234"}
        mock_matching_password.return_value = True
        mock_saving_new_password.return_value = {"data": {"message": "password changed successfully"}}, 200

        response = self.client.put("/user/reset_password", json=reset_password_obj, headers=self.access_token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'data' in response.data)
        self.assertTrue(b'new password should not be same as previous password' in response.data)

    @patch('user.api.saving_new_password')
    @patch('user.api.matching_password')
    def test_resetpassword5(self, mock_matching_password, mock_saving_new_password):
        reset_password_obj = {
            "current_password": "Admin@1234",
            "new_password": "Admin1234"}
        mock_matching_password.return_value = True
        mock_saving_new_password.return_value = {"data": {"message": "password changed successfully"}}, 200

        response = self.client.put("/user/reset_password", json=reset_password_obj, headers=self.access_token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'data' in response.data)
        self.assertTrue(b'current password should contain least 1 uppercase, 1 lowercase, 1 number, and 1 special character and maximum length is 20 and minimum length is 6' in response.data)

    @patch('user.api.saving_new_password')
    @patch('user.api.matching_password')
    def test_resetpassword6(self, mock_matching_password, mock_saving_new_password):
        reset_password_obj = {
            "current_password": "Admin@1234",
            "new_password": "Admin1234"}
        mock_matching_password.return_value = False
        mock_saving_new_password.return_value = {"data": {"message": "password changed successfully"}}, 200

        response = self.client.put("/user/reset_password", json=reset_password_obj, headers=self.access_token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'data' in response.data)
        self.assertTrue(b'incorrect password' in response.data)

    @patch('user.api.saving_updated_profile')
    @patch('user.api.checking_mail_exist')
    @patch('user.api.checking_new_and_old_mail_not_same')
    def test_update_profile1(self, mock_checking_new_and_old_mail_not_same, mock_checking_mail_exist,mock_saving_updated_profile):
        update_profile_obj = {
            "name": "Test Person",
            "email_id": "test@gmail.com",
            "phone": "6887779999",
            "address": "address"}
        mock_checking_new_and_old_mail_not_same.return_value = False
        mock_checking_mail_exist.return_value=True
        mock_saving_updated_profile.return_value = {"data": {"message": 'profile updated successfully'}}, 200

        response = self.client.put("/user/update_profile", data=update_profile_obj, headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'data' in response.data)
        self.assertTrue(b'profile updated successfully' in response.data)

    @patch('user.api.saving_updated_profile')
    @patch('user.api.checking_mail_exist')
    @patch('user.api.checking_new_and_old_mail_not_same')
    def test_update_profile2(self, mock_checking_new_and_old_mail_not_same, mock_checking_mail_exist,
                            mock_saving_updated_profile):
        update_profile_obj = {
            "name": "Test Person",
            "email_id": "test",
            "phone": "6887779999",
            "address": "address"}
        mock_checking_new_and_old_mail_not_same.return_value = False
        mock_checking_mail_exist.return_value = True
        mock_saving_updated_profile.return_value = {"data": {"message": 'profile updated successfully'}}, 200

        response = self.client.put("/user/update_profile", data=update_profile_obj, headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'data' in response.data)
        self.assertTrue(b'provide valid email' in response.data)

    @patch('user.api.saving_updated_profile')
    @patch('user.api.checking_mail_exist')
    @patch('user.api.checking_new_and_old_mail_not_same')
    def test_update_profile3(self, mock_checking_new_and_old_mail_not_same, mock_checking_mail_exist,
                            mock_saving_updated_profile):
        update_profile_obj = {
            "name": "Test Person",
            "email_id": "test@gmail.com",
            "phone": "6787813999",
            "address": ""}
        mock_checking_new_and_old_mail_not_same.return_value = False
        mock_checking_mail_exist.return_value = True
        mock_saving_updated_profile.return_value = {"data": {"message": 'profile updated successfully'}}, 200

        response = self.client.put("/user/update_profile", data=update_profile_obj, headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'data' in response.data)
        self.assertTrue(b'provide address' in response.data)

    @patch('user.api.saving_updated_profile')
    @patch('user.api.checking_mail_exist')
    @patch('user.api.checking_new_and_old_mail_not_same')
    def test_update_profile4(self, mock_checking_new_and_old_mail_not_same, mock_checking_mail_exist,
                            mock_saving_updated_profile):
        update_profile_obj = {
            "name": "Test Person",
            "email_id": "",
            "phone": "6787813999",
            "address": "address"}
        mock_checking_new_and_old_mail_not_same.return_value = False
        mock_checking_mail_exist.return_value = True
        mock_saving_updated_profile.return_value = {"data": {"message": 'profile updated successfully'}}, 200

        response = self.client.put("/user/update_profile", data=update_profile_obj, headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'data' in response.data)
        self.assertTrue(b'provide email' in response.data)

    @patch('user.api.saving_updated_profile')
    @patch('user.api.checking_mail_exist')
    @patch('user.api.checking_new_and_old_mail_not_same')
    def test_update_profile5(self, mock_checking_new_and_old_mail_not_same, mock_checking_mail_exist,
                             mock_saving_updated_profile):
        update_profile_obj = {
            "name": "",
            "email_id": "test@gmail.com",
            "phone": "9876567898",
            "address": "address"}
        mock_checking_new_and_old_mail_not_same.return_value = False
        mock_checking_mail_exist.return_value = True
        mock_saving_updated_profile.return_value = {"data": {"message": 'profile updated successfully'}}, 200

        response = self.client.put("/user/update_profile", data=update_profile_obj, headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'data' in response.data)
        self.assertTrue(b'provide name' in response.data)

    @patch('user.api.saving_updated_profile')
    @patch('user.api.checking_mail_exist')
    @patch('user.api.checking_new_and_old_mail_not_same')
    def test_update_profile6(self, mock_checking_new_and_old_mail_not_same, mock_checking_mail_exist,
                             mock_saving_updated_profile):
        update_profile_obj = {
            "name": "Demo",
            "email_id": "test@gmail.com",
            "phone": "9",
            "address": "address"}
        mock_checking_new_and_old_mail_not_same.return_value = False
        mock_checking_mail_exist.return_value = True
        mock_saving_updated_profile.return_value = {"data": {"message": 'profile updated successfully'}}, 200

        response = self.client.put("/user/update_profile", data=update_profile_obj, headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'data' in response.data)
        self.assertTrue(b'phone number not valid' in response.data)

    @patch('user.api.saving_updated_profile')
    @patch('user.api.checking_mail_exist')
    @patch('user.api.checking_new_and_old_mail_not_same')
    def test_update_profile_1(self, mock_checking_new_and_old_mail_not_same, mock_checking_mail_exist,
                             mock_saving_updated_profile):
        update_profile_obj = {
            "name": "Demo",
            "email_id": "test@gmail.com",
            "phone": "",
            "address": "address"}
        mock_checking_new_and_old_mail_not_same.return_value = False
        mock_checking_mail_exist.return_value = True
        mock_saving_updated_profile.return_value = {"data": {"message": 'profile updated successfully'}}, 200

        response = self.client.put("/user/update_profile", data=update_profile_obj, headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'data' in response.data)
        self.assertTrue(b'provide phone' in response.data)

    @patch('user.api.displaying_user_profile')
    def test_get_profile(self, mock_displaying_user_profile):
        mock_displaying_user_profile.return_value = {"data": {"message": [
            {
                "address": "address",
                "email_id": "admin1@gmail.com",
                "name": "Admin11",
                "phone": 9999999999,
                "photo": "http://10.6.9.26:5000/static/profile/default.png"
            }
        ]}}

        response = self.client.get("/user/profile", headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'data' in response.data)
        self.assertTrue(b'address' in response.data)
        self.assertTrue(b'email_id' in response.data)
        self.assertTrue(b'phone' in response.data)
        self.assertTrue(b'photo' in response.data)
        self.assertTrue(b'name' in response.data)

if __name__=="__main__":
    unittest.main()
