from fastapi import APIRouter

from boxbase.zones.admin.routers.admin import router as admin_router
from boxbase.zones.admin.routers.auth import router as auth_router
from boxbase.zones.admin.routers.roles import router as roles_router
from boxbase.zones.admin.routers.users import router as users_router

router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(users_router, tags=["Users & Memberships"])
router.include_router(roles_router, tags=["Roles & Permissions"])
router.include_router(admin_router, tags=["Admin"])
