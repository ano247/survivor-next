from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, user_token, username, email, password, **extra_fields):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not username:
            raise ValueError('Users must have an username')

        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            user_token=user_token,
            username=username,
            email=self.normalize_email(email),
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user


def create_superuser(self, user_token, username, email, password, **extra_fields):
    """
    Creates and saves a superuser with the given email, date of
    birth and password.
    """
    user = self.create_user(
        user_token=user_token,
        username=username,
        email=email,
        password=password,
        **extra_fields
    )
    user.is_admin = True
    user.save(using=self._db)
    return user
