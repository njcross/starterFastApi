from marshmallow import Schema, fields, validates, ValidationError
from email_validator import validate_email as ve, EmailNotValidError

class EmailRequestSchema(Schema):
    email = fields.String(required=True)

    @validates("email")
    def validate_email(self, value, **kwargs):   # ← accept **kwargs for Marshmallow 4
        try:
            ve(value, check_deliverability=False)
        except EmailNotValidError as e:
            raise ValidationError(str(e))
