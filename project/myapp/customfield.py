from django.db import models

class CustomPhoneNumberField(models.Field):
    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 15
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        return name, path, args, kwargs

    def db_type(self, connection):
        return 'varchar(15)'