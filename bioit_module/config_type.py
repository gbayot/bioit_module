import os
from schematics.types import BaseType
from schematics.exceptions import ValidationError


class ExistingFileType(BaseType):
    def validate_isfile(self, filename):
        if not os.path.isfile(filename):
            raise ValidationError("File doesn't exist")