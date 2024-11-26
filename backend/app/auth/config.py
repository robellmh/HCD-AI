import os

API_SECRET_KEY = os.getenv("API_SECRET_KEY", "my_secret_key")
# Authentication and Authorization
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dummy-secret-key")
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
