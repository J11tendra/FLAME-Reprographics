from app.routes.auth_routes import auth_bp
from app.routes.upload_routes import upload_bp
from app.routes.payment_routes import payment_bp
from app.routes.dashboard_routes import dashboard_bp

__all__ = ["auth_bp", "upload_bp", "payment_bp", "dashboard_bp"]
