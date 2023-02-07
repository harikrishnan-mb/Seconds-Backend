try:
    import unittest
    from app import app
    import os
    import io
    from unittest.mock import Mock, patch
    from advertisement.models import Category, Advertisement, AdPlan, AdImage, ReportAd, FavouriteAd
    from flask_jwt_extended import create_access_token, create_refresh_token
    import json
    from advertisement.api import Category, generate_random_text
    from user.api import check_if_token_is_revoked
    import redis
except Exception as e:
    print('Some modules are missing {}'.format(e))


class ApiTest2(unittest.TestCase):
    client=app.test_client()
    with app.app_context():
        access_token = dict(Authorization='Bearer ' + create_access_token(identity=1))
        refresh_token = dict(Authorization='Bearer ' + create_refresh_token(identity=1))

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

    @patch('advertisement.api.deleting_the_category')
    @patch('advertisement.api.filtering_category')
    @patch('advertisement.api.admin_is_true')
    def test_delete_category_sucess_message(self, mock_admin_is_true, mock_filtering_category,mock_deleting_the_category):
        mock_admin_is_true.return_value = True
        mock_filtering_category.return_value=True
        mock_deleting_the_category.return_value={"data": {"message": "category removed"}}, 200
        response = self.client.delete("/ad/category_delete/1", headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'category removed' in response.data)
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'data' in response.data)

    @patch('advertisement.api.deleting_the_category')
    @patch('advertisement.api.filtering_category')
    @patch('advertisement.api.admin_is_true')
    def test_delete_category_error_in_category(self, mock_admin_is_true, mock_filtering_category,mock_deleting_the_category):
        mock_admin_is_true.return_value = True
        mock_filtering_category.return_value = ''
        mock_deleting_the_category.return_value = {"data": {"message": "category removed"}}, 200
        response = self.client.delete("/ad/category_delete/1", headers=self.access_token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'category does not exist' in response.data)
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'data' in response.data)

    @patch('advertisement.api.deleting_the_category')
    @patch('advertisement.api.filtering_category')
    @patch('advertisement.api.admin_is_true')
    def test_delete_category_error_admin_can_access_route(self, mock_admin_is_true, mock_filtering_category, mock_deleting_the_category):
        mock_admin_is_true.return_value = False
        mock_filtering_category.return_value = ''
        mock_deleting_the_category.return_value = {"data": {"message": "category removed"}}, 200
        response = self.client.delete("/ad/category_delete/1", headers=self.access_token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'only admin can access this route' in response.data)
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'data' in response.data)

    @patch('advertisement.api.adding_category_to_db')
    @patch('advertisement.api.checking_parent_id_exist')
    @patch('advertisement.api.checking_category_name_already_exist')
    @patch('advertisement.api.admin_is_true')
    def test_add_category_message_category_added(self, mock_admin_is_true, mock_checking_category_name_already_exist,mock_checking_parent_id_exist, mock_adding_category_to_db):
        category_add={"category": "Demo", "file":'', "parent_id":"24"}
        mock_admin_is_true.return_value = True
        mock_checking_category_name_already_exist.return_value = False
        mock_checking_parent_id_exist.return_value = True
        mock_adding_category_to_db.return_value = {"data": {"message": "Category added"}}, 200
        response = self.client.post("/ad/add_category", headers=self.access_token, data=category_add)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'Category added' in response.data)
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'data' in response.data)
    @patch('advertisement.api.adding_category_to_db')
    @patch('advertisement.api.checking_parent_id_exist')
    @patch('advertisement.api.checking_category_name_already_exist')
    @patch('advertisement.api.admin_is_true')
    def test_add_category_error_admin_can_access_this(self, mock_admin_is_true, mock_checking_category_name_already_exist,mock_checking_parent_id_exist,mock_adding_category_to_db):
        category_add = {"category": "Demo", "file": 'default.jpg', "parent_id": "24"}
        mock_admin_is_true.return_value = False
        mock_checking_category_name_already_exist.return_value = True
        mock_checking_parent_id_exist.return_value = True
        mock_adding_category_to_db.return_value={"data": {"message": "Category added"}}, 200
        response = self.client.post("/ad/add_category", headers=self.access_token, data=category_add)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'only admin can add category' in response.data)
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'error' in response.data)

    @patch('advertisement.api.adding_category_to_db')
    @patch('advertisement.api.checking_parent_id_exist')
    @patch('advertisement.api.checking_category_name_already_exist')
    @patch('advertisement.api.admin_is_true')
    def test_add_category_error_provide_category_id_or_image(self, mock_admin_is_true,
                                                      mock_checking_category_name_already_exist,
                                                      mock_checking_parent_id_exist, mock_adding_category_to_db):
        category_add = {"category": "Demo", "file": (io.BytesIO(b'static/iphone13pro.svg'), "iphone13pro.svg"), "parent_id": "24"}
        mock_admin_is_true.return_value = True
        mock_checking_category_name_already_exist.return_value = False
        mock_checking_parent_id_exist.return_value = True
        mock_adding_category_to_db.return_value = {"data": {"message": "Category added"}}, 200
        response = self.client.post("/ad/add_category", headers=self.access_token, data=category_add)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'provide image if category and provide parent_id if sub category' in response.data)
        self.assertTrue(b'error' in response.data)

    @patch('advertisement.api.adding_category_to_db')
    @patch('advertisement.api.checking_parent_id_exist')
    @patch('advertisement.api.checking_category_name_already_exist')
    @patch('advertisement.api.admin_is_true')
    def test_add_category_error_provide_category_id_or_image_atleast(self, mock_admin_is_true, mock_checking_category_name_already_exist, mock_checking_parent_id_exist, mock_adding_category_to_db):
        category_add = {"category": "Demo", "parent_id": ''}
        mock_admin_is_true.return_value = True
        mock_checking_category_name_already_exist.return_value = False
        mock_checking_parent_id_exist.return_value = True
        mock_adding_category_to_db.return_value = {"data": {"message": "Category added"}}, 200
        response = self.client.post("/ad/add_category", headers=self.access_token, data=category_add)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'provide parent_id or file' in response.data)
        self.assertTrue(b'error' in response.data)

    @patch('advertisement.api.adding_category_to_db')
    @patch('advertisement.api.checking_parent_id_exist')
    @patch('advertisement.api.checking_category_name_already_exist')
    @patch('advertisement.api.admin_is_true')
    def test_add_category_error_provide_parent_id_as_integer(self, mock_admin_is_true, mock_checking_category_name_already_exist, mock_checking_parent_id_exist, mock_adding_category_to_db):
        category_add = {"category": "Demo", "parent_id": 'hsagfcgh'}
        mock_admin_is_true.return_value = True
        mock_checking_category_name_already_exist.return_value = False
        mock_checking_parent_id_exist.return_value = False
        mock_adding_category_to_db.return_value = {"data": {"message": "Category added"}}, 200
        response = self.client.post("/ad/add_category", headers=self.access_token, data=category_add)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'parent_id should be integer' in response.data)
        self.assertTrue(b'error' in response.data)

    @patch('advertisement.api.adding_category_to_db')
    @patch('advertisement.api.checking_parent_id_exist')
    @patch('advertisement.api.checking_category_name_already_exist')
    @patch('advertisement.api.admin_is_true')
    def test_add_category_error_category_name_already_exists(self, mock_admin_is_true, mock_checking_category_name_already_exist, mock_checking_parent_id_exist, mock_adding_category_to_db):
        category_add = {"category": "Demo", "parent_id": 12}
        mock_admin_is_true.return_value = True
        mock_checking_category_name_already_exist.return_value = True
        mock_checking_parent_id_exist.return_value = False
        mock_adding_category_to_db.return_value = {"data": {"message": "Category added"}}, 200
        response = self.client.post("/ad/add_category", headers=self.access_token, data=category_add)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'category already exist' in response.data)
        self.assertTrue(b'error' in response.data)

    @patch('advertisement.api.adding_category_to_db')
    @patch('advertisement.api.checking_parent_id_exist')
    @patch('advertisement.api.checking_category_name_already_exist')
    @patch('advertisement.api.admin_is_true')
    def test_add_category_error_parent_id_is_not_id_of_any_category(self, mock_admin_is_true, mock_checking_category_name_already_exist, mock_checking_parent_id_exist, mock_adding_category_to_db):
        category_add = {"category": "Demo", "parent_id": 12}
        mock_admin_is_true.return_value = True
        mock_checking_category_name_already_exist.return_value = False
        mock_checking_parent_id_exist.return_value = False
        mock_adding_category_to_db.return_value = {"data": {"message": "Category added"}}, 200
        response = self.client.post("/ad/add_category", headers=self.access_token, data=category_add)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'parent_id should be id of any category' in response.data)
        self.assertTrue(b'error' in response.data)

    @patch('advertisement.api.adding_category_to_db')
    @patch('advertisement.api.checking_parent_id_exist')
    @patch('advertisement.api.checking_category_name_already_exist')
    @patch('advertisement.api.admin_is_true')
    def test_add_category_error_image_should_be_svg(self, mock_admin_is_true,mock_checking_category_name_already_exist,mock_checking_parent_id_exist, mock_adding_category_to_db):
        category_add = {"category": "Demo", "file": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg"), "parent_id": ''}
        mock_admin_is_true.return_value = True
        mock_checking_category_name_already_exist.return_value = False
        mock_checking_parent_id_exist.return_value = False
        mock_adding_category_to_db.return_value = {"data": {"message": "Category added"}}, 200
        response = self.client.post("/ad/add_category", headers=self.access_token, data=category_add)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'image should be svg' in response.data)
        self.assertTrue(b'error' in response.data)

    def test_generate_random_string(self):
        self.assertNotEqual(generate_random_text(), "hdcxwhlkwchc")

    @patch('advertisement.api.checking_new_and_old_category_name_not_same')
    @patch('advertisement.api.updating_category_in_db')
    @patch('advertisement.api.checking_parent_id_exist')
    @patch('advertisement.api.filtering_category')
    @patch('advertisement.api.checking_category_name_already_exist')
    @patch('advertisement.api.admin_is_true')
    def test_change_category_message_category_updated(self, mock_admin_is_true, mock_checking_category_name_already_exist,mock_filtering_category,mock_checking_parent_id_exist,mock_updating_category_in_db,mock_checking_new_and_old_category_name_not_same):
        category_add = {"category": "Demo", "file": '', "parent_id": "24"}
        mock_admin_is_true.return_value = True
        mock_checking_category_name_already_exist.return_value = False
        mock_checking_parent_id_exist.return_value = True
        mock_checking_new_and_old_category_name_not_same.return_value=True
        mock_filtering_category.return_value=Category
        mock_updating_category_in_db.return_value = {"data": {"message": "Category updated"}}, 200
        response = self.client.put("/ad/update_category/1", headers=self.access_token, data=category_add)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'Category updated' in response.data)

    @patch('advertisement.api.admin_is_true')
    def test_change_category_only_admin_can_access(self, mock_admin_is_true):
        mock_admin_is_true.return_value = False
        response = self.client.put("/ad/update_category/1", headers=self.access_token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'only admin can update category' in response.data)

    @patch('advertisement.api.checking_new_and_old_category_name_not_same')
    @patch('advertisement.api.updating_category_in_db')
    @patch('advertisement.api.checking_parent_id_exist')
    @patch('advertisement.api.filtering_category')
    @patch('advertisement.api.checking_category_name_already_exist')
    @patch('advertisement.api.admin_is_true')
    def test_change_category_error_category_id_not_found(self, mock_admin_is_true, mock_checking_category_name_already_exist,mock_filtering_category,mock_checking_parent_id_exist,mock_updating_category_in_db, mock_checking_new_and_old_category_name_not_same):
        category_add = {"category": "Demo", "file": '', "parent_id": "24"}
        mock_admin_is_true.return_value = True
        mock_checking_category_name_already_exist.return_value = False
        mock_checking_parent_id_exist.return_value = True
        mock_filtering_category.return_value = False
        mock_checking_new_and_old_category_name_not_same=True
        mock_updating_category_in_db.return_value = {"data": {"message": "Category updated"}}, 200
        response = self.client.put("/ad/update_category/1", headers=self.access_token, data=category_add)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'category id does not exist' in response.data)

    @patch('advertisement.api.checking_new_and_old_category_name_not_same')
    @patch('advertisement.api.updating_category_in_db')
    @patch('advertisement.api.checking_parent_id_exist')
    @patch('advertisement.api.filtering_category')
    @patch('advertisement.api.checking_category_name_already_exist')
    @patch('advertisement.api.admin_is_true')
    def test_change_category_error_category_already_exist(self, mock_admin_is_true, mock_checking_category_name_already_exist, mock_filtering_category, mock_checking_parent_id_exist, mock_updating_category_in_db, mock_checking_new_and_old_category_name_not_same):
        category_add = {"category": "Demo", "file": (io.BytesIO(b'static/iphone13pro.svg'), "iphone13pro.svg"), "parent_id": 11}
        mock_admin_is_true.return_value = True
        mock_checking_category_name_already_exist.return_value = True
        mock_checking_parent_id_exist.return_value = True
        mock_filtering_category.return_value = True
        mock_checking_new_and_old_category_name_not_same.return_value = True
        mock_updating_category_in_db.return_value = {"data": {"message": "Category updated"}}, 200
        response = self.client.put("/ad/update_category/1", headers=self.access_token, data=category_add)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'category already exist' in response.data)

    @patch('advertisement.api.checking_new_and_old_category_name_not_same')
    @patch('advertisement.api.updating_category_in_db')
    @patch('advertisement.api.checking_parent_id_exist')
    @patch('advertisement.api.filtering_category')
    @patch('advertisement.api.checking_category_name_already_exist')
    @patch('advertisement.api.admin_is_true')
    def test_change_category_error_provide_parent_id_or_image(self, mock_admin_is_true, mock_checking_category_name_already_exist, mock_filtering_category, mock_checking_parent_id_exist, mock_updating_category_in_db, mock_checking_new_and_old_category_name_not_same):
        category_add = {"category": "Demo", "file": (io.BytesIO(b'static/iphone13pro.svg'), "iphone13pro.svg"),
                        "parent_id": 11}
        mock_admin_is_true.return_value = True
        mock_checking_category_name_already_exist.return_value = True
        mock_checking_parent_id_exist.return_value = True
        mock_filtering_category.return_value = True
        mock_checking_new_and_old_category_name_not_same.return_value = False
        mock_updating_category_in_db.return_value = {"data": {"message": "Category updated"}}, 200
        response = self.client.put("/ad/update_category/1", headers=self.access_token, data=category_add)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide image if category and provide parent_id if sub category' in response.data)

    @patch('advertisement.api.checking_new_and_old_category_name_not_same')
    @patch('advertisement.api.updating_category_in_db')
    @patch('advertisement.api.checking_parent_id_exist')
    @patch('advertisement.api.filtering_category')
    @patch('advertisement.api.checking_category_name_already_exist')
    @patch('advertisement.api.admin_is_true')
    def test_change_category_error_parent_id_should_be_integer(self, mock_admin_is_true,
                                                              mock_checking_category_name_already_exist,
                                                              mock_filtering_category, mock_checking_parent_id_exist,
                                                              mock_updating_category_in_db,
                                                              mock_checking_new_and_old_category_name_not_same):
        category_add = {"category": "Demo", "parent_id": "jsghdf"}
        mock_admin_is_true.return_value = True
        mock_checking_category_name_already_exist.return_value = True
        mock_checking_parent_id_exist.return_value = True
        mock_filtering_category.return_value = True
        mock_checking_new_and_old_category_name_not_same.return_value = False
        mock_updating_category_in_db.return_value = {"data": {"message": "Category updated"}}, 200
        response = self.client.put("/ad/update_category/1", headers=self.access_token, data=category_add)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'parent_id should be integer' in response.data)

    @patch('advertisement.api.checking_new_and_old_category_name_not_same')
    @patch('advertisement.api.updating_category_in_db')
    @patch('advertisement.api.checking_parent_id_exist')
    @patch('advertisement.api.filtering_category')
    @patch('advertisement.api.checking_category_name_already_exist')
    @patch('advertisement.api.admin_is_true')
    def test_change_category_error_provide_category_name(self, mock_admin_is_true,
                                                               mock_checking_category_name_already_exist,
                                                               mock_filtering_category, mock_checking_parent_id_exist,
                                                               mock_updating_category_in_db,
                                                               mock_checking_new_and_old_category_name_not_same):
        category_add = {"category": None, "parent_id": "jsghdf"}
        mock_admin_is_true.return_value = True
        mock_checking_category_name_already_exist.return_value = True
        mock_checking_parent_id_exist.return_value = True
        mock_filtering_category.return_value = True
        mock_checking_new_and_old_category_name_not_same.return_value = False
        mock_updating_category_in_db.return_value = {"data": {"message": "Category updated"}}, 200
        response = self.client.put("/ad/update_category/1", headers=self.access_token, data=category_add)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide category name' in response.data)

    @patch('advertisement.api.checking_new_and_old_category_name_not_same')
    @patch('advertisement.api.updating_category_in_db')
    @patch('advertisement.api.checking_parent_id_exist')
    @patch('advertisement.api.filtering_category')
    @patch('advertisement.api.checking_category_name_already_exist')
    @patch('advertisement.api.admin_is_true')
    def test_change_category_error_parent_id_should_be_id_of_any_category(self, mock_admin_is_true,
                                                         mock_checking_category_name_already_exist,
                                                         mock_filtering_category, mock_checking_parent_id_exist,
                                                         mock_updating_category_in_db,
                                                         mock_checking_new_and_old_category_name_not_same):
        category_add = {"category": "Demo", "parent_id": 12}
        mock_admin_is_true.return_value = True
        mock_checking_category_name_already_exist.return_value = True
        mock_checking_parent_id_exist.return_value = False
        mock_filtering_category.return_value = True
        mock_checking_new_and_old_category_name_not_same.return_value = False
        mock_updating_category_in_db.return_value = {"data": {"message": "Category updated"}}, 200
        response = self.client.put("/ad/update_category/1", headers=self.access_token, data=category_add)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'parent_id should be id of any category' in response.data)

    @patch('advertisement.api.checking_new_and_old_category_name_not_same')
    @patch('advertisement.api.updating_category_in_db')
    @patch('advertisement.api.checking_parent_id_exist')
    @patch('advertisement.api.filtering_category')
    @patch('advertisement.api.checking_category_name_already_exist')
    @patch('advertisement.api.admin_is_true')
    def test_change_category_error_image_should_be_svg(self, mock_admin_is_true,
                                                                          mock_checking_category_name_already_exist,
                                                                          mock_filtering_category,
                                                                          mock_checking_parent_id_exist,
                                                                          mock_updating_category_in_db,
                                                                          mock_checking_new_and_old_category_name_not_same):
        category_add = {"category": "Demo", "parent_id": '', "file": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_admin_is_true.return_value = True
        mock_checking_category_name_already_exist.return_value = True
        mock_checking_parent_id_exist.return_value = True
        mock_filtering_category.return_value = True
        mock_checking_new_and_old_category_name_not_same.return_value = False
        mock_updating_category_in_db.return_value = {"data": {"message": "Category updated"}}, 200
        response = self.client.put("/ad/update_category/1", headers=self.access_token, data=category_add)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'image should be svg' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_provide_category_id(self, mock_create_ad_db,mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj={"category_id": "", "status": "active", "title": "BMW Car", "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1", "negotiable_product": "True", "feature_product":"True","price": "5000", "location": "Kochi", "latitude": "9.9", "longitude": "76.2", "seller_name":"Aadi", "phone": 7897987890, "email_id": "testuser@gmail.com", "images":os.getenv('HOME_ROUTE')+"static/iphone13pro.jpg"}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value="category"
        mock_create_ad_plan_db.return_value="ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide category id' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_message_ad_created(self, mock_create_ad_db,mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "1", "status": "active", "title": "BMW Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "False", "feature_product": "True", "price": "5000", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images":(io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'ad created' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_provide_category_id_as_integer(self, mock_create_ad_db,mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "1aca", "status": "active", "title": "BMW Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5000", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images":(io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide category id as integer' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_provide_seller_type(self, mock_create_ad_db,mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "1", "status": "active", "title": "BMW Car",
                         "description": "5000 km run car for sale", "seller_type": "", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5000", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide seller_type' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_provide_title(self, mock_create_ad_db,mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "1", "status": "active", "title": "",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5000", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images":(io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide title' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_provide_location(self, mock_create_ad_db,mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "1", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5000", "location": "",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide location' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_provide_ad_plan_id(self, mock_create_ad_db,mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "1", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "",
                         "negotiable_product": "True", "feature_product": "True", "price": "5000", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide advertisement plan id' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_provide_ad_plan_as_integer(self, mock_create_ad_db,mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "1", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "sd",
                         "negotiable_product": "True", "feature_product": "True", "price": "5000", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide advertisement plan id as integer' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_ad_plan_id_not_found(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "1", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "24",
                         "negotiable_product": "True", "feature_product": "True", "price": "5000", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = None
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'advertisement plan id not found' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_category_id_not_found(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "234", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5000", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = None
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'category id not found' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_provide_negotiable_product_as_boolean(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "sdcsc", "feature_product": "True", "price": "5000", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide product is negotiable or not as True or False' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_provide_negotiable_product(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "", "feature_product": "True", "price": "5000", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide product is negotiable or not' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_provide_ad_is_featured_or_not(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "", "price": "5000", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide product is featured or not' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_provide_product_is_featured_or_not_as_boolean(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "afda", "price": "5000", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide product is featured or not as True or False' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_provide_price_as_floating_point(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "dgh", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide price as floating number' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_provide_price(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide price' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_provide_latitude_as_number(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "feqwfefw", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide latitude as floating number' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_provide_longitude_as_number(self, mock_create_ad_db, mock_create_ad_category_db,
                                                        mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "False", "price": "5354", "location": "Kochi",
                         "latitude": "9.9", "longitude": "dhjbv", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com",
                         "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide longitude as floating number' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_provide_longitude(self, mock_create_ad_db, mock_create_ad_category_db,
                                              mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "76", "longitude": "", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com",
                         "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide longitude' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_latitude(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide latitude' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_provide_phone_number(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": "",
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide phone number' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_provide_valid_phone_number(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": "235425",
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide valid phone number' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_provide_valid_email(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 6786786789,
                         "email_id": "testuser", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide valid email' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_message(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 6786786789,
                         "email_id": "", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'ad created' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_provide_seller_name(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "", "phone": 6786786789,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide seller_name' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_image_is_required(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "", "phone": 6786786789,
                         "email_id": "testuser@gmail.com",
                         "images": ""}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'image field is required' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_image_format_not_correct(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "", "phone": 6786786789,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/fil.csv'), "fil.csv")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'"image should be in png, webp, jpg or jpeg format"' in response.data)

    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.saving_created_ad')
    def test_create_ad_error_jwt(self, mock_create_ad_db, mock_create_ad_category_db, mock_create_ad_plan_db):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "", "phone": 6786786789,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/fil.csv'), "fil.csv")}
        mock_create_ad_db.return_value = {"data": {"message": "ad created"}}, 200
        mock_create_ad_category_db.return_value = "category"
        mock_create_ad_plan_db.return_value = "ad plan"
        response = self.client.post("/ad/create_ad", data=create_ad_obj)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'msg' in response.data)
        self.assertTrue(b'Missing Authorization Header' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_message_ad_edited(self,mock_updating_ad_details,mock_checking_category_id_exist, mock_checking_adplan_exist,mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value=True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'ad edited successfully' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_error_owner_can_edit_ad(self,mock_updating_ad_details,mock_checking_category_id_exist, mock_checking_adplan_exist,mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "24", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = False
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'only owner can edit ad' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_error_provide_category_id(self, mock_updating_ad_details, mock_checking_category_id_exist, mock_checking_adplan_exist,
                        mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide category id' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_error_provide_category_id_as_integer(self, mock_updating_ad_details, mock_checking_category_id_exist, mock_checking_adplan_exist,
                        mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "safd", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide category id as integer' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_error_category_id_not_found(self, mock_updating_ad_details, mock_checking_category_id_exist, mock_checking_adplan_exist,
                        mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "123312", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = None
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'category id not found' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_error_provide_title(self, mock_updating_ad_details, mock_checking_category_id_exist, mock_checking_adplan_exist,
                        mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "12", "status": "active", "title": "",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "1",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide title' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_error_provide_ad_id_as_integer(self, mock_updating_ad_details, mock_checking_category_id_exist, mock_checking_adplan_exist,
                        mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "12", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "avds",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide advertisement plan id as integer' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_error_ad_plan_id_not_found(self, mock_updating_ad_details, mock_checking_category_id_exist, mock_checking_adplan_exist,
                        mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "12", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id":"12313",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = None
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'advertisement plan id not found' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_error_product_is_negotiable_or_not_as_boolean(self, mock_updating_ad_details, mock_checking_category_id_exist, mock_checking_adplan_exist,
                        mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "12", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "12",
                         "negotiable_product": "jqlckc", "feature_product": "True", "price": "5354", "location": "Kochi",
                         "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide product is negotiable or not as True or False' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad1_error_product_is_negotiable_as_boolean(self, mock_updating_ad_details, mock_checking_category_id_exist, mock_checking_adplan_exist,mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "12", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "12",
                         "negotiable_product": "10", "feature_product": "True", "price": "5354",
                         "location": "Kochi","latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi", "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide product is negotiable or not as True or False' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_error_product_is_negotiable_or_not(self, mock_updating_ad_details, mock_checking_category_id_exist, mock_checking_adplan_exist,mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "12", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "12",
                         "negotiable_product": "", "feature_product": "True", "price": "5354",
                         "location": "Kochi", "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi",
                         "phone": 7897987890,
                         "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide product is negotiable or not' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_error_product_is_featured_boolean(self, mock_updating_ad_details, mock_checking_category_id_exist, mock_checking_adplan_exist,mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "12", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "12",
                         "negotiable_product": "True", "feature_product": "dsacds", "price": "5354",
                         "location": "Kochi", "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi",
                         "phone": 7897987890,"email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide product is featured or not as True or False' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_error_product_is_featured_as_boolean(self, mock_updating_ad_details, mock_checking_category_id_exist, mock_checking_adplan_exist,
                         mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "12", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "12",
                         "negotiable_product": "True", "feature_product": "123", "price": "5354",
                         "location": "Kochi", "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi",
                         "phone": 7897987890, "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide product is featured or not as True or False' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_error_product_is_featured_or_not(self, mock_updating_ad_details, mock_checking_category_id_exist, mock_checking_adplan_exist,
                         mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "12", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "12",
                         "negotiable_product": "True", "feature_product": "", "price": "5354",
                         "location": "Kochi", "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi",
                         "phone": 7897987890, "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide product is featured or not' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_error_provide_seller_name(self, mock_updating_ad_details, mock_checking_category_id_exist, mock_checking_adplan_exist,
                         mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "12", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "12",
                         "negotiable_product": "True", "feature_product": "True", "price": "5354",
                         "location": "Kochi", "latitude": "9.9", "longitude": "76.2", "seller_name": "",
                         "phone": 7897987890, "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide seller_name' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_error_provide_price(self, mock_updating_ad_details, mock_checking_category_id_exist, mock_checking_adplan_exist,
                         mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "12", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "12",
                         "negotiable_product": "True", "feature_product": "True", "price": "",
                         "location": "Kochi", "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi",
                         "phone": 7897987890, "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide price' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_error_provide_latitude(self, mock_updating_ad_details, mock_checking_category_id_exist, mock_checking_adplan_exist,
                         mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "12", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "12",
                         "negotiable_product": "True", "feature_product": "False", "price": "32221",
                         "location": "Kochi", "latitude": "", "longitude": "76.2", "seller_name": "Aadi",
                         "phone": 7897987890, "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide latitude' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_error_provide_price_as_floating_number(self, mock_updating_ad_details, mock_checking_category_id_exist,
                                              mock_checking_adplan_exist,
                                              mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "12", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "12",
                         "negotiable_product": "True", "feature_product": "True", "price": "A",
                         "location": "Kochi", "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi",
                         "phone": 7897987890, "email_id": "testuser@gmail.com",
                         "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide price as floating number' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_error_provide_latitude_as_floating_number(self, mock_updating_ad_details, mock_checking_category_id_exist, mock_checking_adplan_exist,
                         mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "12", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "12",
                         "negotiable_product": "True", "feature_product": "True", "price": "32221",
                         "location": "Kochi", "latitude": "saffsa", "longitude": "76.2", "seller_name": "Aadi",
                         "phone": 7897987890, "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide latitude as floating number' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_error_provide_ad_plan_id(self, mock_updating_ad_details,
                                                                 mock_checking_category_id_exist,
                                                                 mock_checking_adplan_exist,
                                                                 mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "12", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "",
                         "negotiable_product": "True", "feature_product": "True", "price": "32221",
                         "location": "Kochi", "latitude": "9.9", "longitude": "76.2", "seller_name": "Aadi",
                         "phone": 7897987890, "email_id": "testuser@gmail.com",
                         "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide advertisement plan id' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_error_provide_longitude_as_float(self, mock_updating_ad_details, mock_checking_category_id_exist, mock_checking_adplan_exist,
                         mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "12", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "12",
                         "negotiable_product": "True", "feature_product": "True", "price": "32221",
                         "location": "Kochi", "latitude": "9.9", "longitude": "weq", "seller_name": "Aadi",
                         "phone": 7897987890, "email_id": "testuser@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide longitude as floating number' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_error_provide_valid_email(self, mock_updating_ad_details, mock_checking_category_id_exist, mock_checking_adplan_exist,
                         mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "12", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "12",
                         "negotiable_product": "True", "feature_product": "True", "price": "32221",
                         "location": "Kochi", "latitude": "9.9", "longitude": "76.3", "seller_name": "Aadi",
                         "phone": 7897987890, "email_id": "testuser", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide valid email' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_message(self, mock_updating_ad_details, mock_checking_category_id_exist, mock_checking_adplan_exist,
                         mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "12", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "12",
                         "negotiable_product": "True", "feature_product": "True", "price": "32221",
                         "location": "Kochi", "latitude": "9.9", "longitude": "76.3", "seller_name": "Aadi",
                         "phone": 7897987890, "email_id": "", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'ad edited successfully' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_error_provide_phone_num(self, mock_updating_ad_details, mock_checking_category_id_exist, mock_checking_adplan_exist,
                         mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "12", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "12",
                         "negotiable_product": "True", "feature_product": "True", "price": "32221",
                         "location": "Kochi", "latitude": "9.9", "longitude": "76.3", "seller_name": "Aadi",
                         "phone": '', "email_id": "user@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide phone number' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_error_provide_seller_type(self, mock_updating_ad_details, mock_checking_category_id_exist, mock_checking_adplan_exist,
                         mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "12", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "", "ad_plan_id": "12",
                         "negotiable_product": "True", "feature_product": "True", "price": "32221",
                         "location": "Kochi", "latitude": "9.9", "longitude": "76.3", "seller_name": "Aadi",
                         "phone": '9089080089', "email_id": "user@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide seller_type' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_provide_valid_phone_num(self, mock_updating_ad_details, mock_checking_category_id_exist, mock_checking_adplan_exist,
                         mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "12", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "12",
                         "negotiable_product": "True", "feature_product": "True", "price": "32221",
                         "location": "Kochi", "latitude": "9.9", "longitude": "76.3", "seller_name": "Aadi",
                         "phone": '2342315', "email_id": "user@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token, data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'provide valid phone number' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad24_error_jwt(self, mock_updating_ad_details, mock_checking_category_id_exist, mock_checking_adplan_exist,
                         mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "12", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "12",
                         "negotiable_product": "True", "feature_product": "True", "price": "32221",
                         "location": "Kochi", "latitude": "9.9", "longitude": "76.3", "seller_name": "Aadi",
                         "phone": '9002342315', "email_id": "user@gmail.com", "images": (io.BytesIO(b'static/iphone13pro.jpg'), "iphone13pro.jpg")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", data=create_ad_obj)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'Missing Authorization Header' in response.data)
        self.assertTrue(b'msg' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_error_image_is_required(self, mock_updating_ad_details, mock_checking_category_id_exist, mock_checking_adplan_exist,
                         mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "12", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "12",
                         "negotiable_product": "True", "feature_product": "True", "price": "32221",
                        "location": "Kochi", "latitude": "9.9", "longitude": "76.3", "seller_name": "Aadi",
                        "phone": '9002342315', "email_id": "user@gmail.com", "images": ""}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token , data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'data' in response.data)
        self.assertTrue(b'image field is required' in response.data)
        self.assertTrue(b'error' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.checking_adplan_exist')
    @patch('advertisement.api.checking_category_id_exist')
    @patch('advertisement.api.updating_ad_details')
    def test_update_ad_error_image_not_correct_format(self, mock_updating_ad_details, mock_checking_category_id_exist, mock_checking_adplan_exist,
                         mock_checking_person_posted_ad):
        create_ad_obj = {"category_id": "12", "status": "active", "title": "Car",
                         "description": "5000 km run car for sale", "seller_type": "Agent", "ad_plan_id": "12",
                         "negotiable_product": "True", "feature_product": "True", "price": "32221",
                        "location": "Kochi", "latitude": "9.9", "longitude": "76.3", "seller_name": "Aadi",
                        "phone": '9002342315', "email_id": "user@gmail.com", "images": (io.BytesIO(b'static/fil.csv'), "fil.csv")}
        mock_updating_ad_details.return_value = {"data": {"message": "ad edited successfully"}}, 200
        mock_checking_category_id_exist.return_value = "category"
        mock_checking_adplan_exist.return_value = "ad plan"
        mock_checking_person_posted_ad.return_value = True
        response = self.client.put("/ad/update_ad/1", headers=self.access_token , data=create_ad_obj)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'data' in response.data)
        self.assertTrue(b'"image should be in png, webp, jpg or jpeg format"' in response.data)
        self.assertTrue(b'error' in response.data)


    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.filtering_ad_by_id')
    @patch('advertisement.api.deleting_ad')
    def test_delete_ad_message(self, mock_delete_ad_person, mock_del_ad_filter_adv, mock_ad_id_and_person):
        mock_delete_ad_person.return_value = {"data": {"message": "ad deleted"}}
        mock_del_ad_filter_adv.return_value = "ad"
        mock_ad_id_and_person.return_value= True
        response = self.client.delete("/ad/delete_ad/1", headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'ad deleted' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.filtering_ad_by_id')
    @patch('advertisement.api.deleting_ad')
    def test_delete_ad2_message_ad_deleted(self, mock_delete_ad_person, mock_del_ad_filter_adv, mock_ad_id_and_person):
        mock_delete_ad_person.return_value = {"data": {"message": "ad deleted"}}
        mock_del_ad_filter_adv.return_value = "ad"
        mock_ad_id_and_person.return_value = True
        response = self.client.delete("/ad/delete_ad/1", headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'ad deleted' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.filtering_ad_by_id')
    @patch('advertisement.api.deleting_ad')
    def test_delete_ad_error_ad_not_found(self, mock_delete_ad_person, mock_del_ad_filter_adv, mock_ad_id_and_person):
        mock_delete_ad_person.return_value = {"data": {"message": "ad deleted"}}
        mock_del_ad_filter_adv.return_value = None
        mock_ad_id_and_person.return_value = True
        response = self.client.delete("/ad/delete_ad/1", headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'ad not found' in response.data)

    @patch('advertisement.api.listing_the_ad')
    @patch('advertisement.api.searching_the_ad')
    def test_list_ad_message(self, mock_searching_the_ad, mock_listing_the_ad):
        mock_listing_the_ad.return_value = {"data": {"message": [
            {
                "cover image": "http://10.6.9.26:5000/static/images_ad/avon_cycle.jpeg",
                "featured": True,
                "id": 12,
                "location": "Turavur, Aalapuzha",
                "price": 8000.0,
                "title": "avon cycle"
            }]}}
        mock_searching_the_ad.return_value = None
        response = self.client.get("/ad/view_ad")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'data' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.filtering_ad_by_id')
    @patch('advertisement.api.saving_ad_as_inactive')
    def test_api_inactivate_ad_message(self,mock_saving_ad_as_inactive,mock_filtering_ad_by_id_adv,mock_checking_user_posted_ad):
        mock_saving_ad_as_inactive.return_value = {"data": {"message": "ad inactivated"}}
        mock_filtering_ad_by_id_adv.return_value = "ad"
        mock_checking_user_posted_ad.return_value = True
        response = self.client.put("/ad/remove_ad/1", headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'ad inactivated' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.filtering_ad_by_id')
    @patch('advertisement.api.saving_ad_as_inactive')
    def test_api_inactivate_ad_error_only_owner_can_edit_ad(self, mock_saving_ad_as_inactive, mock_filtering_ad_by_id_adv,mock_checking_user_posted_ad):
        mock_saving_ad_as_inactive.return_value = {"data": {"message": "ad deleted"}}
        mock_filtering_ad_by_id_adv.return_value = "ad"
        mock_checking_user_posted_ad.return_value = False
        response = self.client.put("/ad/remove_ad/1", headers=self.access_token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'only owner can edit ad' in response.data)

    @patch('advertisement.api.checking_user_posted_ad')
    @patch('advertisement.api.filtering_ad_by_id')
    @patch('advertisement.api.saving_ad_as_inactive')
    def test_inactivate_ad_error_ad_not_found(self, mock_saving_ad_as_inactive, mock_filtering_ad_by_id_adv, mock_checking_user_posted_ad):
        mock_saving_ad_as_inactive.return_value = {"data": {"message": "ad deleted"}}
        mock_filtering_ad_by_id_adv.return_value = None
        mock_checking_user_posted_ad.return_value = True
        response = self.client.put("/ad/remove_ad/1", headers=self.access_token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'ad not found' in response.data)

    @patch('advertisement.api.reporting_ad_and_checking_number_of_reports')
    @patch('advertisement.api.checking_user_already_reported_ad')
    @patch('advertisement.api.filtering_ad_by_id')
    def test_api_reporting_ad_message(self, mock_filtering_ad_by_id, mock_checking_user_already_reported_ad, mock_reporting_ad_and_checking_number_of_reports):
        mock_filtering_ad_by_id.return_value = "ad"
        mock_checking_user_already_reported_ad.return_value = False
        mock_reporting_ad_and_checking_number_of_reports.return_value = {"data": {"message": "ad reported"}}
        response = self.client.post("/ad/report_ad/1", headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'ad reported' in response.data)

    @patch('advertisement.api.reporting_ad_and_checking_number_of_reports')
    @patch('advertisement.api.checking_user_already_reported_ad')
    @patch('advertisement.api.filtering_ad_by_id')
    def test_api_reporting_ad_error_ad_not_found(self, mock_filtering_ad_by_id, mock_checking_user_already_reported_ad,
                        mock_reporting_ad_and_checking_number_of_reports):
        mock_filtering_ad_by_id.return_value = None
        mock_checking_user_already_reported_ad.return_value = False
        mock_reporting_ad_and_checking_number_of_reports.return_value = {"data": {"message": "ad reported"}}
        response = self.client.post("/ad/report_ad/1", headers=self.access_token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'ad not found' in response.data)

    @patch('advertisement.api.reporting_ad_and_checking_number_of_reports')
    @patch('advertisement.api.checking_user_already_reported_ad')
    @patch('advertisement.api.filtering_ad_by_id')
    def test_api_reporting_ad_error_ad_already_reported(self, mock_filtering_ad_by_id, mock_checking_user_already_reported_ad,
                        mock_reporting_ad_and_checking_number_of_reports):
        mock_filtering_ad_by_id.return_value = "ad"
        mock_checking_user_already_reported_ad.return_value = True
        mock_reporting_ad_and_checking_number_of_reports.return_value = {"data": {"message": "ad reported"}}
        response = self.client.post("/ad/report_ad/1", headers=self.access_token)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'ad already reported by user' in response.data)

    @patch('advertisement.api.reporting_ad_and_checking_number_of_reports')
    @patch('advertisement.api.checking_user_already_reported_ad')
    @patch('advertisement.api.filtering_ad_by_id')
    def test_api_reporting_ad_error_jwt(self, mock_filtering_ad_by_id, mock_checking_user_already_reported_ad,
                        mock_reporting_ad_and_checking_number_of_reports):
        mock_filtering_ad_by_id.return_value = "ad"
        mock_checking_user_already_reported_ad.return_value = True
        mock_reporting_ad_and_checking_number_of_reports.return_value = {"data": {"message": "ad reported"}}
        response = self.client.post("/ad/report_ad/1")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'msg' in response.data)
        self.assertTrue(b'Missing Authorization Header' in response.data)

    @patch('advertisement.api.saving_ad_to_favourite')
    @patch('advertisement.api.removing_ad_from_favourite')
    @patch('advertisement.api.checking_user_favourited_ad')
    @patch('advertisement.api.filtering_ad_by_id')
    def test_api_favourite_ad_error_jwt(self, mock_filtering_ad_by_id, mock_checking_user_favourited_ad, mock_removing_ad_from_favourite, mock_saving_ad_to_favourite ):
        mock_filtering_ad_by_id.return_value = "ad"
        mock_checking_user_favourited_ad.return_value = "ad"
        mock_removing_ad_from_favourite.return_value = {"data": {"message": "ad removed from favourites"}}, 200
        mock_saving_ad_to_favourite.return_value={"data": {"message": "ad saved to favourites"}}, 200
        response = self.client.post("/ad/favourite_ad/1")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'msg' in response.data)
        self.assertTrue(b'Missing Authorization Header' in response.data)

    @patch('advertisement.api.saving_ad_to_favourite')
    @patch('advertisement.api.removing_ad_from_favourite')
    @patch('advertisement.api.checking_user_favourited_ad')
    @patch('advertisement.api.filtering_ad_by_id')
    def test_api_favourite_ad_error_ad_not_found(self, mock_filtering_ad_by_id, mock_checking_user_favourited_ad, mock_removing_ad_from_favourite, mock_saving_ad_to_favourite):
        mock_filtering_ad_by_id.return_value = None
        mock_checking_user_favourited_ad.return_value = "ad"
        mock_removing_ad_from_favourite.return_value = {"data": {"message": "ad removed from favourites"}}, 200
        mock_saving_ad_to_favourite.return_value = {"data": {"message": "ad saved to favourites"}}, 200
        response = self.client.post("/ad/favourite_ad/1", headers=self.access_token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'ad not found' in response.data)


    @patch('advertisement.api.saving_ad_to_favourite')
    @patch('advertisement.api.removing_ad_from_favourite')
    @patch('advertisement.api.checking_user_favourited_ad')
    @patch('advertisement.api.filtering_ad_by_id')
    def test_api_favourite_ad_message_added_to_favourites(self, mock_filtering_ad_by_id, mock_checking_user_favourited_ad, mock_removing_ad_from_favourite, mock_saving_ad_to_favourite):
        mock_filtering_ad_by_id.return_value = "ad"
        mock_checking_user_favourited_ad.return_value = None
        mock_removing_ad_from_favourite.return_value = {"data": {"message": "ad removed from favourites"}}, 200
        mock_saving_ad_to_favourite.return_value = {"data": {"message": "ad saved to favourites"}}, 200
        response = self.client.post("/ad/favourite_ad/1", headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'ad saved to favourites' in response.data)

    @patch('advertisement.api.saving_ad_to_favourite')
    @patch('advertisement.api.removing_ad_from_favourite')
    @patch('advertisement.api.checking_user_favourited_ad')
    @patch('advertisement.api.filtering_ad_by_id')
    def test_api_favourite_ad_message_removed_from_favourites(self, mock_filtering_ad_by_id, mock_checking_user_favourited_ad, mock_removing_ad_from_favourite, mock_saving_ad_to_favourite):
        mock_filtering_ad_by_id.return_value = "ad"
        mock_checking_user_favourited_ad.return_value = "ad"
        mock_removing_ad_from_favourite.return_value = {"data": {"message": "ad removed from favourites"}}, 200
        mock_saving_ad_to_favourite.return_value = {"data": {"message": "ad saved to favourites"}}, 200
        response = self.client.post("/ad/favourite_ad/1", headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'ad removed from favourites' in response.data)

    @patch('advertisement.api.returning_ad_created_by_user')
    @patch('advertisement.api.checking_user_liked_ad')
    @patch('advertisement.api.advertisement_created_by_user')
    def test_api_my_ads_message(self,mock_advertisement_created_by_user, mock_checking_user_liked_his_ad, mock_returning_ad_created_by_user):
        mock_advertisement_created_by_user.return_value = ["advertisement1","advertisement2"]
        mock_checking_user_liked_his_ad.return_value = True
        mock_returning_ad_created_by_user.return_value = True
        response = self.client.get("/ad/view_my_ads", headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'[]' in response.data)

    @patch('advertisement.api.returning_ad_created_by_user')
    @patch('advertisement.api.checking_user_liked_ad')
    @patch('advertisement.api.advertisement_created_by_user')
    def test_my_ads_message_list(self,mock_advertisement_created_by_user, mock_checking_user_liked_his_ad, mock_returning_ad_created_by_user):
        mock_advertisement_created_by_user.return_value = []
        mock_checking_user_liked_his_ad.return_value = False
        mock_returning_ad_created_by_user.return_value = True
        response = self.client.get("/ad/view_my_ads", headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'[]' in response.data)

    @patch('advertisement.api.returning_ad_created_by_user')
    @patch('advertisement.api.checking_user_liked_ad')
    @patch('advertisement.api.advertisement_created_by_user')
    def test_api_my_ads__error_jwt(self, mock_advertisement_created_by_user, mock_checking_user_liked_his_ad,
                     mock_returning_ad_created_by_user):
        mock_advertisement_created_by_user.return_value = []
        mock_checking_user_liked_his_ad.return_value = False
        mock_returning_ad_created_by_user.return_value = True
        response = self.client.get("/ad/view_my_ads")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'msg' in response.data)
        self.assertTrue(b'Missing Authorization Header' in response.data)

    @patch('advertisement.api.checking_for_disabled_ads')
    @patch('advertisement.api.returning_my_favourites')
    @patch('advertisement.api.user_favourite_ads')
    def test_api_my_favourites_error_jwt(self, mock_user_favourite_ads, mock_returning_my_favourites, mock_checking_for_disabled_ads):
        mock_user_favourite_ads.return_value = None
        mock_returning_my_favourites.return_value = True
        mock_checking_for_disabled_ads.return_value = True
        response = self.client.get("/ad/my_favourite_ad")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'msg' in response.data)
        self.assertTrue(b'Missing Authorization Header' in response.data)

    @patch('advertisement.api.checking_for_disabled_ads')
    @patch('advertisement.api.favourite_advertisement')
    @patch('advertisement.api.user_favourite_ads')
    def test_api_my_favourites_message(self, mock_user_favourite_ads, mock_favourite_advertisement,
                            mock_checking_for_disabled_ads):
        mock_user_favourite_ads.return_value = None
        mock_favourite_advertisement.return_value = {"is_disabled": False}
        mock_checking_for_disabled_ads.return_value = True
        response = self.client.get("/ad/my_favourite_ad", headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'[]' in response.data)

    @patch('advertisement.api.showing_similar_ads')
    @patch('advertisement.api.checking_user_liked_ad')
    @patch('advertisement.api.returning_similar_ads')
    @patch('advertisement.api.searching_the_category_id')
    @patch('advertisement.api.searching_in_title_list')
    @patch('advertisement.api.splitting_title')
    @patch('advertisement.api.filtering_ad_by_id')
    def test_api_related_ads_message(self, mock_filtering_ad_by_id, mock_splitting_title,mock_searching_in_title_list, mock_searching_the_category_id,mock_returning_similar_ads,mock_checking_user_liked_ad,mock_showing_similar_ads):
        search_list=["ad1", "ad2"]
        mock_filtering_ad_by_id.return_value = "ad"
        mock_splitting_title.return_value = "bmw cars"
        mock_searching_in_title_list.return_value=True
        mock_searching_the_category_id.return_value = search_list
        mock_returning_similar_ads.return_value=["ad"]
        mock_checking_user_liked_ad.return_value=True
        mock_showing_similar_ads.return_value=True
        response = self.client.get("/ad/similar_ads/1", headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'message' in response.data)
        self.assertTrue(b'[]' in response.data)

    @patch('advertisement.api.showing_similar_ads')
    @patch('advertisement.api.checking_user_liked_ad')
    @patch('advertisement.api.returning_similar_ads')
    @patch('advertisement.api.searching_the_category_id')
    @patch('advertisement.api.searching_in_title_list')
    @patch('advertisement.api.splitting_title')
    @patch('advertisement.api.filtering_ad_by_id')
    def test_api_related_ads_error_ad_not_found(self, mock_filtering_ad_by_id, mock_splitting_title, mock_searching_in_title_list,mock_searching_the_category_id, mock_returning_similar_ads, mock_checking_user_liked_ad,mock_showing_similar_ads):
        search_list = ["ad1", "ad2"]
        mock_filtering_ad_by_id.return_value = None
        mock_splitting_title.return_value = "bmw cars"
        mock_searching_in_title_list.return_value = True
        mock_searching_the_category_id.return_value = search_list
        mock_returning_similar_ads.return_value = ["ad"]
        mock_checking_user_liked_ad.return_value = True
        mock_showing_similar_ads.return_value = True
        response = self.client.get("/ad/similar_ads/1", headers=self.access_token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'ad not found' in response.data)

    def test_model_ad_plan(self):
        ad_plan = AdPlan(price=10000,days=5)
        assert ad_plan.price == 10000
        assert ad_plan.days == 5

    def test_model_ad_image(self):
        ad_image = AdImage(file="file",display_order=2,is_cover_image=True,ad_id=1)
        assert ad_image.file == "file"
        assert ad_image.display_order == 2
        assert ad_image.is_cover_image == True
        assert ad_image.ad_id == 1

    def test_model_advertisement(self):
        ad = Advertisement(title="test",status="active",seller_type="tester",description='description',is_negotiable=True, is_featured=True,location="Kochi",latitude=15,longitude=80,
                           seller_name="seller",phone=7897979787,geo="123",email="email@gmail.com",is_deleted=False,advertising_id=1,user_id=1,category_id=12,advertising_plan_id=1,price=1008)
        assert ad.title == "test"
        assert ad.status == "active"
        assert ad.seller_type == "tester"
        assert ad.description == 'description'
        assert ad.is_negotiable==True
        assert ad.is_featured==True
        assert ad.location == "Kochi"
        assert ad.latitude == 15
        assert ad.longitude == 80
        assert ad.seller_name == "seller"
        assert ad.phone == 7897979787
        assert ad.geo == "123"
        assert ad.email == "email@gmail.com"
        assert ad.is_deleted == False
        assert ad.advertising_id == 1
        assert ad.user_id == 1
        assert ad.category_id == 12
        assert ad.advertising_plan_id == 1
        assert ad.price == 1008

    def test_model_report_ad(self):
        report_ad = ReportAd(user_id=100,ad_id=100)
        assert report_ad.user_id == 100
        assert report_ad.ad_id  == 100


    @patch('advertisement.api.returning_ad_detail')
    @patch('advertisement.api.filtering_ad_by_id')
    def test_getting_ad_details_error_ad_not_found(self, mock_filtering_ad_by_id, mock_returning_ad_detail):
        mock_filtering_ad_by_id.return_value = None
        mock_returning_ad_detail = "ad_detail"
        response = self.client.get("/ad/ad_details/1", headers=self.access_token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'error' in response.data)
        self.assertTrue(b'ad not found' in response.data)

    @patch('advertisement.api.returning_ad_detail')
    @patch('advertisement.api.filtering_ad_by_id')
    def test_getting_ad_details_message(self, mock_filtering_ad_by_id, mock_returning_ad_detail):
        mock_filtering_ad_by_id.return_value = "test"
        mock_returning_ad_detail.return_value = {"advertising_id": "74OS395EBE21BH",
                                    "category_name": "Automotive",
                                    "description": "Car",
                                    "favourite": False,
                                    "featured": False,
                                    "id": 10,
                                    "images": [
                                        "http://10.6.9.26:5000/static/images_ad/74OS395EBE21BHdownload.jpeg"
                                    ],
                                    "latitude": 10.0159,
                                    "location": "Kochi, Kerala",
                                    "longitude": 76.3419,
                                    "photo": "http://10.6.9.26:5000/static/profile/3useraffsvzgavon_cycle_2.jpeg",
                                    "posted_at": "Thu, 02 Feb 2023 18:37:26 GMT",
                                    "price": 800043.0,
                                    "seller_name": "Thuqlaq",
                                    "status": "active",
                                    "title": "Honda Car\n"
}
        response = self.client.get("/ad/ad_details/1", headers=self.access_token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/json")
        self.assertTrue(b'seller_name' in response.data)
        self.assertTrue(b'title' in response.data)
        self.assertTrue(b'advertising_id' in response.data)
        self.assertTrue(b'category_name' in response.data)
        self.assertTrue(b'description' in response.data)
        self.assertTrue(b'title' in response.data)
        self.assertTrue(b'favourite' in response.data)
        self.assertTrue(b'featured' in response.data)
        self.assertTrue(b'status' in response.data)
        self.assertTrue(b'id' in response.data)
        self.assertTrue(b'images' in response.data)
        self.assertTrue(b'latitude' in response.data)
        self.assertTrue(b'location' in response.data)
        self.assertTrue(b'longitude' in response.data)
        self.assertTrue(b'photo' in response.data)
        self.assertTrue(b'posted_at' in response.data)
        self.assertTrue(b'price' in response.data)

if __name__=="__main__":
    unittest.main()