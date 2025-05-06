import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, jsonify, Response, session
from datetime import datetime, timedelta
import csv
import io
from fpdf import FPDF
from flask import send_file

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Ganti dengan secret key yang aman
app.permanent_session_lifetime = timedelta(minutes=30)  # Durasi sesi login

# Konfigurasi koneksi ke database MySQL
db_config = {
    'host': 'localhost',       # Ganti dengan host MySQL Anda
    'user': 'root',            # Ganti dengan username MySQL Anda
    'password': 'Ritwan123@#',    # Ganti dengan password MySQL Anda
    'database': 'e_logbook'     # Ganti dengan nama database Anda
}

# Konfigurasi login
USERNAME = 'admin'
PASSWORD = '0ne'

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None  # Variabel untuk menyimpan pesan kesalahan
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            query = "SELECT * FROM userlogin WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            connection.close()

            if user:
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('index'))
            else:
                error = "Invalid username or password."  # Simpan pesan kesalahan
        except Exception as e:
            print("Error during login:", e)
            error = "An error occurred. Please try again later."

    # Render template login dengan pesan kesalahan (jika ada)
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)  # Hapus username dari session
    return redirect(url_for('login'))

def get_data_from_db(page=1, per_page=50):
    try:
        offset = (page - 1) * per_page
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        # Hitung total data
        cursor.execute("SELECT COUNT(*) FROM logbook WHERE status = 'To Do'")
        total_data = cursor.fetchone()[0]
        # Ambil data sesuai halaman
        query = """
            SELECT * FROM logbook
            WHERE status = 'To Do'
            ORDER BY no DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(query, (per_page, offset))
        data = cursor.fetchall()
        connection.close()
        return data, total_data
    except Exception as e:
        print("Database connection error:", e)
        return [], 0

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    page = int(request.args.get('page', 1))
    per_page = 50
    data, total_data = get_data_from_db(page, per_page)
    total_pages = (total_data + per_page - 1) // per_page
    user_login = session.get('username')
    return render_template(
        'index.html',
        data=data,
        user_login=user_login,
        page=page,
        total_pages=total_pages
    )

@app.route('/input', methods=['GET', 'POST'])
def input():
    if request.method == 'POST':
        try:
            no = request.form.get('no')
            id_ = request.form.get('id')
            detail = request.form.get('detail')
            note = request.form.get('note')
            created = request.form.get('created')
            in_time = request.form.get('in_time')
            status = request.form.get('status')
            by = request.form.get('by') or ""
            completed = request.form.get('completed') or None
            out_time = request.form.get('out_time') or None

            # Validasi data
            if not no or not id_ or not detail or not created or not in_time or not status:
                return jsonify({"error": "Data tidak lengkap."}), 400

            # Simpan data ke database
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            query = """
                INSERT INTO logbook (no, id, detail, note, created, in_time, status, `by`, completed, out_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (no, id_, detail, note, created, in_time, status, by, completed, out_time))
            connection.commit()
            connection.close()

            return jsonify({"success": True}), 200
        except Exception as e:
            print("Error saat menyimpan data:", e)
            return jsonify({"error": str(e)}), 500

    # GET request
    user_login = session.get('username')
    return render_template('input.html', user_login=user_login)
    

@app.route('/edit/<int:data_id>', methods=['GET', 'POST'])
def edit_data(data_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Ambil data dari form
        no = request.form.get('no')
        id_ = request.form.get('id')
        detail = request.form.get('detail')
        note = request.form.get('note')
        created = request.form.get('created')
        in_time = request.form.get('in_time')
        status = request.form.get('status')
        by = request.form.get('by') or None
        completed = request.form.get('completed')
        out_time = request.form.get('out_time')

        # Validasi: Kolom completed dan out_time tidak boleh kosong
        if not completed or not out_time:
            return "Kolom 'Completed' dan 'Out Time' tidak boleh kosong.", 400

        # Update data di database
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            query = """
                UPDATE logbook
                SET id = %s, detail = %s, note = %s, created = %s, in_time = %s, status = %s, `by` = %s, completed = %s, out_time = %s
                WHERE no = %s
            """
            cursor.execute(query, (id_, detail, note, created, in_time, status, by, completed, out_time, no))
            connection.commit()
            connection.close()
            return redirect(url_for('index'))
        except Exception as e:
            print("Error updating database:", e)
            return f"Error: {e}", 500

    # Ambil data dari database berdasarkan data_id
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Ambil data logbook berdasarkan ID
        query = "SELECT * FROM logbook WHERE no = %s"
        cursor.execute(query, (data_id,))
        data = cursor.fetchone()

        # Ambil daftar pengguna dari tabel userlogin
        query_users = "SELECT username FROM userlogin"
        cursor.execute(query_users)
        users = [row[0] for row in cursor.fetchall()]

        connection.close()

        # Format waktu untuk input HTML
        if data and data[5]:  # Indeks 5 adalah kolom in_time
            if isinstance(data[5], timedelta):  # Gunakan timedelta yang diimpor
                # Konversi timedelta menjadi string dalam format HH:MM
                total_seconds = int(data[5].total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                in_time = f"{hours:02}:{minutes:02}"
            else:
                # Jika data[5] sudah berupa string, gunakan langsung
                in_time = data[5]

            data = list(data)  # Ubah tuple menjadi list agar bisa dimodifikasi
            data[5] = in_time  # Perbarui nilai in_time
    except Exception as e:
        print("Error fetching data:", e)
        return f"Error: {e}", 500

    # Pastikan data dan daftar pengguna diteruskan ke template
    return render_template('edit.html', data=data, users=users)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    # Ambil data yang akan diedit berdasarkan ID
    data = get_data_by_id(id)  # Fungsi untuk mengambil data dari database
    # Ambil daftar pengguna dari database
    users = get_all_users()  # Fungsi untuk mengambil semua pengguna
    return render_template('edit.html', data=data, users=users)

@app.route('/get_next_no', methods=['GET'])
def get_next_no():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT MAX(no) FROM logbook")  # Ganti 'no' dengan kolom yang sesuai
        result = cursor.fetchone()
        connection.close()

        # Jika result[0] adalah None (tabel kosong), mulai dari 1
        next_no = (result[0] + 1) if result[0] is not None else 1
        return jsonify({'next_no': next_no})  # Pastikan respons berupa JSON
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Kembalikan error jika terjadi masalah

@app.route('/view_all')
def view_all():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = """
        SELECT * FROM logbook
        ORDER BY no DESC
    """
    cursor.execute(query)
    data = cursor.fetchall()
    connection.close()
    user_login = session.get('username')
    page = 1
    total_pages = 1
    return render_template(
        'index.html',
        data=data,
        user_login=user_login,
        page=page,
        total_pages=total_pages
    )

@app.route('/export', methods=['GET'])
def export_data():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        query = """
            SELECT * FROM logbook
            WHERE created BETWEEN %s AND %s
            ORDER BY no ASC
        """
        cursor.execute(query, (start_date, end_date))
        rows = cursor.fetchall()
        connection.close()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['No', 'ID', 'Detail', 'Note', 'Created', 'In Time', 'Status', 'By', 'Completed', 'Out Time'])
        for row in rows:
            writer.writerow(row)
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment;filename=logbook_{start_date}_to_{end_date}.csv'}
        )
    except Exception as e:
        print("Error exporting data:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/export_pdf', methods=['GET'])
def export_pdf():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        query = """
            SELECT * FROM logbook
            WHERE created BETWEEN %s AND %s
            ORDER BY no ASC
        """
        cursor.execute(query, (start_date, end_date))
        rows = cursor.fetchall()
        connection.close()

        pdf = FPDF(orientation='L', unit='mm', format='A4')  # Landscape agar lebih lebar
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        pdf.cell(0, 10, txt="Logbook Export", ln=True, align='C')
        pdf.ln(3)

        # Lebar kolom (dalam mm) untuk tiap field
        col_widths = [12, 12, 40, 100, 22, 18, 15, 20, 22, 18]
        headers = ['No', 'ID', 'Detail', 'Note', 'Created', 'In', 'Status', 'By', 'Completed', 'Out']

        # Header
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, header, border=1, align='C')
        pdf.ln()

        # Data
        for row in rows:
            for i, item in enumerate(row[:10]):  # Pastikan hanya 10 kolom
                # Potong string jika terlalu panjang
                text = str(item) if item is not None else ''
                if len(text) > 20:
                    text = text[:17] + '...'
                pdf.cell(col_widths[i], 8, text, border=1)
            pdf.ln()

        pdf_bytes = pdf.output(dest='S').encode('latin1')
        return Response(
            pdf_bytes,
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment;filename=logbook_{start_date}_to_{end_date}.pdf'
            }
        )
    except Exception as e:
        print("Error exporting PDF:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/add_userlogin', methods=['GET', 'POST'])
def add_userlogin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Validasi input
        if not username or not password:
            return jsonify({"error": "Username dan Password tidak boleh kosong."}), 400

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            query = "INSERT INTO userlogin (username, password) VALUES (%s, %s)"
            cursor.execute(query, (username, password))
            connection.commit()
            connection.close()
            return jsonify({"success": True}), 200
        except Exception as e:
            print("Error adding user login:", e)
            return jsonify({"error": str(e)}), 500

    return render_template('add_userlogin.html')

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

if __name__ == '__main__':
    app.run(debug=True)
