from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class BurstRateThrottle(UserRateThrottle):
    """
    Throttle for burst requests (high frequency in short time).
    Used for sensitive operations like borrow/return.
    """
    scope = 'burst'
    rate = '10/minute'

class SustainedRateThrottle(UserRateThrottle):
    """
    Throttle for sustained requests over time.
    Used for general API calls.
    """
    scope = 'sustained'
    rate = '100/hour'

class AuthenticationRateThrottle(AnonRateThrottle):
    """
    Specific throttle for authentication endpoints to prevent brute force.
    """
    scope = 'auth'
    rate = '5/minute'