import ratelimit


class ScopeRateLimiter:
    def __init__(self, **kwargs):
        self.config = kwargs
        self.scopes = {}

    def check_limits(self, scope):
        result = True
        if scope not in self.scopes:
            self.scopes[scope] = ratelimit.limits(**self.config)(lambda : None)
        try:
            self.scopes[scope]()
        except ratelimit.exception.RateLimitException as e:
            result = False
        return result
