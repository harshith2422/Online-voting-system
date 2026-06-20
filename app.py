from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Configuration
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='Mysql@123',
        database='online_voting'
    )

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            return redirect('/dashboard')
        else:
            flash("Invalid login credentials!", "error")
            return redirect('/')

    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (name, email, address, password) VALUES (%s, %s, %s, %s)",
                           (name, email, address, password))
            conn.commit()
            flash("Registration successful, please login.", "success")
            return redirect('/')
        except mysql.connector.errors.IntegrityError:
            flash("Email already exists!", "error")
            return redirect('/register')
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    if 'user_id' not in session:
        return redirect('/')

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    cursor.execute("SELECT * FROM parties")
    parties = cursor.fetchall()

    cursor.execute("SELECT * FROM votes WHERE user_id = %s", (user_id,))
    vote = cursor.fetchone()

    conn.close()

    voted = bool(vote)
    if request.method == 'POST' and not voted:
        party_id = request.form['party_id']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO votes (user_id, party_id) VALUES (%s, %s)", (user_id, party_id))
        conn.commit()
        conn.close()
        return redirect('/dashboard')

    return render_template('dashboard.html', user=user, parties=parties, voted=voted)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
