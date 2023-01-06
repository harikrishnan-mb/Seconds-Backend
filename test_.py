try:
    import unittest
    from app import app
    from unittest.mock import Mock, patch
    from flask_jwt_extended import create_access_token, create_refresh_token
    import json
    from user.api import hashing_password
except Exception as e:
    print('Some modules are missing {}'.format(e))


class ApiTest(unittest.TestCase):
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

    def test_hashing_password(self):
        self.assertNotEqual(hashing_password("password"), "password")

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
        self.assertTrue(b'provide current password' in response.data)

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

    @patch('advertisement.api.category_update')
    @patch('advertisement.api.category_delete')
    @patch('advertisement.api.admin_is_true')
    def test_delete_category1(self, mock_admin_is_true, mock_category_delete,mock_category_update):
        mock_admin_is_true.return_value = True
        mock_category_update.return_value=True
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

    @patch('advertisement.api.category_update')
    @patch('advertisement.api.category_delete')
    @patch('advertisement.api.admin_is_true')
    def test_delete_category3(self, mock_admin_is_true, mock_category_delete, mock_category_update):
        mock_admin_is_true.return_value = True
        mock_category_update.return_value = False
        mock_category_delete.return_value = {"data": {"message": "category removed"}}, 200
        response = self.client.delete("/ad/category_delete/1", headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'category does not exist' in response.data)
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'data' in response.data)


    @patch('advertisement.api.add_categories')
    @patch('advertisement.api.admin_is_true')
    def test_add_category1(self, mock_admin_is_true, mock_add_categories):
        category_obj={"category":"Test1", "file":"", "parent_id":1}
        mock_admin_is_true.return_value = True
        mock_add_categories.return_value = {"data": {"message": "Category created"}}, 200
        response = self.client.post("/ad/add_category", headers=self.access_token, data=category_obj)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'Category created' in response.data)
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'data' in response.data)

    @patch('advertisement.api.add_categories')
    @patch('advertisement.api.admin_is_true')
    def test_add_category2(self, mock_admin_is_true, mock_add_categories):
        mock_admin_is_true.return_value = False
        mock_add_categories.return_value = {"data": {"message": "Category created"}}, 200
        response = self.client.post("/ad/add_category", headers=self.access_token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'only admin can add category' in response.data)
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'error' in response.data)

    @patch('advertisement.api.category_update')
    @patch('advertisement.api.change_categories')
    @patch('advertisement.api.admin_is_true')
    def test_change_category(self, mock_admin_is_true, mock_change_categories, mock_category_update):
        category_obj = {"category": "Test1", "file": "", "parent_id": 1}
        mock_admin_is_true.return_value = True
        mock_category_update.return_value=True
        mock_change_categories.return_value = {"data": {"message": "Category updated"}}, 200
        response = self.client.put("/ad/update_category/1", headers=self.access_token, data=category_obj)
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

    @patch('advertisement.api.category_update')
    @patch('advertisement.api.change_categories')
    @patch('advertisement.api.admin_is_true')
    def test_change_category3(self, mock_admin_is_true, mock_change_categories, mock_category_update):
        category_obj = {"category": "Test1", "file": "", "parent_id": 1}
        mock_admin_is_true.return_value = True
        mock_category_update.return_value = False
        mock_change_categories.return_value = {"data": {"message": "Category updated"}}, 200
        response = self.client.put("/ad/update_category/1", headers=self.access_token, data=category_obj)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'category id does not exist' in response.data)

    @patch('advertisement.api.create_ad_plan_db')
    @patch('advertisement.api.create_ad_category_db')
    @patch('advertisement.api.create_ad_db')
    def test_create_ad1(self, mock_create_ad_db,mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj={"category_id": "", "status": "active", "title": "BMW Car", "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1", "negotiable_product": "True", "feature_product":"True","price": "5000", "location": "Kochi", "latitude": "9.9", "longitude": "76.2", "seller_name":"Aadi", "phone": 7897987890, "email_id": "testuser@gmail.com", "images":['default.jpg']}
        image_obj={"images":['default.jpg']}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value="category"
        mock_create_ad_plan_db.return_value="ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide category id' in response.data)

    @patch('advertisement.api.create_ad_plan_db')
    @patch('advertisement.api.create_ad_category_db')
    @patch('advertisement.api.create_ad_db')
    def test_create_ad2(self, mock_create_ad_db,mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "1", "status": "active", "title": "BMW Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5000", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images":['default.jpg']}
        image_obj = {"images": ['default.jpg']}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'ad created' in response.data)

    @patch('advertisement.api.create_ad_plan_db')
    @patch('advertisement.api.create_ad_category_db')
    @patch('advertisement.api.create_ad_db')
    def test_create_ad3(self, mock_create_ad_db,mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "1aca", "status": "active", "title": "BMW Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5000", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images":['default.jpg']}
        image_obj = {"images": ['default.jpg']}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide category id as integer' in response.data)

    @patch('advertisement.api.create_ad_plan_db')
    @patch('advertisement.api.create_ad_category_db')
    @patch('advertisement.api.create_ad_db')
    def test_create_ad4(self, mock_create_ad_db,mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "1", "status": "active", "title": "BMW Car",
                         "description": "5000 km run car for sale", "seller_type": "", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5000", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": ['default.jpg']}
        image_obj = {"images": ['default.jpg']}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide seller_type' in response.data)

    @patch('advertisement.api.create_ad_plan_db')
    @patch('advertisement.api.create_ad_category_db')
    @patch('advertisement.api.create_ad_db')
    def test_create_ad5(self, mock_create_ad_db,mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "1", "status": "active", "title": "",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5000", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images":['default.jpg']}
        image_obj = {"images": ['default.txt']}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide title' in response.data)

    @patch('advertisement.api.create_ad_plan_db')
    @patch('advertisement.api.create_ad_category_db')
    @patch('advertisement.api.create_ad_db')
    def test_create_ad6(self, mock_create_ad_db,mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "1", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5000", "location": "",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": ['default.jpg']}
        image_obj = {"images": ['default.txt']}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide location' in response.data)

    @patch('advertisement.api.create_ad_plan_db')
    @patch('advertisement.api.create_ad_category_db')
    @patch('advertisement.api.create_ad_db')
    def test_create_ad7(self, mock_create_ad_db,mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "1", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "",
                         "negotiable_product": "True", "feature_product": "True", "price": "5000", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": ['default.jpg']}
        image_obj = {"images": ['default.txt']}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide advertisement plan id' in response.data)

    @patch('advertisement.api.create_ad_plan_db')
    @patch('advertisement.api.create_ad_category_db')
    @patch('advertisement.api.create_ad_db')
    def test_create_ad8(self, mock_create_ad_db,mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "1", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "sd",
                         "negotiable_product": "True", "feature_product": "True", "price": "5000", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": ['default.jpg']}
        image_obj = {"images": ['default.txt']}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide advertisement plan id as integer' in response.data)

    @patch('advertisement.api.create_ad_plan_db')
    @patch('advertisement.api.create_ad_category_db')
    @patch('advertisement.api.create_ad_db')
    def test_create_ad9(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "1", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "24",
                         "negotiable_product": "True", "feature_product": "True", "price": "5000", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": ['default.jpg']}
        image_obj = {"images": ['default.txt']}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = None
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'advertisement plan id not found' in response.data)

    @patch('advertisement.api.create_ad_plan_db')
    @patch('advertisement.api.create_ad_category_db')
    @patch('advertisement.api.create_ad_db')
    def test_create_ad10(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "234", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5000", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": ['default.jpg']}
        image_obj = {"images": ['default.txt']}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = None
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'category id not found' in response.data)

    @patch('advertisement.api.create_ad_plan_db')
    @patch('advertisement.api.create_ad_category_db')
    @patch('advertisement.api.create_ad_db')
    def test_create_ad11(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "sdcsc", "feature_product": "True", "price": "5000", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": ['default.jpg']}
        image_obj = {"images": ['default.txt']}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide product is negotiable or not as True or False' in response.data)

    @patch('advertisement.api.create_ad_plan_db')
    @patch('advertisement.api.create_ad_category_db')
    @patch('advertisement.api.create_ad_db')
    def test_create_ad12(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "", "feature_product": "True", "price": "5000", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": ['default.jpg']}
        image_obj = {"images": ['default.txt']}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide product is negotiable or not' in response.data)

    @patch('advertisement.api.create_ad_plan_db')
    @patch('advertisement.api.create_ad_category_db')
    @patch('advertisement.api.create_ad_db')
    def test_create_ad13(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "", "price": "5000", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": ['default.jpg']}
        image_obj = {"images": ['default.txt']}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide product is featured or not' in response.data)

    @patch('advertisement.api.create_ad_plan_db')
    @patch('advertisement.api.create_ad_category_db')
    @patch('advertisement.api.create_ad_db')
    def test_create_ad14(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "afda", "price": "5000", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": ['default.jpg']}
        image_obj = {"images": ['default.txt']}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide product is featured or not as True or False' in response.data)

    @patch('advertisement.api.create_ad_plan_db')
    @patch('advertisement.api.create_ad_category_db')
    @patch('advertisement.api.create_ad_db')
    def test_create_ad15(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "dgh", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": ['default.jpg']}
        image_obj = {"images": ['default.txt']}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide price as floating number' in response.data)

    @patch('advertisement.api.create_ad_plan_db')
    @patch('advertisement.api.create_ad_category_db')
    @patch('advertisement.api.create_ad_db')
    def test_create_ad16(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": ['default.jpg']}
        image_obj = {"images": ['default.txt']}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide price' in response.data)

    @patch('advertisement.api.create_ad_plan_db')
    @patch('advertisement.api.create_ad_category_db')
    @patch('advertisement.api.create_ad_db')
    def test_create_ad17(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": ['default.jpg']}
        image_obj = {"images": ['default.txt']}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide latitude' in response.data)

    @patch('advertisement.api.create_ad_plan_db')
    @patch('advertisement.api.create_ad_category_db')
    @patch('advertisement.api.create_ad_db')
    def test_create_ad17(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": ['default.jpg']}
        image_obj = {"images": ['default.txt']}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide latitude' in response.data)

    @patch('advertisement.api.create_ad_plan_db')
    @patch('advertisement.api.create_ad_category_db')
    @patch('advertisement.api.create_ad_db')
    def test_create_ad18(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": "",
                         "email_id": "testuser@gmail.com", "images": ['default.jpg']}
        image_obj = {"images": ['default.txt']}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide phone number' in response.data)

    @patch('advertisement.api.create_ad_plan_db')
    @patch('advertisement.api.create_ad_category_db')
    @patch('advertisement.api.create_ad_db')
    def test_create_ad19(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": "235425",
                         "email_id": "testuser@gmail.com", "images": ['default.jpg']}
        image_obj = {"images": ['default.txt']}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide valid phone number' in response.data)

    @patch('advertisement.api.create_ad_plan_db')
    @patch('advertisement.api.create_ad_category_db')
    @patch('advertisement.api.create_ad_db')
    def test_create_ad20(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 6786786789,
                         "email_id": "testuser", "images": ['default.jpg']}
        image_obj = {"images": ['default.txt']}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide valid email' in response.data)

    @patch('advertisement.api.update_ad_id_db')
    @patch('advertisement.api.create_ad_plan_db')
    @patch('advertisement.api.create_ad_category_db')
    @patch('advertisement.api.update_ad_db')
    def test_update_ad1(self,mock_update_ad_db,mock_create_ad_category_db, mock_create_ad_plan_db,mock_update_ad_id_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": ['default.jpg']}
        image_obj = {"images": ['default.txt']}
        mock_update_ad_db.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        mock_update_ad_id_db.return_value=True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'ad edited successfully' in response.data)

    @patch('advertisement.api.update_ad_id_db')
    @patch('advertisement.api.create_ad_plan_db')
    @patch('advertisement.api.create_ad_category_db')
    @patch('advertisement.api.update_ad_db')
    def test_update_ad1(self, mock_update_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db,
                        mock_update_ad_id_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": ['default.jpg']}
        image_obj = {"images": ['default.txt']}
        mock_update_ad_db.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        mock_update_ad_id_db.return_value = False
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'only owner can edit ad' in response.data)

    @patch('advertisement.api.ad_id_and_person')
    @patch('advertisement.api.del_ad_filter_adv')
    @patch('advertisement.api.delete_ad_person')
    def test_delete_ad(self, mock_delete_ad_person, mock_del_ad_filter_adv, mock_ad_id_and_person):
        mock_delete_ad_person.return_value = {"data": {"message": "ad deleted"}}
        mock_del_ad_filter_adv.return_value = "ad"
        mock_ad_id_and_person.return_value= True
        response = self.client.delete("/ad/delete_ad/1", headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'ad deleted' in response.data)

    @patch('advertisement.api.ad_id_and_person')
    @patch('advertisement.api.del_ad_filter_adv')
    @patch('advertisement.api.delete_ad_person')
    def test_delete_ad(self, mock_delete_ad_person, mock_del_ad_filter_adv, mock_ad_id_and_person):
        mock_delete_ad_person.return_value = {"data": {"message": "ad deleted"}}
        mock_del_ad_filter_adv.return_value = "ad"
        mock_ad_id_and_person.return_value = True
        response = self.client.delete("/ad/delete_ad/1", headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'ad deleted' in response.data)

    @patch('advertisement.api.ad_id_and_person')
    @patch('advertisement.api.del_ad_filter_adv')
    @patch('advertisement.api.delete_ad_person')
    def test_delete_ad1(self, mock_delete_ad_person, mock_del_ad_filter_adv, mock_ad_id_and_person):
        mock_delete_ad_person.return_value = {"data": {"message": "ad deleted"}}
        mock_del_ad_filter_adv.return_value = None
        mock_ad_id_and_person.return_value = True
        response = self.client.delete("/ad/delete_ad/1", headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'ad not found' in response.data)
if __name__=="__main__":
    unittest.main()
