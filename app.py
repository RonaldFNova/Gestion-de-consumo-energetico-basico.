
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///GestionEnergia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Modelo de roles
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)  # Ej: 'admin', 'usuario'
    descripcion = db.Column(db.String(120))
    users = db.relationship('User', backref='role', lazy=True)

# Modelo de usuario con relación a Role
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

    def __repr__(self):
        return f'<User {self.nombre} ({self.role.nombre})>'

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        return redirect(url_for('home'))
    return render_template('Usuarios/registro.html')


@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        return redirect(url_for('home'))
    return render_template('Datos/formulario.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('home'))
    return render_template('Usuarios/login.html')

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True) 