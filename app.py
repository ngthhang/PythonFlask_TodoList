from flask import Flask, render_template, url_for, request , redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
from datetime import datetime

# APP INIT 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
# app.config['SECRET_KEY'] = '09102000'
app.static_folder = 'static'
db = SQLAlchemy(app)

#APP LOGIN INIT
login_manager = LoginManager()
login_manager.init_app(app)

# APP DATABASE 
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    current_user = db.Column(db.Integer, nullable = False)
    content = db.Column(db.String(200), nullable = False)
    complete = db.Column(db.Integer, default = 0)
    date_created = db.Column(db.DateTime,default = datetime.utcnow )

    def __repr__(self):
        return '<Task %r>' % self.id

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(100), nullable = False)
    password = db.Column(db.String(200), nullable = False)

db.create_all()

# APP ROUTING 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect('/login')

@app.route('/login', methods = ['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    current_user = User.query.filter_by(email=email).first()
    login_user(current_user)
    return redirect('/')

@app.route('/login',methods = ['GET'])
def get_login():
    return render_template('login.html')

@app.route('/signup', methods = ['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    current_user = User(name=username,email=email,password=password)
    db.session.add(current_user)
    db.session.commit()
    current_user = User.query.filter_by(email=email).first()
    login_user(current_user)
    return redirect('/')

@app.route('/signup', methods = ['GET'])
def get_signup():
    return render_template('signup.html')

@app.route('/', methods = ['GET','POST'])
@login_required
def index():
    if request.method  == 'POST':
        task_content = request.form['content']
        if task_content == '':
            return render_template('error.html', message = 'Your task cant be null, please try another one')
        else: 
            new_task = Todo(content = task_content, current_user = current_user.id)
            try: 
                db.session.add(new_task)
                db.session.commit()
                return redirect('/')
            except:
                return render_template('error.html', message = 'There is some error in creating your task')
    else:
        tasks = Todo.query.filter_by(current_user = current_user.id).order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks, current_user = current_user)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return render_template('error.html', message = 'there is some error in deleting your task')

@app.route('/update/<int:id>', methods = ['GET', 'POST'])
@login_required
def update(id):
    task_to_update = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task_to_update.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return render_template('error.html',message = 'There is some error in updating your task')
    else: 
        return render_template('update.html',task = task_to_update)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True, port=8000)