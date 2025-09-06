from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.sql import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///GestionEnergia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = "jaszvfhjhfsf468hji@gfgo,.gft4"  

db = SQLAlchemy(app)


class Roles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False) 
    descripcion = db.Column(db.String(120))
    Usuarios = db.relationship('Usuarios', backref='Roles', lazy=True)

class Usuarios(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    Roles_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    def __repr__(self):
        return f'<Usuarios {self.nombre} ({self.Roles.nombre})>'

class Login(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_hora = db.Column(db.DateTime, default=func.now())
    usuario = db.relationship('Usuarios', backref='logins')

class Datos(db.Model):
    id = db.Column(db.Integer, primary_key=True)    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tipo_energia = db.Column(db.String(50), nullable=False)
    lectura = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_registro = db.Column(db.Date, nullable=False)
    usuario = db.relationship('Usuarios', backref='datos')


@app.route('/')
def index():
    usuario_id = session.get('usuario_id')

    if not usuario_id:
        return render_template('index.html') 

    usuario = Usuarios.query.get(usuario_id)
    
    if usuario.Roles.nombre == 'usuario':
        return redirect(url_for('homeUser')) 
    
    if usuario.Roles.nombre == 'admin':
        return redirect(url_for('homeAdmin'))


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']

        correoExistente = Usuarios.query.filter_by(correo=correo).first()

        if correoExistente:
            error = 'El correo ya está registrado'
            return render_template('Usuarios/registro.html', error=error)
        
        password = request.form['password']
        Usuarios_Roles = Roles.query.filter_by(nombre='usuario').first()
        nuevo_usuario = Usuarios(
            nombre=nombre,
            correo=correo,
            password=password,
            Roles_id=Usuarios_Roles.id
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        session['usuario_id'] = nuevo_usuario.id 

        return redirect(url_for('homeUser')) 
    
    else:
        return render_template('Usuarios/registro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']

        usuario = Usuarios.query.filter_by(correo=correo, password=password).first()
        if not usuario:
            error = 'Correo o contraseña incorrectas'
            return render_template('Usuarios/login.html', error=error)

        usuario = Usuarios.query.get(usuario.id)
        session['usuario_id'] = usuario.id 

        nuevo_login = Login(usuario_id=usuario.id)

        db.session.add(nuevo_login)
        db.session.commit()

        if usuario.Roles.nombre != 'admin':
            return redirect(url_for('homeUser'))
        
        return redirect(url_for('homeAdmin'))
    
    else:
        return render_template('Usuarios/login.html')


@app.route('/registroDatos', methods=['GET', 'POST'])
def registroDatos():
    if request.method == 'POST':
        tipoEnergia = request.form['tipo_energia']
        fechaRegistro = request.form['fecha']
        lectura = request.form['lectura']

        usuario_id = session.get('usuario_id') 
        if not usuario_id:
            return redirect(url_for('login')) 

        nuevo_dato = Datos(
            usuario_id=usuario_id,  
            tipo_energia=tipoEnergia,
            lectura=lectura,
            fecha_registro=datetime.strptime(fechaRegistro, '%Y-%m-%d').date()
        )

        db.session.add(nuevo_dato)
        db.session.commit()
    
    else:
        usuario_id = session.get('usuario_id') 
        if not usuario_id:
            return redirect(url_for('login')) 

    return render_template('Datos/formulario.html')


@app.route('/reportes', methods=['GET', 'POST'])
def reportes():
    usuario_id = session.get('usuario_id')
    usuario = Usuarios.query.get(usuario_id)

    if request.method == 'GET':
        if not usuario_id:
            return redirect(url_for('login')) 
    
        if usuario.Roles.nombre != 'usuario':
            return redirect(url_for('homeAdmin'))

        consumos = Datos.query.filter_by(usuario_id=usuario_id).all()
        return render_template('Reportes/consumo.html', consumos=consumos)


@app.route('/homeUser' )
def homeUser():
    usuario_id = session.get('usuario_id') 
    usuario = Usuarios.query.get(usuario_id)

    if not usuario_id:
        return redirect(url_for('login')) 
    
    if usuario.Roles.nombre != 'usuario':
        return redirect(url_for('homeAdmin')) 
    
    return render_template('Usuarios/home.html', usuario=usuario)
    

@app.route('/homeAdmin')
def homeAdmin():
    usuario_id = session.get('usuario_id') 
    usuario = Usuarios.query.get(usuario_id)

    if not usuario_id:
        return redirect(url_for('login'))
    
    if usuario.Roles.nombre != 'admin':
        return redirect(url_for('homeUser')) 
    
    return render_template('Admin/home.html', usuario_id=usuario_id)


@app.route('/cerrarSesion')
def cerrarSesion():
    session.pop('usuario_id')  
    return redirect(url_for('index'))


@app.route('/editarPerfil', methods=['GET', 'POST'])
def editarPerfil():

    usuario_id = session.get('usuario_id') 
    usuario = Usuarios.query.get(usuario_id)

    if not usuario_id:
        return redirect(url_for('login'))
    
    if usuario.Roles.nombre != 'usuario':
        return redirect(url_for('homeAdmin')) 

    if request.method == 'GET':
          
        return render_template('Usuarios/editarPerfil.html')
    
    else:
        actual = request.form['actual']
        nueva = request.form['nueva']
        confirmar = request.form['confirmar']

        if actual != usuario.password:
            error = 'La contraseña actual es incorrecta'
            return render_template('Usuarios/editarPerfil.html', error=error)
        
        if nueva != confirmar:
            error = 'La nueva contraseña y la confirmación no coinciden'
            return render_template('Usuarios/editarPerfil.html', error=error)

        usuario.password = nueva
        db.session.commit()

        return redirect(url_for('homeUser'))


@app.route('/logins', methods=['GET'])
def logins():
    usuario_id = session.get('usuario_id')
    usuario = Usuarios.query.get(usuario_id)

    if not usuario_id:
        return redirect(url_for('login')) 
    
    if usuario.Roles.nombre != 'admin':
        return redirect(url_for('homeUser'))

    if request.method == 'GET':

        registros_logins = Login.query.all()
        return render_template('Admin/gestionLogins.html', logins=registros_logins)


@app.route('/registros', methods=['GET'])
def registros():
    usuario_id = session.get('usuario_id')
    usuario = Usuarios.query.get(usuario_id)

    if not usuario_id:
        return redirect(url_for('login')) 
    
    if usuario.Roles.nombre != 'admin':
        return redirect(url_for('homeUser'))

    if request.method == 'GET':

        registros_usuarios = Usuarios.query.all()
        return render_template('Admin/gestionRegistros.html', usuarios=registros_usuarios)


@app.route('/editarUsuario/<int:usuario_id>', methods=['GET', 'POST'])
def editarUsuario(usuario_id):
    usuario_sesion_id = session.get('usuario_id') 
    usuario_sesion = Usuarios.query.get(usuario_sesion_id)

    if not usuario_sesion_id:
        return redirect(url_for('login'))

    if usuario_sesion.Roles.nombre != 'admin':
        return redirect(url_for('homeUser')) 

    usuario = Usuarios.query.get(usuario_id)
    if not usuario:
        return "Usuario no encontrado", 404

    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        rol_id = request.form['rol']  

        correo_existente = Usuarios.query.filter(Usuarios.correo == correo, Usuarios.id != usuario.id).first()
        if correo_existente:
            error = 'El correo ya está registrado por otro usuario'
            return render_template('Admin/editarUsuario.html', usuario=usuario, error=error)

        rol = Roles.query.get(rol_id) 

        if not rol:
            error = 'Rol no válido'
            return render_template('Admin/editarUsuario.html', usuario=usuario, error=error)

        usuario.nombre = nombre
        usuario.correo = correo
        usuario.Roles_id = rol.id

        if request.form['password']: 
            usuario.password = request.form['password']

        db.session.commit()
        return redirect(url_for('registros'))

    return render_template('Admin/editarUsuario.html', usuario=usuario,roles=Roles.query.all())


@app.route('/gestionConsumos', methods=['POST', 'GET'])
def gestionConsumos():
    usuario_id = session.get('usuario_id')
    usuario = Usuarios.query.get(usuario_id)

    if not usuario_id:
        return redirect(url_for('login')) 
    
    if usuario.Roles.nombre != 'admin':
        return redirect(url_for('homeUser'))

    if request.method == 'GET':

        usuarios = Usuarios.query.all()
        return render_template('Admin/gestionConsumo.html', usuarios=usuarios)
    
    if request.method == 'POST':
        usuario_id = request.form['usuario_id']
        usuario = Usuarios.query.get(usuario_id)
        if not usuario:
            return "Usuario no encontrado", 404

        tipoEnergia = request.form['tipo_energia']
        fechaRegistro = request.form['fecha']
        lectura = request.form['lectura']

        nuevo_dato = Datos(
            usuario_id=usuario.id,  
            tipo_energia=tipoEnergia,
            lectura=lectura,
            fecha_registro=datetime.strptime(fechaRegistro, '%Y-%m-%d').date()
        )

        db.session.add(nuevo_dato)
        db.session.commit()

        return redirect(url_for('gestionConsumos'))


@app.route('/listaConsumo', methods=['GET'])
def listaConsumo():
    usuario_id = session.get('usuario_id')
    usuario = Usuarios.query.get(usuario_id)

    if not usuario_id:
        return redirect(url_for('login')) 
    
    if usuario.Roles.nombre != 'admin':
        return redirect(url_for('homeUser'))

    if request.method == 'GET':
        consumos = Datos.query.all()
        return render_template('Admin/listaConsumo.html', consumos=consumos)
    

@app.route('/editarConsumo/<int:consumo_id>', methods=['POST'])
def editarConsumo(consumo_id):
    usuario_sesion_id = session.get('usuario_id') 
    usuario_sesion = Usuarios.query.get(usuario_sesion_id)

    if not usuario_sesion_id:
        return redirect(url_for('login'))

    if usuario_sesion.Roles.nombre != 'admin':
        return redirect(url_for('homeUser')) 

    consumo = Datos.query.get(consumo_id)
    if not consumo:
        return "Consumo no encontrado", 404

    if request.method == 'POST':
        tipoEnergia = request.form['tipo_energia']
        fechaRegistro = request.form['fecha']
        lectura = request.form['lectura']

        consumo.tipo_energia = tipoEnergia
        consumo.fecha_registro = datetime.strptime(fechaRegistro, '%Y-%m-%d').date()
        consumo.lectura = lectura

        db.session.commit()
        return redirect(url_for('listaConsumo'))

    return render_template('Admin/editarConsumo.html', consumo=consumo)


@app.route('/eliminarConsumo/<int:consumo_id>', methods=['GET'])
def eliminarConsumo(consumo_id):
    usuario_sesion_id = session.get('usuario_id') 
    usuario_sesion = Usuarios.query.get(usuario_sesion_id)

    if not usuario_sesion_id:
        return redirect(url_for('login'))

    if usuario_sesion.Roles.nombre != 'admin':
        return redirect(url_for('homeUser')) 

    if request.method == 'GET':
        consumo = Datos.query.get(consumo_id)
        if not consumo:
            return "Consumo no encontrado", 404

        db.session.delete(consumo)
        db.session.commit()
        return redirect(url_for('listaConsumo'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        admin_Roles = Roles.query.filter_by(nombre='admin').first()
        if not admin_Roles:
            admin_Roles = Roles(nombre='admin', descripcion='Administrador')
            db.session.add(admin_Roles)
        Usuarios_Roles = Roles.query.filter_by(nombre='usuario').first()
        if not Usuarios_Roles:
            Usuarios_Roles = Roles(nombre='usuario', descripcion='Usuario convencional')
            db.session.add(Usuarios_Roles)
        db.session.commit()

        admin_Usuarios = Usuarios.query.filter_by(correo='admin@email.com').first()
        if not admin_Usuarios:
            nuevo_admin = Usuarios(
                nombre='Administrador',
                correo='admin@email.com',
                password='admin123', 
                Roles_id=admin_Roles.id
            )
            db.session.add(nuevo_admin)
            db.session.commit()

    app.run(debug=True)
