from flask import Flask,render_template,request,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_required,login_user,logout_user,LoginManager,current_user
from datetime import datetime
from flask_bcrypt import Bcrypt
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'JHGSGFY23KJ12AZEC32'
db = SQLAlchemy(app)
db.init_app(app)

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)


login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))





class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(200),nullable=False)
    password = db.Column(db.String(400),nullable=False)
    todos = db.relationship('Todo',backref='user')



class Todo(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    content = db.Column(db.String(200),nullable=False)
    completed= db.Column(db.Boolean,default=False,nullable=False)
    date_created = db.Column(db.DateTime,default=datetime.utcnow)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))








@app.route("/",methods=["GET","POST"])
@login_required
def index():
    if request.method == "POST":
        content = request.form["content"]
        todo= Todo(content=content,user=current_user)
        db.session.add(todo)
        db.session.commit()
        return redirect('/')
    else:
        todos = Todo.query.filter_by(user=current_user).order_by(Todo.date_created).all()
        return render_template("index.html",todos=todos)




@app.route("/delete/<id>")
def delete_todo(id):
    task = db.get_or_404(Todo,id)
    db.session.delete(task)
    db.session.commit()
    return redirect("/")




@app.route('/complete/<id>')
def complete_todo(id):
    task = db.get_or_404(Todo,id)
    task.completed = not task.completed
    db.session.commit()
    print(task.completed)
    return redirect('/')
  




@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user:
            if bcrypt.check_password_hash(user.password,password):
                login_user(user)
                
                return redirect('/')
            flash("Can't login with the provided credentials")
            return redirect('/login')
        else:
            flash("Can't login with the provided credentials")

            return redirect("/login")


        

    return render_template('login.html')


@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/signup',methods=["GET","POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password1 = request.form["password"]
        password2 = request.form["password2"]
        if password1 == password2:
            user = User(email=email,password=bcrypt.generate_password_hash(password1))
            db.session.add(user)
            db.session.commit()
            return redirect('/')
        
        
    return render_template('signup.html')

if __name__ == "__main__":
    app.run(debug=True)