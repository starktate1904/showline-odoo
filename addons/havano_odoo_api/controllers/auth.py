from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

class HavanoAuthController(http.Controller):
    def _company_context(self):
        company = None
        allowed_companies = []
        if request.session.uid:
            user = request.env["res.users"].sudo().browse(request.session.uid)
            if user.exists():
                company = {"id": user.company_id.id, "name": user.company_id.name}
                allowed_companies = [
                    {"id": comp.id, "name": comp.name}
                    for comp in user.company_ids
                ]
        return {"company": company, "allowed_companies": allowed_companies}
    
    @http.route("/api/v1/auth/login", auth="public", methods=["POST"], type="http", csrf=False)
    def login(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data.decode())
            if "params" in data:
                data = data["params"]
        except:
            data = {}
        
        db = data.get("db", request.env.cr.dbname)
        login = data.get("login")
        password = data.get("password")
        
        if not login or not password:
            company_ctx = self._company_context()
            return request.make_json_response({
                "success": False,
                "error": "Login and password are required.",
                "code": 400,
                "company": company_ctx["company"],
                "allowed_companies": company_ctx["allowed_companies"],
            }, status=400)
        
        try:
            request.session.db = db
            credentials = {
                "login": login,
                "password": password,
                "type": "password",
            }
            env_for_db = request.env
            if request.env.cr.dbname != db:
                company_ctx = self._company_context()
                return request.make_json_response({
                    "success": False,
                    "error": "Database mismatch for current server session.",
                    "code": 400,
                    "company": company_ctx["company"],
                    "allowed_companies": company_ctx["allowed_companies"],
                }, status=400)

            auth_info = request.session.authenticate(env_for_db, credentials)
            uid = auth_info.get("uid")
            
            if not uid:
                company_ctx = self._company_context()
                return request.make_json_response({
                    "success": False,
                    "error": "Invalid credentials.",
                    "code": 401,
                    "company": company_ctx["company"],
                    "allowed_companies": company_ctx["allowed_companies"],
                }, status=401)
            
            request.session.uid = uid
            request.session.login = login
            
            user = request.env['res.users'].sudo().browse(uid)
            _logger.info("LOGIN SUCCESS: %s (id=%s)", user.name, user.id)
            
            company_ctx = self._company_context()
            return request.make_json_response({
                "success": True,
                "data": {
                    "user_id": user.id,
                    "user_name": user.name,
                    "user_email": user.email,
                    "company_id": user.company_id.id,
                    "company_name": user.company_id.name,
                    "session_id": request.session.sid,
                    "database": db,
                },
                "message": "Login successful",
                "company": company_ctx["company"],
                "allowed_companies": company_ctx["allowed_companies"],
            })
            
        except Exception as exc:
            _logger.error("Login failed: %s", str(exc))
            company_ctx = self._company_context()
            return request.make_json_response({
                "success": False,
                "error": "Invalid credentials.",
                "code": 401,
                "company": company_ctx["company"],
                "allowed_companies": company_ctx["allowed_companies"],
            }, status=401)
    
    @http.route("/api/v1/auth/logout", auth="public", methods=["POST"], type="http", csrf=False)
    def logout(self, **kwargs):
        if request.session.uid:
            request.session.logout()
        company_ctx = self._company_context()
        return request.make_json_response({
            "success": True,
            "data": {},
            "message": "Logged out successfully.",
            "company": company_ctx["company"],
            "allowed_companies": company_ctx["allowed_companies"],
        })
    
    @http.route("/api/v1/auth/me", auth="public", methods=["GET"], type="http", csrf=False)
    def get_current_user(self, **kwargs):
        if not request.session.uid:
            company_ctx = self._company_context()
            return request.make_json_response({
                "success": False,
                "error": "Please login first.",
                "code": 401,
                "company": company_ctx["company"],
                "allowed_companies": company_ctx["allowed_companies"],
            }, status=401)
        
        user = request.env['res.users'].sudo().browse(request.session.uid)
        
        company_ctx = self._company_context()
        return request.make_json_response({
            "success": True,
            "data": {
                "user_id": user.id,
                "user_name": user.name,
                "user_email": user.email,
                "company_id": user.company_id.id,
                "company_name": user.company_id.name,
                "authenticated": True,
            },
            "company": company_ctx["company"],
            "allowed_companies": company_ctx["allowed_companies"],
        })