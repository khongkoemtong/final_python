from flask import Flask,jsonify,request
import pymysql
import os
import uuid
from flask_jwt_extended import JWTManager, create_access_token, jwt_required



app= Flask(__name__)


UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER


app.config['SECRET_KEY']="123"
jwt = JWTManager(app)



def connect_db():
    conection = pymysql.connect(
        host='localhost',
        user='root',
        passwd='',
        db='python_flask',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    if not conection :
        print("can not connect to database ! 🥲")

    print("connect success ! ")
    return conection

@app.route('/create-product',methods=['POST'])
@jwt_required()
def Create():
    conection = connect_db()
    cursor = conection.cursor()
    name = request.form['Name']
    price = request.form['Price']
    qty = request.form['Qty']
    file = request.files['Image']

    if file:
        end_name = os.path.splitext(file.filename)[1]
        filename = str(uuid.uuid4())+end_name
        file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))


    sql = "INSERT INTO products (Name,Price,Qty,Image) values(%s,%s,%s,%s)"
    cursor.execute(sql,(name,price,qty,filename))
    conection.commit()


    return jsonify({
        "message":"insert successs",
        })

@app.route('/read-product')
@jwt_required()
def read ():
    conection = connect_db()
    cursor = conection.cursor()

    cursor.execute( "SELECT * FROM products")
    product = cursor.fetchall()
    conection.commit

    conection.close()

    return jsonify({'data':product})

@app.route('/update/<int:id>',methods=['POST'])
def update(id):
    conection = connect_db()
    cursor = conection.cursor()

    name = request.form['Name']
    price = request.form['Price']
    qty = request.form['Qty']
    file = request.files['Image']

    filename = ""
    if file :
        end_name = os.path.splitext(file.filename)[1]
        filename = str(uuid.uuid4()) + end_name
        file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))

    sql = "UPDATE  products SET Name = %s , Price = %s , Qty =%s, Image=%s WHERE id = %s"

    cursor.execute(sql,(name,price,qty,filename,id))
    conection.commit()

    return jsonify("Update success !")


@app.route('/delete/<int:id>' ,methods=["DELETE"])

def delete (id):
    conection = connect_db()
    cursor = conection.cursor()

    sql = "DELETE FROM products WHERE id = %s"
    cursor.execute(sql,(id))
    conection.commit()

    return jsonify("delete successs")




@app.route('/register',methods=["POST"])
def register ():
    conection = connect_db()
    cursor = conection.cursor()

    email = request.form['email']
    password = request.form['password'] 
    username = request.form['username']

    sql = "INSERT INTO accounts (email,password,username) values (%s,%s,%s)"
    cursor.execute(sql,(email,password,username))
    user = cursor.fetchone
    conection.commit()

    return jsonify({'message':"success"})


@app.route('/login' ,methods=['POST'])
def login ():
    conection = connect_db()
    cursor = conection.cursor()

    email = request.form['email']
    password = request.form['password']

    sql = "SELECT * FROM accounts WHERE email = %s AND password = %s"

    cursor.execute(sql,(email,password))

    user = cursor.fetchone()

    if user :
        access_token = create_access_token(identity=user['email'])
        return jsonify(token=access_token)
    
    return jsonify(user)

if __name__=="__main__":
    app.run(debug=True,port=5000)