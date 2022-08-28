from flask import Flask, render_template,redirect,url_for,request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap  import Bootstrap
import  datetime as dt
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, URL

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///listtodo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db =SQLAlchemy(app)

# Global variables
db_listtodo_list =[]
db_count_task_by_list ={}
db_tasktodo_list =[]
db_get_all =1
wklist_name=''
wklist_id =0


# User management
class tbl_users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

# Configuration table tbl_list / tbl_task
class tbl_lists(db.Model):
    list_id     = db.Column(db.Integer, primary_key=True)
    list_name   = db.Column(db.String(250), unique=True, nullable=False)
    list_date   = db.Column(db.String(250), nullable=False)
    task_count  = db.Column(db.Integer, nullable=False)

class tbl_tasks(db.Model):
    list_id     = db.Column(db.Integer, primary_key=True)
    task_id     = db.Column(db.Integer, primary_key=True)
    task_name   = db.Column(db.String(250), unique=True, nullable=False)

# Definicion de Funciones
def fn_get_all_listtodo():
    global db_listtodo_list,db_count_task_by_list
    db_listtodo_list = db.session.query(tbl_lists).all()
    # for idx in range(len(db_listtodo_list)):
    #     db_count_task_by_list[db_listtodo_list[idx].list_id] = tbl_tasks.query.filter_by(list_id=db_listtodo_list[idx].list_id).count()

def fn_get_taskstodo(plist_id):
    global db_tasktodo_list,db_get_all
    db_get_all =0
    db_tasktodo_list = db.session.query(tbl_tasks).filter_by(list_id=plist_id).all()

def fn_del_listodo(plist_id):
    ## First del ALL tasks to do
    tasktodo_to_delete = tbl_tasks.query.filter_by(list_id=plist_id).all()
    for task_del in tasktodo_to_delete:
        db.session.delete(task_del)
        db.session.commit()
    #Second del the List to do
    list_to_delete = tbl_lists.query.get(plist_id)
    db.session.delete(list_to_delete)
    db.session.commit()

def fn_del_taskstodo(plist_id,ptask_id):
    tasktodo_to_delete = tbl_tasks.query.filter_by(list_id=plist_id, task_id=ptask_id).first()
    db.session.delete(tasktodo_to_delete)
    db.session.commit()
    fn_update_count_tasttodo(plist_id)

def fn_add_taskstodo(plist_id, ptask_name):
    # Adding a new task to do
    new_task_todo = tbl_tasks(list_id = plist_id
                              ,task_name=ptask_name)
    db.session.add(new_task_todo)
    db.session.commit()
    fn_update_count_tasttodo(plist_id =plist_id)

def fn_update_count_tasttodo(plist_id):
    ## Update the count task on list to do
    count_tastk_todo = tbl_tasks.query.filter_by(list_id=plist_id).count()
    list_to_update = tbl_lists.query.filter_by(list_id=plist_id).first()
    list_to_update.task_count = count_tastk_todo
    db.session.commit()

def fn_add_listtodo(plisttodo_name):
    new_list_todo = tbl_lists(list_name     =plisttodo_name
                              ,list_date    =dt.datetime.now()
                              ,task_count   =0
                              )
    db.session.add(new_list_todo)
    db.session.commit()

@app.route("/")
def fn_home():
    fn_get_all_listtodo()
    return render_template(template_name_or_list    ="index.html"
                           ,db_data_listtodo        = db_listtodo_list
                           ,db_data_tasktodo        = db_tasktodo_list
                           ,list_id                 = wklist_id
                           ,list_name               = wklist_name
                           )


@app.route("/fn_show_tasktodo/<wlist_id>,<wlist_name>",methods=["GET"])
def fn_show_taskstodo(wlist_id,wlist_name):
    global db_tasktodo_list,db_get_all,wklist_name,wklist_id
    wklist_name =wlist_name
    wklist_id   =wlist_id
    fn_get_taskstodo(plist_id=wlist_id)
    return redirect(url_for("fn_home"))

@app.route("/fn_delete_listtodo/<wlist_id>",methods=["GET"])
def fn_delete_listtodo(wlist_id):
    fn_del_listodo(plist_id=wlist_id)
    db_tasktodo_list.clear()
    db_listtodo_list.clear()
    return redirect(url_for("fn_home"))

@app.route("/fn_delete_taskstodo/<wlist_id>,<wtask_id>",methods=["GET"])
def fn_delete_taskstodo(wlist_id,wtask_id):
    fn_del_taskstodo(plist_id=wlist_id,ptask_id=wtask_id)
    fn_get_taskstodo(plist_id=wlist_id)
    return redirect(url_for("fn_home"))

@app.route("/fn_save_taskstodo/<wlist_id>",methods=["PATCH","POST","GET"])
def fn_save_taskstodo(wlist_id):
    if request.method == 'POST':
        fn_add_taskstodo(plist_id=wlist_id
                         ,ptask_name=request.form['desc_task'])
        fn_get_taskstodo(plist_id=wlist_id)
    return redirect(url_for("fn_home"))

@app.route("/fn_save_listtodo",methods=["PATCH","POST","GET"])
def fn_save_listtodo():
    if request.method == 'POST':
        fn_add_listtodo(plisttodo_name=request.form['desc_listtodo'])
        return redirect(url_for("fn_home"))
    return  render_template(template_name_or_list="add.html")

@app.route("/fn_manage_listtodo",methods=["PATCH","POST","GET"])
def fn_manage_listtodo():
    fn_get_all_listtodo()

    if request.method == 'POST':
        fn_add_listtodo(plisttodo_name=request.form['desc_listtodo'])
        return redirect(url_for("fn_home"))

    return  render_template(template_name_or_list="manage.html"
                            ,db_data_listtodo=db_listtodo_list
                            )

if __name__ == '__main__':
    app.run(debug=True)
