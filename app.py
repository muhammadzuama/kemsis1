from flask import Flask, render_template, request, send_from_directory, redirect, flash
import os
import psycopg2

app = Flask(__name__)

# Mendapatkan direktori proyek
base_dir = os.path.dirname(os.path.abspath(__file__))

# Mengatur direktori penyimpanan gambar
app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, 'uploads')

# Detail database
db_details = {
    'database': 'kemsis',
    'user': 'postgres',
    'password': '1905',
    'host': 'localhost',
}
# Set secret key
app.secret_key = 'kunci_rahasia_anda'

def encrypt_password(password):
    shift = 5  # Jumlah pergeseran karakter
    encrypted_password = ''
    for char in password:
        if char.isalpha():
            ascii_offset = 65 if char.isupper() else 97
            encrypted_char = chr((ord(char) - ascii_offset + shift) % 26 + ascii_offset)
            encrypted_password += encrypted_char
        elif char.isdigit():
            encrypted_char = str((int(char) + shift) % 10)
            encrypted_password += encrypted_char
        else:
            encrypted_password += char

    return encrypted_password


def decrypt_password(encrypted_password):
    shift = 5  # Jumlah pergeseran karakter
    decrypted_password = ''
    for char in encrypted_password:
        if char.isalpha():
            ascii_offset = 65 if char.isupper() else 97
            decrypted_char = chr((ord(char) - ascii_offset - shift) % 26 + ascii_offset)
            decrypted_password += decrypted_char
        elif char.isdigit():
            decrypted_char = str((int(char) - shift) % 10)
            decrypted_password += decrypted_char
        else:
            decrypted_password += char

    return decrypted_password


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        encrypted_password = encrypt_password(password)
        conn = psycopg2.connect(**db_details)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, encrypted_password))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/login')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = psycopg2.connect(**db_details)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            stored_password = result[2]  # Menggunakan indeks 2 untuk kolom password
            decrypted_password = decrypt_password(stored_password)
            if password == decrypted_password:
                return redirect('/view')

        # Tambahkan pesan flash untuk login gagal
        flash('Username atau password salah.', 'error')
        return redirect('/login')

    return render_template('login.html')


# Sisa kode aplikasi Flask...
def create_upload_folder():
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)


def encrypt_caption(caption):
    # Daftar kata-kata kasar
    bad_words = {
        'anjing': 'sabar',
        'jancok': 'astagfirullah',
        'bangsat': 'stay hallal brother',
        'kata kotor': 'kata bersih',
        'meso': 'alhamdullilah'
    }

    # Enkripsi caption dengan mengganti kata-kata kasar
    encrypted_caption = caption
    for word, replacement in bad_words.items():
        encrypted_caption = encrypted_caption.replace(word, replacement)

    return encrypted_caption


def insert_image(caption, filename, filepath):
    encrypted_caption = encrypt_caption(caption)

    conn = psycopg2.connect(**db_details)
    cursor = conn.cursor()

    query = "INSERT INTO images1 (caption, filename, filepath) VALUES (%s, %s, %s)"
    cursor.execute(query, (encrypted_caption, filename, filepath))

    conn.commit()
    cursor.close()
    conn.close()


def get_images():
    conn = psycopg2.connect(**db_details)
    cursor = conn.cursor()

    query = "SELECT id, caption, filename, filepath FROM images1 ORDER BY id DESC"
    cursor.execute(query)
    images = cursor.fetchall()

    cursor.close()
    conn.close()

    return images


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/up', methods=['GET', 'POST'])
def up():
    if request.method == 'POST':
        file = request.files['file']
        caption = request.form['caption']

        if file and caption:
            create_upload_folder()
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            insert_image(caption, filename, file_path)

            return redirect('/view')

    return render_template('upload.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/view')
def view():
    images = get_images()
    return render_template('view.html', images=images)


if __name__ == '__main__':
    app.run(debug=True)
