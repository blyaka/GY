
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class RuUserAttributeSimilarityValidator:
    def __init__(self, user_attributes=None, max_similarity=0.7):
        self.user_attributes = user_attributes or ['username', 'first_name', 'last_name', 'email']
        self.max_similarity = max_similarity

    def validate(self, password, user=None):
        if not user:
            return
        for attr_name in self.user_attributes:
            value = getattr(user, attr_name, None)
            if not value or not isinstance(value, str):
                continue
            value_parts = value.split()
            for part in [value] + value_parts:
                if part and self.max_similarity <= self._similarity(password, part):
                    raise ValidationError(
                        _("Введённый пароль слишком похож на поле «%(verbose_name)s»."),
                        code='password_too_similar',
                        params={'verbose_name': attr_name},
                    )

    def get_help_text(self):
        return _("Пароль не должен быть слишком похож на ваши персональные данные.")

    def _similarity(self, value1, value2):
        from difflib import SequenceMatcher
        return SequenceMatcher(a=value1.lower(), b=value2.lower()).quick_ratio()


class RuMinimumLengthValidator:
    def __init__(self, min_length=8):
        self.min_length = int(min_length)

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("Пароль слишком короткий. Минимальная длина — %(min_length)d символов."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return _("Пароль должен содержать не менее %(min_length)d символов.") % {'min_length': self.min_length}




class RuCommonPasswordValidator:
    def __init__(self, password_list_path=None):
        from django.contrib.auth.password_validation import CommonPasswordValidator
        self.validator = CommonPasswordValidator(password_list_path=password_list_path)

    def validate(self, password, user=None):
        try:
            self.validator.validate(password, user)
        except ValidationError:
            raise ValidationError(
                _("Введённый пароль слишком широко распространён."),
                code='password_too_common',
            )

    def get_help_text(self):
        return _("Пароль не должен быть слишком простым и распространённым.")



class RuNumericPasswordValidator:
    def __init__(self):
        pass

    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                _("Пароль не может состоять только из цифр."),
                code='password_entirely_numeric',
            )

    def get_help_text(self):
        return _("Пароль не должен состоять только из цифр.")
