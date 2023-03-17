from enum import Enum

class ErrorCodes(Enum):
    username_does_not_exist={'msg': "username does not exist", 'code':1001}
    provide_password={'msg': "provide password", 'code':1002}
    incorrect_password={'msg': "incorrect password", 'code':1003}
    provide_all_login_keys={'msg': "provide all login keys", 'code':1004}
    email_cannot_be_empty={'msg': "email cannot be empty", 'code':1005}
    username_cannot_be_empty={'msg': "username cannot be empty", 'code':1006}
    password_cannot_be_empty={'msg': "password cannot be empty", 'code':1007}
    provide_a_valid_email={'msg': "provide a valid email", 'code':1008}
    provide_a_valid_username={'msg': "provide a valid username", 'code':1009}
    password_format_not_matching={'msg': "current password should contain least 1 uppercase, 1 lowercase, 1 number, and 1 special character and maximum length is 20 and minimum length is 8", 'code':1010}
    username_already_exists={'msg': "username already exists", 'code':1011}
    email_already_exists={'msg': "email already exists", 'code':1012}
    provide_all_signup_keys={'msg': "provide all signup keys", 'code':1013}
    provide_current_password={'msg': "provide current password", 'code':1014}
    provide_new_password={'msg': "provide new password", 'code':1015}
    new_password_should_not_be_same_as_previous_password={'msg': "new password should not be same as previous password", 'code':1017}
    key_not_found={'msg': "key not found", 'code':1018}
    image_field_is_required={'msg': "image field is required", 'code':1019}
    image_should_be_in_png_webp_jpg_or_jpeg_format={'msg': "image should be in png, webp, jpg or jpeg format", 'code': 1020}
    ad_already_reported_by_user={'msg': "ad already reported by user", 'code': 1021}
