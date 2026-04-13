from flask import redirect, url_for
from flask import Flask
from routes.auth import auth_bp
from routes.uploads import uploads_bp
from routes.reports import reports_bp
from routes.admin import admin_bp
from routes.student import student_bp
from routes.tutor import tutor_bp
import config

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(uploads_bp, url_prefix="/uploads")
    app.register_blueprint(reports_bp, url_prefix="/reports")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(student_bp, url_prefix="/student")
    
    app.register_blueprint(tutor_bp, url_prefix="/tutor")
    # ********************************************* REDIRIGE A AUTH_LOGIN***********************************************
    @app.route("/")
    def home():
        return redirect(url_for("auth.login_from"))

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=app.config["PORT"])

