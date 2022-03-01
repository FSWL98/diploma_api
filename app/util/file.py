def get_file_formats():
    file_mime_types = {
        'audio': ['audio/mpeg3', 'audio/mpeg', 'audio/ogg'],
        'document': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     'application/vnd.ms-excel', 'application/msword',
                     'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                     'application/vnd.ms-powerpoint',
                     'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                     'text/plain', 'application/pdf', 'application/x-rar-compressed', 'application/zip',
                     'application/x-zip-compressed'],
        'image': ['image/jpeg', 'image/png', 'image/svg+xml', 'image/gif'],
        'video': ['video/mpeg', 'video/mp4', 'video/x-msvideo']
    }
    file_extensions = {
        'image': ['jpeg', 'jpg', 'JPG', 'png', 'svg', 'gif'],
        'audio': ['mp3', 'ogg', 'oga'],
        'video': ['mpeg', 'mp4', 'avi'],
        'document': ['xlsx', 'xls', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'pdf', 'rar', 'zip']
    }
    return file_mime_types, file_extensions

