try:
    import unittest
    from app import app
    from unittest.mock import Mock, patch
    from flask_jwt_extended import create_access_token, create_refresh_token
    import json
except Exception as e:
    print('Some modules are missing {}'.format(e))


class ApiTest1(unittest.TestCase):
    client=app.test_client()
    with app.app_context():
        access_token = dict(Authorization='Bearer ' + create_access_token(identity=1))
        refresh_token = dict(Authorization='Bearer ' + create_refresh_token(identity=1))

    @patch('user.api.user_mail_query')
    @patch('user.api.user_query')
    @patch('user.api.user_profile_commit')
    def test_signup1(self, mock_user_profile_commit, mock_user_query, mock_user_mail_query):
        signup_obj = {
            "email_id": "",
            "username": "testuser",
            "password": "Admin@123"}
        mock_user_profile_commit.return_value = {"data": {"message": "user created"}}, 200
        mock_user_query.return_value = None
        mock_user_mail_query.return_value = None
        response = self.client.post("/user/signup", json=signup_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error')
        self.assertTrue(b'email cannot be empty')

    @patch('user.api.user_mail_query')
    @patch('user.api.user_query')
    @patch('user.api.user_profile_commit')
    def test_signup2(self, mock_user_profile_commit, mock_user_query, mock_user_mail_query):
        signup_obj = {
            "email_id": "testuser@yahoo.com",
            "username": "",
            "password": "Admin@123"}
        mock_user_profile_commit.return_value = {"data": {"message": "user created"}}, 200
        mock_user_query.return_value = None
        mock_user_mail_query.return_value = None
        response = self.client.post("/user/signup", json=signup_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'username cannot be empty' in response.data)

    @patch('user.api.user_mail_query')
    @patch('user.api.user_query')
    @patch('user.api.user_profile_commit')
    def test_signup3(self, mock_user_profile_commit, mock_user_query,mock_user_mail_query):
        signup_obj = {
                      "email_id": "testuser@gmail.com",
                      "username": "testuser",
                      "password": "Admin@123"}
        mock_user_profile_commit.return_value={"data": {"message": "user created"}}, 200
        mock_user_query.return_value=None
        mock_user_mail_query.return_value=None
        response=self.client.post("/user/signup", json=signup_obj)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)

    @patch('user.api.user_mail_query')
    @patch('user.api.user_query')
    @patch('user.api.user_profile_commit')
    def test_signup4(self, mock_user_profile_commit, mock_user_query, mock_user_mail_query):
        signup_obj = {
            "email_id": "",
            "username": "Testuser@1",
            "password": "Admin@123"}
        mock_user_profile_commit.return_value = {"data": {"message": "user created"}}, 200
        mock_user_query.return_value = None
        mock_user_mail_query.return_value = None
        response = self.client.post("/user/signup", json=signup_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'email cannot be empty' in response.data)

    @patch('user.api.user_mail_query')
    @patch('user.api.user_query')
    @patch('user.api.user_profile_commit')
    def test_signup5(self, mock_user_profile_commit, mock_user_query, mock_user_mail_query):
        signup_obj = {
            "email_id": "testuser@gmail.com",
            "username": "Testuser1",
            "password": "Admin@123"}
        mock_user_profile_commit.return_value = {"data": {"message": "user created"}}, 200
        mock_user_query.return_value = "user"
        mock_user_mail_query.return_value = None
        response = self.client.post("/user/signup", json=signup_obj)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'username already exists' in response.data)

    @patch('user.api.user_mail_query')
    @patch('user.api.user_query')
    @patch('user.api.user_profile_commit')
    def test_signup6(self, mock_user_profile_commit, mock_user_query, mock_user_mail_query):
        signup_obj = {
            "email_id": "testuser@gmail.com",
            "username": "Testuser1",
            "password": "Admin@123"}
        mock_user_profile_commit.return_value = {"data": {"message": "user created"}}, 200
        mock_user_query.return_value = None
        mock_user_mail_query.return_value = "email"
        response = self.client.post("/user/signup", json=signup_obj)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'email already exists' in response.data)

    @patch('user.api.checking_userpassword')
    @patch('user.api.password_match')
    @patch('user.api.user_filter_db')
    def test_login1(self, mock_user_filter_db, mock_password_match, mock_checking_userpassword):
        login_obj = {
            "username": "vigdelh11",
            "password": "Admin@123"}
        mock_user_filter_db.return_value = None
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
    @patch('user.api.user_filter_db')
    def test_login2(self, mock_user_filter_db, mock_password_match, mock_checking_userpassword):
        login_obj = {
            "username": "vigdelh11",
            "password": "Admin@123"}
        mock_user_filter_db.return_value = "user"
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
    @patch('user.api.user_filter_db')
    def test_login3(self, mock_user_filter_db, mock_password_match, mock_checking_userpassword):
        login_obj = {
            "username": "vigdelh11",
            "password": "Admin@123"}
        mock_user_filter_db.return_value = "user"
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
        # login_obj = {
        #     "username": "testuser",
        #     "id": 1,
        #     "password": "Admin@123"}
        # identity=login_obj["id"]
        # with app.app_context():
        #     token=dict(Authorization='Bearer ' + create_refresh_token(identity=identity))
        response = self.client.get("/user/refresh", headers=self.refresh_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'access_token' in response.data)
        self.assertTrue(b'data' in response.data)

    def test_refresh2(self):
        response = self.client.get("/user/refresh")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content_type, "application/json")

    @patch('user.api.reset_password_db')
    @patch('user.api.matching_password')
    def test_resetpassword1(self, mock_matching_password, mock_reset_password_db):
        reset_password_obj = {
            "current_password": "Admin@123",
            "new_password": "Admin@1234"}
        mock_matching_password.return_value = True
        mock_reset_password_db.return_value = {"data": {"message": "password changed successfully"}}, 200

        response = self.client.put("/user/reset_password", json=reset_password_obj, headers= self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'data' in response.data)
        self.assertTrue(b'password changed successfully' in response.data)

    @patch('user.api.reset_password_db')
    @patch('user.api.matching_password')
    def test_resetpassword2(self, mock_matching_password, mock_reset_password_db):
        reset_password_obj = {
            "current_password": "",
            "new_password": "Admin@1234"}
        mock_matching_password.return_value = True
        mock_reset_password_db.return_value = {"data": {"message": "password changed successfully"}}, 200

        response = self.client.put("/user/reset_password", json=reset_password_obj, headers=self.access_token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'data' in response.data)
        self.assertTrue(b' provide current password' in response.data)

    @patch('user.api.reset_password_db')
    @patch('user.api.matching_password')
    def test_resetpassword3(self, mock_matching_password, mock_reset_password_db):
        reset_password_obj = {
            "current_password": "Admin@1234",
            "new_password": ""}
        mock_matching_password.return_value = True
        mock_reset_password_db.return_value = {"data": {"message": "password changed successfully"}}, 200

        response = self.client.put("/user/reset_password", json=reset_password_obj, headers=self.access_token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'data' in response.data)
        self.assertTrue(b'provide new password' in response.data)

    @patch('user.api.reset_password_db')
    @patch('user.api.matching_password')
    def test_resetpassword4(self, mock_matching_password, mock_reset_password_db):
        reset_password_obj = {
            "current_password": "Admin@1234",
            "new_password": "Admin@1234"}
        mock_matching_password.return_value = True
        mock_reset_password_db.return_value = {"data": {"message": "password changed successfully"}}, 200

        response = self.client.put("/user/reset_password", json=reset_password_obj, headers=self.access_token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'data' in response.data)
        self.assertTrue(b'new password should not be same as previous password' in response.data)

    @patch('user.api.reset_password_db')
    @patch('user.api.matching_password')
    def test_resetpassword4(self, mock_matching_password, mock_reset_password_db):
        reset_password_obj = {
            "current_password": "Admin@1234",
            "new_password": "Admin1234"}
        mock_matching_password.return_value = True
        mock_reset_password_db.return_value = {"data": {"message": "password changed successfully"}}, 200

        response = self.client.put("/user/reset_password", json=reset_password_obj, headers=self.access_token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'data' in response.data)
        self.assertTrue(b'current password should contain least 1 uppercase, 1 lowercase, 1 number, and 1 special character and maximum length is 20 and minimum length is 8' in response.data)

    @patch('user.api.reset_password_db')
    @patch('user.api.matching_password')
    def test_resetpassword5(self, mock_matching_password, mock_reset_password_db):
        reset_password_obj = {
            "current_password": "Admin@1234",
            "new_password": "Admin1234"}
        mock_matching_password.return_value = False
        mock_reset_password_db.return_value = {"data": {"message": "password changed successfully"}}, 200

        response = self.client.put("/user/reset_password", json=reset_password_obj, headers=self.access_token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'data' in response.data)
        self.assertTrue(b'incorrect password' in response.data)


    @patch('advertisement.api.get_every_categories')
    def test_list_every_categories(self, mock_get_every_category):
        mock_get_every_category.return_value={"data": {
        "message": [
            {
                "id": 1,
                "images": "http://10.6.9.26:5000/static/catagory/mobile.svg",
                "name": "Mobiles",
                "sub_category": [
                    {
                        "id": 12,
                        "name": "Mobile Phones"
                    },
                    {
                        "id": 13,
                        "name": "Accessories"
                    },
                    {
                        "id": 14,
                        "name": "Tablets"
                    },
                    {
                        "id": 15,
                        "name": "Telephone"
                    }
                    ]
            }]}}, 200

        response = self.client.get("/ad/list_every_category")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'id' in response.data)
        self.assertTrue(b'images' in response.data)
        self.assertTrue(b'name' in response.data)
        self.assertTrue(b'sub_category' in response.data)
        self.assertTrue(b'data' in response.data)

    @patch('advertisement.api.get_only_categories')
    def test_list_only_categories(self, mock_get_only_category):
        mock_get_only_category.return_value={
        "data": {
            "message": [
                {
                    "id": 1,
                    "images": "http://10.6.9.26:5000/static/catagory/mobile.svg",
                    "name": "Mobiles"
                }]}}, 200
        response = self.client.get("/ad/category")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'id' in response.data)
        self.assertTrue(b'images' in response.data)
        self.assertTrue(b'name' in response.data)
        self.assertTrue(b'data' in response.data)

    @patch('advertisement.api.ads_plan')
    def test_list_ad_plan(self, mock_ads_plan):
        mock_ads_plan.return_value={
            "data": {
            "message": [
                {"days": 30, "id": 4, "price": 3200.0 }]}
        }, 200
        response = self.client.get("/ad/ad_plan")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'data' in response.data)
        self.assertTrue(b'price' in response.data)
        self.assertTrue(b'days' in response.data)
        self.assertTrue(b'data' in response.data)

    @patch('advertisement.api.category_delete')
    @patch('advertisement.api.admin_is_true')
    def test_delete_category1(self, mock_admin_is_true, mock_category_delete):
        mock_admin_is_true.return_value = True
        mock_category_delete.return_value = {"data": {"message": "category removed"}}, 200
        response = self.client.delete("/ad/category_delete/1", headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'category removed' in response.data)
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'data' in response.data)


    @patch('advertisement.api.category_delete')
    @patch('advertisement.api.admin_is_true')
    def test_delete_category2(self, mock_admin_is_true, mock_category_delete):
        mock_admin_is_true.return_value = False
        mock_category_delete.return_value = {"data": {"message": "category removed"}}, 200
        response = self.client.delete("/ad/category_delete/1", headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'data' in response.data)
        self.assertTrue(b'only admin can access this route' in response.data)

    @patch('advertisement.api.add_categories')
    @patch('advertisement.api.admin_is_true')
    def test_add_category1(self, mock_admin_is_true, mock_add_categories):
        mock_admin_is_true.return_value = True
        mock_add_categories.return_value = {"data": {"message": "Category created"}}, 200
        response = self.client.post("/ad/add_category", headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'Category created' in response.data)
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'data' in response.data)

    @patch('advertisement.api.add_categories')
    @patch('advertisement.api.admin_is_true')
    def test_add_category2(self, mock_admin_is_true, mock_add_categories):
        mock_admin_is_true.return_value = False
        mock_add_categories.return_value = {"data": {"message": "category removed"}}, 200
        response = self.client.post("/ad/add_category", headers=self.access_token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'only admin can add category' in response.data)
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'error' in response.data)

    @patch('advertisement.api.change_categories')
    @patch('advertisement.api.admin_is_true')
    def test_change_category(self, mock_admin_is_true, mock_change_categories):
        mock_admin_is_true.return_value = True
        mock_change_categories.return_value = {"data": {"message": "Category updated"}}, 200
        response = self.client.put("/ad/update_category/1", headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'Category updated' in response.data)

    @patch('advertisement.api.change_categories')
    @patch('advertisement.api.admin_is_true')
    def test_change_category2(self, mock_admin_is_true, mock_change_categories):
        mock_admin_is_true.return_value = False
        mock_change_categories.return_value = {"data": {"message": "Category updated"}}, 200
        response = self.client.put("/ad/update_category/1", headers=self.access_token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'only admin can update category' in response.data)

if __name__=="__main__":
    unittest.main()
