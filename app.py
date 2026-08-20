import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import current_user, LoginManager, login_user, logout_user, login_required
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from models import Base, User, Service

load_dotenv()

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ============
# CONFIG FLASK
# ============
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")


# =================
# CONFIG SQLALCHEMY
# =================
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")
db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT")
db_name = os.environ.get("DB_NAME")

db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

engine = create_engine(db_url)

try:

    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    print("SUCCESS DB!")

except Exception as ex:
    print(ex)


# ==================
# CONFIG FLASK-LOGIN
# ==================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return session.query(User).get(int(user_id))

# =============
# ROUTES PUBLIC
# =============
# Erreur404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('public/page_not_found.html'), 404


# Accueil
@app.route("/")
def index():

    onglerie_services = (
        session.query(Service)
        .filter(Service.category_service == "Onglerie")
        .order_by(asc(Service.id))
        .all()
    )

    regard_services = (
        session.query(Service)
        .filter(Service.category_service == "Beauté du regard")
        .order_by(asc(Service.id))
        .all()
    )

    images = get_gallery_images()
    last_images = images[:4]  # 🔥 les 4 dernières ajoutées

    return render_template(
        "public/index.html",
        onglerie_services=onglerie_services,
        regard_services=regard_services,
        last_images=last_images
    )


# Nos réalisations
@app.route("/nos-realisations")
def nosRealisations():
    images = get_gallery_images()
    return render_template("public/nos-realisations.html", images=images)


# Mentions légales
@app.route("/mentions-legales")
def mentionsLegales():
    return render_template("public/mentions-legales.html")


# ============
# ROUTES ADMIN
# ============
# Connexion
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Vérifier que tous les champs requis sont remplis
        if not username:
            flash("L'identifiant est obligatoire. ", "error")
            return redirect(url_for('login'))

        if not password:
            flash("Le mot de passe est obligatoire. ", "error")
            return redirect(url_for('login'))

        # Vérifier qur l'utilisateur existe dans la DB
        user = session.query(User).filter_by(username=username).first()

        if not user:
            flash("Identifiant incorrect.", "error")
            return redirect(url_for('login'))
        
        # Vérifier que le mot de passe correspond à l'utilisateur
        if check_password_hash(user.password, password):
        
        # CConnecter l'utilisateur
            login_user(user)

        # Rediriger l'utilisateur vers son tableau de bord
            return redirect(url_for('dashboard'))

        else:
            flash("Le mot de passe ne correspond pas. ", "error")
            return redirect(url_for('login'))

    return render_template("admin/login.html")


# Déconnexion
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# Tableau de bord
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("admin/dashboard.html")


# Prestations
@app.route("/services")
@login_required
def services():
    onglerie_services = (
        session.query(Service)
        .filter(Service.category_service == "Onglerie")
        .order_by(asc(Service.id))
        .all()
    )

    regard_services = (
        session.query(Service)
        .filter(Service.category_service == "Beauté du regard")
        .order_by(asc(Service.id))
        .all()
    )

    return render_template("admin/services.html", onglerie_services=onglerie_services, regard_services=regard_services)


# Ajouter une prestation
@app.route("/add-service", methods=["GET", "POST"])
@login_required
def addService():
    if request.method == "POST":
        category_service = request.form.get("category_service")
        name_service = request.form.get("name_service")
        price_service = request.form.get("price_service")

        # Vérifier que tous les champs requis sont remplis
        if not category_service:
            flash("La catégorie est obligatoire.", "error")
            return redirect(url_for("addService"))
        if not name_service:
            flash("Le nom de la prestation est obligatoire.", "error")
            return redirect(url_for("addService"))
        if not price_service:
            flash("Le prix est obligatoire.", "error")
            return redirect(url_for("addService"))
        
        # Ajouter la prestation dans la DB
        newService = Service(
            category_service=category_service,
            name_service=name_service,
            price_service=price_service)
        
        session.add(newService)
        session.commit()
        
        flash("La prestation a bien été ajoutée.", "success")
        return redirect(url_for('services'))

    return render_template("admin/add-service.html")


# Éditer une prestation
@app.route("/edit-service/<int:service_id>", methods=["GET", "POST"])
@login_required
def edit_service(service_id):
    service = session.query(Service).filter_by(id=service_id).first()

    if not service:
        flash("Prestation introuvable.", "error")
        return redirect(url_for("services"))

    if request.method == "POST":
        category_service = request.form.get("category_service")
        name_service = request.form.get("name_service")
        price_service = request.form.get("price_service")

        if not category_service or not name_service or not price_service:
            flash("Tous les champs sont obligatoires.", "error")
            return redirect(url_for("edit_service", service_id=service_id))

        service.category_service = category_service
        service.name_service = name_service
        service.price_service = price_service

        session.commit()

        flash("La prestation a bien été modifiée.", "success")
        return redirect(url_for("services"))

    return render_template("admin/edit-service.html", service=service)


# Supprimer une prestation
@app.route("/delete-service/<int:service_id>", methods=["POST"])
@login_required
def delete_service(service_id):
    service = session.query(Service).filter_by(id=service_id).first()

    if not service:
        flash("Prestation introuvable.", "error")
        return redirect(url_for("services"))

    session.delete(service)
    session.commit()

    flash("La prestation a bien été supprimée.", "success")
    return redirect(url_for("services"))


# Récupérer les photos dans le répertoire static/images/galerie
def get_gallery_images():
    gallery_path = os.path.join(app.static_folder, "images/galerie")
    allowed_extensions = (".png", ".jpg", ".jpeg", ".webp")

    images = [
        file for file in os.listdir(gallery_path)
        if file.lower().endswith(allowed_extensions)
    ]

    # Trier par date de modification (plus récent en premier)
    images.sort(
        key=lambda file: os.path.getmtime(os.path.join(gallery_path, file)),
        reverse=True
    )

    return images


# Photos
@app.route("/images")
@login_required
def images():
    images = get_gallery_images()
    return render_template("admin/images.html", images=images)

# Ajouter une photo
@app.route("/add-image", methods=["GET", "POST"])
@login_required
def add_image():
    if request.method == "POST":
        if "image" not in request.files:
            flash("Aucun fichier envoyé.", "error")
            return redirect(url_for("add_image"))

        file = request.files["image"]

        if file.filename == "":
            flash("Aucun fichier sélectionné.", "error")
            return redirect(url_for("add_image"))

        if not allowed_file(file.filename):
            flash("Format de fichier non autorisé.", "error")
            return redirect(url_for("add_image"))

        filename = secure_filename(file.filename)
        gallery_path = os.path.join(app.static_folder, "images/galerie")
        file_path = os.path.join(gallery_path, filename)

        # éviter d'écraser un fichier existant
        if os.path.exists(file_path):
            flash("Une image avec ce nom existe déjà.", "error")
            return redirect(url_for("add_image"))

        file.save(file_path)
        flash("L'image a bien été ajoutée.", "success")
        return redirect(url_for("images"))

    return render_template("admin/add-image.html")


# Supprimer une photo
@app.route("/delete-image/<filename>", methods=["POST"])
@login_required
def delete_image(filename):
    gallery_path = os.path.join(app.static_folder, "images/galerie")
    file_path = os.path.join(gallery_path, filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        flash("Image supprimée.", "success")
    else:
        flash("Image introuvable.", "error")

    return redirect(url_for("images"))


# ===
# RUN
# ===
if __name__ == '__main__':
    app.run(debug=False)

