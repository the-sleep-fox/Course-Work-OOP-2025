from .slots import router as slots_router
from .booking import router as booking_router
from .view import router as view_router

routers = [slots_router, booking_router, view_router]
