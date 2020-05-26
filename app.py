from flask import Flask, render_template, url_for, request , redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.static_folder = 'static'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(200), nullable = False)
    complete = db.Column(db.Integer, default = 0)
    date_created = db.Column(db.DateTime,default = datetime.utcnow )

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/', methods = ['GET','POST'])
def index():
    if request.method  == 'POST':
        task_content = request.form['content']
        if task_content == '':
            return 'abc'
        else: 
            new_task = Todo(content = task_content)
            try: 
                db.session.add(new_task)
                db.session.commit()
                return redirect('/')
            except:
                return 'There is some error in creating your task'
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'there is some error in deleting your task'

@app.route('/update/<int:id>', methods = ['GET', 'POST'])
def update(id):
    task_to_update = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task_to_update.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There is some error in updating your task'
    else: 
        return render_template('update.html',task = task_to_update)

if __name__ == "__main__":
    app.run(debug=True, port=8000)