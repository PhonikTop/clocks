class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        import string
        import random

        response = self.get_response(request)
        try:
            cookie_key = request.COOKIES["user"]
            response.set_cookie("user", cookie_key)
            return response
        except KeyError:
            response.set_cookie(
                "user",
                "".join(
                    random.choice(string.ascii_lowercase + string.digits)
                    for _ in range(12)
                ),
            )
            return response
