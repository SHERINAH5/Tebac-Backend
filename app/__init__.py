from flask import Flask, render_template_string
from app.extensions import db, migrate, jwt
from app.controllers.auth_controller import auth





def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

  
    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

  
    # Models 
    from app.models.users import User 
    from app.models.products import Product


    # Blueprints
    app.register_blueprint(auth, url_prefix="/api/v1/auth")

    # Health 
    
    @app.route("/")
    def index():
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Tebac Designers API</title>
            <style>
                body {
                    margin: 0;
                    font-family: Arial, sans-serif;
                    background-color: #fff7fb;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                }
                .card {
                    background-color: white;
                    border-radius: 12px;
                    box-shadow: 0 6px 25px rgba(0,0,0,0.12);
                    padding: 35px;
                    max-width: 420px;
                    text-align: center;
                    border-top: 6px solid #e91e63;
                }
                h1 {
                    color: #e91e63;
                    margin-bottom: 10px;
                }
                p {
                    color: #555;
                    font-size: 1rem;
                }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>Tebac Designers</h1>
                <p>Backend API is running successfully 🚀</p>
            </div>
        </body>
        </html>
        """)

    return app