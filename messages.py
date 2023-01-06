from enum import Enum
class ErrorCodes(Enum):
    username_does_not_exist = 1001
    provide_password=1002
    incorrect_password=1003
    provide_all_login_keys=1004
    email_cannot_be_empty=1005
    username_cannot_be_empty=1006
    password_cannot_be_empty=1007
    provide_a_valid_email=1008
    provide_a_valid_username=1009
    password_format_not_matching=1010
    username_already_exists=1011
    email_already_exists=1012
    provide_all_signup_keys=1013
    provide_current_password=1014
    provide_new_password=1015
    new_password_should_not_be_same_as_previous_password=1017
    key_not_found=1018