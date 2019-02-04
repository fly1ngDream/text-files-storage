def validate_file_extensions(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]
    # [0] returns path+filename
    valid_extensions = ['.txt', '.docx', '.doc', '.odt']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')
