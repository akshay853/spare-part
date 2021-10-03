from flask import Flask, request, session, redirect, url_for, render_template,send_file,send_from_directory
from flaskext.mysql import MySQL
import pymysql 
import re 
from flask_session import Session
from pymysql import cursors
from werkzeug.utils import secure_filename
import os 

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app) 
app.secret_key = 'spare'
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'spare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
UPLOAD_FOLDER = 'static/product_image'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def view_product():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT * from products')
    result = cursor.fetchall()
    return result

@app.route('/')
def mainhome():
    return render_template('mainhome.html')

@app.route('/logout')
def logout():
    session.clear
    session['id'] = ""
    return render_template('mainhome.html')


@app.route('/loginPage')
def loginPage():
    return render_template('login.html')

@app.route('/registerPage')
def registerPage():
    return render_template('userreg.html')

@app.route('/registration',methods=['GET', 'POST'])
def register():
    print('hello')
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    msg = ''

    if request.method == 'POST': #and 'username' in request.form and 'password' in request.form and 'email' in request.form:     
        userid = request.form['userid']
        name = request.form['username']
        address = request.form['address']
        phonenumber = request.form['phone_no']
        password = request.form['pass']
        options = request.form['user']
   
        cursor.execute('SELECT * FROM user_reg WHERE name = %s', (name))
        user_reg = cursor.fetchone()
       
        if user_reg:
            msg = 'Account already exists!'
        elif not re.match(r'[A-Za-z0-9]+', name):
            msg = 'Invalid name!'
        elif not re.match(r'[A-Za-z0-9]+', address):
            msg = 'Invalid address!'
        elif not re.match(r'[0-9]+', phonenumber):
            msg = 'Invalid phonenumber!'
        elif not re.match(r'[A-Za-z0-9]+', password):
            msg = 'Invalid password!'
        elif not name or not password:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO user_reg VALUES (%s, %s, %s, %s, %s, %s)', (userid, name, phonenumber,address, password,options)) 
            conn.commit()
   
            msg = 'You have successfully registered!'
            return render_template('userreg.html', msg=msg)
    # elif request.method == 'POST':
        
    #     msg = 'Please fill out the form!'
    return render_template('userreg.html', msg=msg)

@app.route('/login', methods=['GET', 'POST'])
def login():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    msg = ''
    if request.method == 'POST':#and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor.execute('SELECT * FROM user_reg WHERE name = %s AND password = %s', (username, password))
        login = cursor.fetchone()
        if(username == "admin" and password == "admin"):
            filename = os.listdir("static/product_image")
            result = view_product()
            return render_template('adminhome.html',data=result, filenames = filename)
        options = login['options']
        if login:
            session['loggedin'] = True
            session['id'] = login['u_id']
            session['username'] = login['name']
            if options=="seller":
                # session['id'] = "ii"
                filename = os.listdir("static/product_image")
                result = view_product()
                print(result)
                return render_template("clienthome.html",data=result, filenames = filename)
            elif options=="user":
                # session['id'] = "ii"
                # path = os.path.join(app.config['UPLOAD_FOLDER'])
                filename = os.listdir("static/product_image")
                result = view_product()
                print(result)
                return render_template("userhome.html",data=result, filenames = filename)
            # elif username =='admin' and password == 'admin':
            #     return render_template('adminhome.html')
            else:
                return '''<script>alert("invalid User");window.location="/"</script>'''
    else:
        return '''<script>alert("Not a user...Please Sign up...!!!");window.location="/"</script>'''

        #     return redirect(url_for('home'))
        # else:
        #     msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

@app.route('/editprofile')
def editprofile():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT * FROM user_reg WHERE u_id = %s', [session['id']])
    user_reg = cursor.fetchone()
    print(user_reg)
    return render_template('editprofile.html',data=user_reg) 

@app.route('/updateuser',methods=['GET','POST'])
def updateuser():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    u_id = request.form['u_id']
    name = request.form['name']
    address = request.form['address']
    phone = request.form['phone']
    password = request.form['password']
    cur.execute("UPDATE user_reg SET u_id = %s, name = %s, phn_no = %s, address = %s, password = %s WHERE u_id = %s",
    (u_id,name,phone,address,password,u_id))
    conn.commit()       
    cur.close()
    msg = 'Record successfully Updated'   
    return render_template("userhome.html")
    return render_template('viewuser.html')
@app.route('/userhome')
def userhome():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    # path = os.path.join(app.config['UPLOAD_FOLDER'])
    filename = os.listdir("static/product_image")
    return render_template("userhome.html",data=products, filenames = filename)

@app.route('/clienthome')
def clienthome():
    return render_template('clienthome.html')

#ADMIN modules goes from here!
@app.route('/adminhome')
def adminhome():
    filename = os.listdir("static/product_image")
    result = view_product()
    return render_template('adminhome.html',data=result, filenames = filename)

@app.route('/addclientpage')
def addclientpage():
    return render_template("addclient.html")

@app.route('/addclient', methods=['POST'])
def addclient():
    c_id = request.form['c_id']
    c_name = request.form['c_name']
    phonenumber = request.form['phn_no']
    address = request.form['address']
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('INSERT INTO client VALUES (%s, %s, %s, %s)', (c_id, c_name,phonenumber,address)) 
    conn.commit()
    msg = 'add client sucessfully!'
    return render_template('addclient.html', msg=msg)
    return redirect(url_for('login'))


@app.route('/viewclient')
def viewclient():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT * FROM client')
    client = cursor.fetchall()
    return render_template("view_n_update_client.html",data = client)

@app.route("/editclient", methods=['GET','POST'])
def editclient():
    c_id = request.form['c_ids']
    print(c_id)
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('select * from client where c_id = %s',(c_id))
    result = cursor.fetchone()
    return render_template("updateclient.html",data=result)

@app.route('/updateclient',methods=['POST'])
def updateclient():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    c_id = request.form['c_id']
    c_name = request.form['c_name']
    phone = request.form['phn_no']
    address = request.form['address']
    cur.execute("UPDATE client SET c_id = %s, c_name = %s, phn_no = %s, address = %s WHERE c_id = %s ",
    (c_id,c_name,phone,address,c_id))
    conn.commit()      
    cur.close()
    msg = 'client successfully Updated'   
    #return render_template("updateclient.html",data=msg)
    return '''<script>alert("updated !");window.location="/adminhome"</script>'''

@app.route('/viewuser')
def viewuser():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT * FROM user_reg')
    user_reg = cursor.fetchall() 
    return render_template('viewuser.html',data=user_reg)


@app.route('/loadproductpage')
def loadproductpage():
    return render_template('addproducts.html')

@app.route('/addproduct', methods =['GET','POST'])
def addproperty():
    productid = request.form['p_id']
    name = request.form['p_name']
    modelnumber = request.form['model_no']
    price = request.form['price']
    productdetails = request.form['pdt']
    image = request.files['images']
    conn = mysql.connect()
    filename = secure_filename(image.filename)
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('INSERT INTO products VALUES (%s, %s, %s, %s, %s)', (productid, name, modelnumber, price,productdetails)) 
    conn.commit()
    msg = 'add product sucessfully!'
    return '''<script>alert('add product sucessfully!');window.location="/clienthome"</script>'''
    return redirect(url_for('login'))

@app.route('/viewproduct')
def viewproduct():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    path = os.path.join(app.config['UPLOAD_FOLDER'])
    print(path)
    filename = os.listdir("static/product_image")
    print(filename)
    return render_template('viewproduct.html',data=products, filenames = filename)




@app.route("/updateproduct")
def updateproduct():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('select * from products')
    result = cursor.fetchall()

    return render_template('updateproduct.html',data=result)

@app.route("/upproduct", methods = ['POST'])
def upproduct():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    p_id = request.form['p_id']
    name = request.form['p_name']
    model = request.form['model_no']
    price = request.form['price']
    pdt = request.form['pdt']
    # image = request.files['images']
    # filename = secure_filename(image.filename)
    # image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    cur.execute("UPDATE products SET p_id = %s,name = %s, model_no = %s, price = %s, p_details = %s WHERE p_id = %s ",
    (p_id,name,model,price,pdt,p_id))
    conn.commit() 
    cur.close()
    msg = 'product successfully Updated'   
    #return (msg)
    return '''<script>alert("updated!");window.location="/clienthome"</script>'''
    return redirect(url_for('login'))

@app.route("/addCat")
def addCat():
    return render_template("addcategories.html")

@app.route('/addcategories',methods=['POST'])
def addcategories():
    catid = request.form['cat_id']
    catname = request.form['cat_name']
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('INSERT INTO categories VALUES (%s, %s)', (catid, catname)) 
    conn.commit()
    msg = 'add categories sucessfully!'
    return '''<script>alert("updated!");window.location="/clienthome"</script>'''



@app.route('/viewcategories')
def viewcategoies():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('SELECT * FROM categories ')
    categories = cursor.fetchall()
    return render_template('viewcategories.html',data = categories) 
    return redirect(url_for('login'))

@app.route('/updateCat')
def updateCat():
    return render_template('updatecategory.html')

@app.route('/updatecategories',methods=['POST'])
def updatecategories():
    conn = mysql.connect()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cat_id = request.form['cat_id']
    cat_name = request.form['cat_name']
    cur.execute("UPDATE categories SET cat_id = %s, cat_name=%s WHERE cat_id = %s ",(cat_id,cat_name,cat_id))
    conn.commit()      
    cur.close()
    msg = 'categories successfully Updated'   
    return '''<script>alert("updated!");window.location="/clienthome"</script>'''

@app.route('/viewRating',methods=['GET','POST'])
def viewRating():
    names = request.form['name']
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("select * from products where name = %s",(names))
    result = cursor.fetchone()
    return render_template('111111111.html', data=names,results = result)

@app.route("/addrating",methods=['POST'])
def addrating():
    proid = request.form['nameaa']
    rate = request.form['rate']
    desc = request.form['subject']
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('INSERT INTO rating VALUES (%s, %s, %s)',(proid, rate, desc)) 
    conn.commit()
    return '''<script>alert("rating added!");window.location="/userhome"</script>'''

@app.route("/viewrating")
def viewrating():
    filename = os.listdir("static/product_image")
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("select * from rating")
    result = cursor.fetchall()
    cursor.execute("select * from products")
    product = cursor.fetchall()
    return render_template("viewrating.html",rating=result,data=product,filenames=filename)


if __name__ == '__main__':
    app.run(debug=True)

