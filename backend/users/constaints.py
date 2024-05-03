from django.core.validators import RegexValidator

USER_MAX_LENGTH = 150
EMAIL_MAX_LENGTH = 254
VALIDATOR_REGEX = RegexValidator(r'^[\w.@+-]+\Z')
TAG_MAX_LENGTH_HEX = 7
TAG_INGREDIENT_MAX_LENGTH = 200
