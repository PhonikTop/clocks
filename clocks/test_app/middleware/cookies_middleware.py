class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        import string
        import random

        response = self.get_response(request)
        response.set_cookie("user",
                            ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(12)))

        return response
