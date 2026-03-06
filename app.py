from flask import Flask, render_template, request, redirect, session, url_for, flash
import mysql.connector 
import qrcode
import os

app = Flask(__name__)
app.secret_key = 'secretul_tau_aici'

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        port=3006,
        user='app',
        password='covrigi',
        database='lifecard'
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password_hash']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            'SELECT * FROM User WHERE email = %s AND password_hash = %s', (email, password)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect(url_for('index'))
        else:
            flash('Email sau parolă incorectă')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password_hash = request.form['password_hash']
        phone = request.form['phone']
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO User (name, email, password_hash, phone) VALUES (%s, %s, %s, %s)',
                (name, email, password_hash, phone)
            )
            conn.commit()
            flash('Cont creat cu succes. Te poți autentifica.')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash('Emailul există deja în baza de date!')
        finally:
            cursor.close()
            conn.close()
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    user_id = session['user_id']
    cursor1 = conn.cursor(dictionary=True)
    
    cursor1.execute('''
        SELECT s.start_date, s.end_date, s.status,
               c.card_code, c.issued_at
        FROM Subscription s
        LEFT JOIN Card c ON c.user_id = s.user_id
        WHERE s.user_id = %s AND s.status = 'active' AND s.start_date <= CURDATE()
        ORDER BY s.end_date DESC
        LIMIT 1
    ''', (user_id,))
    subs = cursor1.fetchone()

    future_sub = None
    if not subs:
        cursor1.execute('''
            SELECT s.start_date, s.end_date, s.status,
                   c.card_code, c.issued_at
            FROM Subscription s
            LEFT JOIN Card c ON c.user_id = s.user_id
            WHERE s.user_id = %s AND s.status = 'active' AND s.start_date > CURDATE()
            ORDER BY s.start_date ASC
            LIMIT 1
        ''', (user_id,))
        future_sub = cursor1.fetchone()

    cursor1.close()

    cursor2 = conn.cursor(dictionary=True)
    cursor2.execute('''
        SELECT v.visit_time, v.visit_date, g.name AS gym_name
        FROM VisitLog v
        JOIN Gym g ON v.gym_id = g.id
        WHERE v.user_id = %s
        ORDER BY v.visit_time DESC
    ''', (user_id,))
    visits = cursor2.fetchall()
    cursor2.close()
    conn.close()

    qr_filename = None
    if subs and subs['card_code']:
        img = qrcode.make(subs['card_code'])
        qr_filename = f"static/qr_{user_id}.png"
        img.save(qr_filename)

    return render_template('index.html', subs=subs, visits=visits, qr_image=qr_filename, future_sub=future_sub)

@app.route('/search_gyms', methods=['GET'])
def search_gyms():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    gyms = []
    if 'city' in request.args:
        city = request.args.get('city')
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            'SELECT * FROM Gym WHERE city LIKE %s', ('%' + city + '%',)
        )
        gyms = cursor.fetchall()
        cursor.close()
        conn.close()
    return render_template('gym_search.html', gyms=gyms)

@app.route('/cumpara', methods=['GET', 'POST'])
def cumpara():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    from datetime import date, datetime
    import calendar
    import re

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    user_id = session['user_id']

    cursor.execute('''
        SELECT s.start_date, s.end_date, s.status,
               c.card_code, c.issued_at
        FROM Subscription s
        LEFT JOIN Card c ON c.user_id = s.user_id
        WHERE s.user_id = %s
        ORDER BY s.end_date DESC
        LIMIT 1
    ''', (user_id,))
    rows = cursor.fetchall()
    subs = rows[0] if rows else None

    errors = []

    if request.method == 'POST':
        card_nmb = request.form.get('card_nmb', '').strip()
        pin = request.form.get('pin', '').strip()
        cvv = request.form.get('cvv', '').strip()
        data_exp = request.form.get('data_exp', '').strip()
        data_act_str = request.form.get('data_act', '').strip()

        if not re.fullmatch(r'\d{16}', card_nmb):
            errors.append("Numărul cardului trebuie să conțină exact 16 cifre.")
        if not re.fullmatch(r'\d{4}', pin):
            errors.append("PIN-ul trebuie să conțină exact 4 cifre.")
        if not re.fullmatch(r'\d{3}', cvv):
            errors.append("CVV-ul trebuie să conțină exact 3 cifre.")

        today = date.today()

        if subs and subs['status'] == 'active':
            try:
                end_date = subs['end_date']
                if isinstance(end_date, str):
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

                start_date = subs['start_date']
                if isinstance(start_date, str):
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

                year = end_date.year + (end_date.month // 12)
                month = end_date.month % 12 + 1
                last_day = calendar.monthrange(year, month)[1]
                new_end_date = date(year, month, last_day)
            except Exception as e:
                errors.append("Eroare la prelungirea abonamentului.")
        else:
            try:
                data_act_date = datetime.strptime(data_act_str, '%Y-%m-%d').date()
                if data_act_date <= today:
                    errors.append("Data de activare trebuie să fie după ziua de azi.")
                start_date = data_act_date
                last_day = calendar.monthrange(start_date.year, start_date.month)[1]
                new_end_date = date(start_date.year, start_date.month, last_day)
            except ValueError:
                errors.append("Data de activare nu este validă.")
                start_date = None
                new_end_date = None

        if errors:
            cursor.execute('''
                SELECT v.visit_time, g.name AS gym_name
                FROM VisitLog v
                JOIN Gym g ON v.gym_id = g.id
                WHERE v.user_id = %s
                ORDER BY v.visit_time DESC
            ''', (user_id,))
            visits = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template('cumpara.html', subs=subs, visits=visits, errors=errors)

        start_date_str = start_date.strftime('%Y-%m-%d') if hasattr(start_date, 'strftime') else start_date
        new_end_date_str = new_end_date.strftime('%Y-%m-%d') if hasattr(new_end_date, 'strftime') else new_end_date

        cursor.execute('''
            INSERT INTO Subscription (user_id, gym_id, start_date, end_date, status)
            VALUES (%s, %s, %s, %s, %s)
        ''', (user_id, 1, start_date_str, new_end_date_str, 'active')) 

        conn.commit()
        flash("Abonamentul a fost actualizat cu succes.")
        cursor.close()
        conn.close()
        return redirect(url_for('cumpara'))

    cursor.execute('''
        SELECT v.visit_time, g.name AS gym_name
        FROM VisitLog v
        JOIN Gym g ON v.gym_id = g.id
        WHERE v.user_id = %s
        ORDER BY v.visit_time DESC
    ''', (user_id,))
    visits = cursor.fetchall()

    qr_filename = None
    if subs and subs['card_code']:
        img = qrcode.make(subs['card_code'])
        qr_filename = f"static/qr_{user_id}.png"
        img.save(qr_filename)

    cursor.close()
    conn.close()
    return render_template('cumpara.html', subs=subs, visits=visits, qr_image=qr_filename)

@app.route('/delete_account', methods=['POST'])
def delete_account(): 
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM VisitLog WHERE user_id = %s', (user_id,))
    cursor.execute('DELETE FROM Subscription WHERE user_id = %s', (user_id,))
    cursor.execute('DELETE FROM Card WHERE user_id = %s', (user_id,))
    cursor.execute('DELETE FROM User WHERE id = %s', (user_id,))

    conn.commit()
    cursor.close()
    conn.close()

    session.clear()
    flash("Contul tău a fost șters cu succes.")
    return redirect(url_for('signup'))

if __name__ == '__main__':
    app.run(debug=True)
