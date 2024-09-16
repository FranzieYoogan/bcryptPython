from crypt import methods
from flask import request
from flask import Flask, render_template
import mysql.connector
from flask_bcrypt import Bcrypt 




app = Flask(__name__)
bcrypt = Bcrypt(app)




@app.route("/", methods=['GET', 'POST'])
def encrypt():
    alert = ""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Hash the password for comparison
        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Connect to the database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin123",
            database="passwordEncrypt"
        )
        mycursor = connection.cursor()
        
        # Execute the query
        mycursor.execute("SELECT userEmail, userPassword FROM userAccount WHERE userEmail = %s", (email,))
        result = mycursor.fetchone()
        
        if result:
            stored_email, stored_pw_hash = result
            if bcrypt.check_password_hash(stored_pw_hash, password):
                alert = True
            else:
                alert = False
        else:
            alert = "Email not found."
        
        # Close the connection
        connection.close()

    return render_template('index.htm', alert=alert)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    ok = ""
    error = ""

    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        try:
            # Use a new connection for this request
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="admin123",
                database="passwordEncrypt"
            )
            mycursor = connection.cursor()

            # Check if the email already exists
            mycursor.execute("SELECT userEmail FROM userAccount WHERE userEmail = %s", (email,))
            existing_email = mycursor.fetchone()

            if existing_email:
                error = "Email already exists"
            else:
                # Hash the password and insert the new user
                pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
                sql = "INSERT INTO userAccount (userEmail, userPassword) VALUES (%s, %s)"
                val = (email, pw_hash)
                mycursor.execute(sql, val)
                connection.commit()
                ok = "Sign-up successful"

            # Close the cursor and connection
            mycursor.close()
            connection.close()
        except mysql.connector.Error as e:
            error = True

    return render_template('signup.htm', ok=ok, error=error)

    
if __name__ == '__main__':
    app.run(debug=True)