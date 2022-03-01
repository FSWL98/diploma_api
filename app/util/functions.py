from http import HTTPStatus


def handle_error(result, api=None, error_code=HTTPStatus.BAD_REQUEST, error_message='Wrong parameters'):
    # TODO: rewrite with python 3.10 pattern matching
    if isinstance(result, tuple) and len(result) == 2 and not result[0] and type(result[1]) == str:
        if api:
            api.abort(error_code, result[1])
        return result[0]
    elif not result and api:
        api.abort(error_code, error_message)
    return result
