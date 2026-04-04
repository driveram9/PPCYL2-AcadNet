from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    usuario = request.form['usuario']
    contrasenia = request.form['contrasenia']


    if usuario == "AdminPPCYL2" and contrasenia == "AdminPPCYL2771":
        return redirect(url_for("admin_dashboard"))
    else:
        return ("Lo sentimos, no fue posible encontrar el usuario ingresado")

@app.route("/admin")
def admin_dashboard():
    return render_template("admin.html")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
