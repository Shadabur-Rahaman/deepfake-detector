"""Authentication package. Imports are lazy so missing Redis cannot block startup."""

__all__ = [
    "AuthCore",
    "User",
    "Role",
    "Permission",
    "UserRole",
]
__version__ = "1.0.0"
