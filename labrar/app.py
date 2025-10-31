from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from lab import Library, Book, Student, Faculty, Admin, validate_email
from datetime import datetime
from data_exporter import DataExporter
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Required for flash messages

# Initialize library system
library = Library()

# Initialize admin
admin = Admin("1", "Ruman", "ruman@library.com")
library.users["1"] = admin
library.active_borrows["1"] = []

# Add sample books
library.add_book("101", "Python Programming", "John Doe", "978-0-123456-78-9", 5)
library.add_book("102", "Data Structures", "Jane Smith", "978-0-987654-32-1", 3)

@app.route('/')
def index():
    stats = {
        'total_books': len(library.books),
        'available_books': sum(book.copies_available for book in library.books.values()),
        'total_users': len(library.users),
        'active_borrows': sum(len(txns) for txns in library.active_borrows.values())
    }
    return render_template('index.html', stats=stats)

@app.route('/books')
def books():
    search = request.args.get('search', '').lower()
    if search:
        books_list = [book for book in library.books.values()
                     if search in book.title.lower() or
                     search in book.author.lower() or
                     search in book.isbn.lower()]
    else:
        books_list = list(library.books.values())
    return render_template('books.html', books=books_list)

@app.route('/add-book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        book_id = request.form['book_id']
        if library.add_book(
            book_id,
            request.form['title'],
            request.form['author'],
            request.form['isbn'],
            int(request.form['total_copies'])
        ):
            flash('Book added successfully!', 'success')
            return redirect(url_for('books'))
        flash('Failed to add book.', 'error')
    return render_template('book_form.html', book=None)

@app.route('/edit-book/<book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    book = library.books.get(book_id)
    if not book:
        flash('Book not found.', 'error')
        return redirect(url_for('books'))
    
    if request.method == 'POST':
        if library.update_book(
            book_id,
            request.form['title'],
            request.form['author'],
            request.form['isbn'],
            int(request.form['total_copies'])
        ):
            flash('Book updated successfully!', 'success')
            return redirect(url_for('books'))
        flash('Failed to update book.', 'error')
    
    return render_template('book_form.html', book=book)

@app.route('/delete-book/<book_id>', methods=['POST'])
def delete_book(book_id):
    if library.delete_book(book_id):
        flash('Book deleted successfully!', 'success')
    else:
        flash('Failed to delete book.', 'error')
    return redirect(url_for('books'))

@app.route('/users', methods=['GET'])
def users():
    return render_template('users.html', users=library.users.values())

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form['user_id']
        name = request.form['name']
        email = request.form['email']
        role = request.form['role']
        
        if library.register_user(user_id, name, email, role):
            flash('User registered successfully!', 'success')
            return redirect(url_for('users'))
        flash('Failed to register user.', 'error')
    
    return render_template('users.html', users=library.users.values())

@app.route('/borrow', methods=['GET', 'POST'])
def borrow_book():
    if request.method == 'POST':
        user_id = request.form['user_id']
        book_id = request.form['book_id']
        
        if library.borrow_book(user_id, book_id):
            flash('Book borrowed successfully!', 'success')
            return redirect(url_for('transactions'))
        flash('Failed to borrow book.', 'error')
    
    available_books = [book for book in library.books.values() if book.is_available()]
    return render_template('borrow.html', available_books=available_books)

@app.route('/return', methods=['GET', 'POST'])
def return_book():
    if request.method == 'POST':
        user_id = request.form['user_id']
        book_id = request.form['book_id']
        
        if library.return_book(user_id, book_id):
            flash('Book returned successfully!', 'success')
            return redirect(url_for('transactions'))
        flash('Failed to return book.', 'error')
    
    active_transactions = []
    for user_txns in library.active_borrows.values():
        active_transactions.extend(txn for txn in user_txns if txn.status == "Borrowed")
    
    return render_template('return.html', 
                         active_transactions=active_transactions,
                         users=library.users,
                         books=library.books)

@app.route('/transactions')
def transactions():
    user_id = request.args.get('user_id')
    transactions_list = library.transactions.values()
    if user_id:
        transactions_list = [t for t in transactions_list if t.user_id == user_id]
    return render_template('transactions.html',
                         transactions=transactions_list,
                         users=library.users,
                         books=library.books)

@app.route('/export/excel')
def export_excel():
    try:
        filename = DataExporter.export_to_excel(library)
        return send_file(
            filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='library_data.xlsx'
        )
    except Exception as e:
        flash(f'Error exporting data: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/export/json')
def export_json():
    try:
        filename = DataExporter.export_to_json(library)
        return send_file(
            filename,
            mimetype='application/json',
            as_attachment=True,
            download_name='library_data.json'
        )
    except Exception as e:
        flash(f'Error exporting data: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)