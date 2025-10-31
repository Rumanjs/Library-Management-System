from datetime import datetime, timedelta
from typing import List, Optional, Dict
import uuid
from email.message import EmailMessage
import smtplib
import re

def validate_email(email: str) -> bool:
    """
    Validate email format.
    Returns True if email is valid, False otherwise.
    """
    # Regular expression for email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))

class EmailNotifier:
    """Handles email notifications for the library system."""
    @staticmethod
    def create_email(to_email: str, subject: str, content: str) -> EmailMessage:
        email = EmailMessage()
        email['From'] = "library@example.com"
        email['To'] = to_email
        email['Subject'] = subject
        email.set_content(content)
        return email
    
    @staticmethod
    def send_borrow_notification(user: 'User', book: 'Book', transaction: 'Transaction') -> None:
        subject = "Library Book Borrowed"
        content = f"""
Dear {user.name},

This email confirms that you have borrowed the following book:
Title: {book.title}
Author: {book.author}
ISBN: {book.isbn}

Transaction Details:
Transaction ID: {transaction.transaction_id}
Borrow Date: {transaction.borrow_date.strftime('%Y-%m-%d')}
Due Date: {transaction.due_date.strftime('%Y-%m-%d')}

Please return the book by the due date to avoid any fines.

Best regards,
Library Management System
"""
        email = EmailNotifier.create_email(user.email, subject, content)
        # For demonstration, just print the email
        print("\nEmail Notification Preview:")
        print(f"To: {email['To']}")
        print(f"Subject: {email['Subject']}")
        print(content)

    @staticmethod
    def send_return_notification(user: 'User', book: 'Book', transaction: 'Transaction', fine: float = 0.0) -> None:
        subject = "Library Book Returned"
        content = f"""
Dear {user.name},

This email confirms that you have returned the following book:
Title: {book.title}
Author: {book.author}
ISBN: {book.isbn}

Transaction Details:
Transaction ID: {transaction.transaction_id}
Return Date: {transaction.return_date.strftime('%Y-%m-%d')}
"""
        if fine > 0:
            content += f"\nPlease note that a fine of ₹{fine:.2f} has been applied due to late return."
        
        content += "\nThank you for using our library services.\n\nBest regards,\nLibrary Management System"
        
        email = EmailNotifier.create_email(user.email, subject, content)
        # For demonstration, just print the email
        print("\nEmail Notification Preview:")
        print(f"To: {email['To']}")
        print(f"Subject: {email['Subject']}")
        print(content)

# ============================================
# BASE CLASSES
# ============================================

class Book:
    """Represents a book in the library system."""
    def __init__(self, book_id: str, title: str, author: str, isbn: str, total_copies: int):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.total_copies = total_copies
        self.copies_available = total_copies
    
    def borrow_book(self) -> bool:
        if self.copies_available > 0:
            self.copies_available -= 1
            return True
        return False
    
    def return_book(self) -> bool:
        if self.copies_available < self.total_copies:
            self.copies_available += 1
            return True
        return False
    
    def is_available(self) -> bool:
        return self.copies_available > 0
    
    def __str__(self):
        return f"[{self.book_id}] {self.title} by {self.author} | ISBN: {self.isbn} | Available: {self.copies_available}/{self.total_copies}"


class Transaction:
    """Represents a borrow/return transaction."""
    def __init__(self, user_id: str, book_id: str, borrow_date: datetime):
        self.transaction_id = str(uuid.uuid4())[:8]
        self.user_id = user_id
        self.book_id = book_id
        self.borrow_date = borrow_date
        self.due_date = borrow_date + timedelta(days=14)
        self.return_date: Optional[datetime] = None
        self.fine_amount: float = 0.0
        self.status = "Borrowed"
    
    def complete_return(self, return_date: datetime, fine_per_day: float = 5.0) -> float:
        self.return_date = return_date
        self.status = "Returned"
        
        if return_date > self.due_date:
            days_late = (return_date - self.due_date).days
            self.fine_amount = days_late * fine_per_day
        
        return self.fine_amount
    
    def __str__(self):
        fine_info = f" | Fine: ₹{self.fine_amount}" if self.fine_amount > 0 else ""
        return_info = f" | Returned: {self.return_date.strftime('%Y-%m-%d')}" if self.return_date else ""
        return f"[{self.transaction_id}] Book: {self.book_id} | Borrowed: {self.borrow_date.strftime('%Y-%m-%d')} | Due: {self.due_date.strftime('%Y-%m-%d')} | Status: {self.status}{return_info}{fine_info}"


class User:
    """Base user class."""
    def __init__(self, user_id: str, name: str, email: str, role: str):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.role = role
        self.borrowed_books: List[str] = []
    
    def can_borrow(self) -> bool:
        raise NotImplementedError
    
    def is_fine_applicable(self) -> bool:
        raise NotImplementedError
    
    def add_borrowed_book(self, book_id: str):
        self.borrowed_books.append(book_id)
    
    def remove_borrowed_book(self, book_id: str):
        if book_id in self.borrowed_books:
            self.borrowed_books.remove(book_id)
    
    def __str__(self):
        return f"[{self.user_id}] {self.name} ({self.role}) | Email: {self.email} | Borrowed: {len(self.borrowed_books)} books"


class Student(User):
    MAX_BORROW_LIMIT = 3
    def __init__(self, user_id: str, name: str, email: str):
        super().__init__(user_id, name, email, "Student")
    
    def can_borrow(self) -> bool:
        return len(self.borrowed_books) < self.MAX_BORROW_LIMIT
    
    def is_fine_applicable(self) -> bool:
        return True


class Faculty(User):
    def __init__(self, user_id: str, name: str, email: str):
        super().__init__(user_id, name, email, "Faculty")
    
    def can_borrow(self) -> bool:
        return True
    
    def is_fine_applicable(self) -> bool:
        return False


class Admin(User):
    def __init__(self, user_id: str, name: str, email: str):
        super().__init__(user_id, name, email, "Admin")
    
    def can_borrow(self) -> bool:
        return True
    
    def is_fine_applicable(self) -> bool:
        return False


# ============================================
# LIBRARY MANAGEMENT SYSTEM
# ============================================

class Library:
    def __init__(self):
        self.books: Dict[str, Book] = {}
        self.users: Dict[str, User] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.active_borrows: Dict[str, List[Transaction]] = {}
    
    # USER REGISTRATION
    def register_user(self, user_id: str, name: str, email: str, role: str) -> bool:
        if not user_id.isdigit() or int(user_id) <= 0:
            print("❌ Error: User ID must be a positive integer.")
            return False
        
        if user_id in self.users:
            print(f"❌ Error: User ID '{user_id}' already exists.")
            return False
        
        if role.lower() == "admin":
            print("❌ Error: Only the predefined admin (Ruman) can exist.")
            return False
            
        if not validate_email(email):
            print("❌ Error: Invalid email format. Email should be in the format: username@domain.com")
            return False

        if role.lower() == "student":
            user = Student(user_id, name, email)
        elif role.lower() == "faculty":
            user = Faculty(user_id, name, email)
        else:
            print(f"❌ Invalid role '{role}'. Choose Student or Faculty.")
            return False

        self.users[user_id] = user
        self.active_borrows[user_id] = []
        print(f"✅ User registered successfully: {user}")
        return True
    
    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)
    
    # BOOK MANAGEMENT
    def add_book(self, book_id: str, title: str, author: str, isbn: str, total_copies: int) -> bool:
        if book_id in self.books:
            print(f"❌ Error: Book ID '{book_id}' already exists.")
            return False
        book = Book(book_id, title, author, isbn, total_copies)
        self.books[book_id] = book
        print(f"✅ Book added successfully: {book}")
        return True
    
    def view_all_books(self):
        if not self.books:
            print("📚 No books in the library.")
            return
        print("\n📚 LIBRARY BOOK INVENTORY")
        print("="*80)
        for book in self.books.values():
            print(book)
        print("="*80 + "\n")
    
    def search_books(self, search_term: str, search_by: str = "title"):
        results = []
        search_term = search_term.lower()
        for book in self.books.values():
            if search_by == "title" and search_term in book.title.lower():
                results.append(book)
            elif search_by == "author" and search_term in book.author.lower():
                results.append(book)
            elif search_by == "isbn" and search_term in book.isbn.lower():
                results.append(book)
        if results:
            print(f"\n🔍 Search Results ({len(results)} found):")
            for book in results:
                print(book)
        else:
            print(f"❌ No books found for '{search_term}'")
    
    def update_book(self, book_id: str, title: Optional[str] = None, author: Optional[str] = None, 
                  isbn: Optional[str] = None, total_copies: Optional[int] = None) -> bool:
        if book_id not in self.books:
            print(f"❌ Book ID '{book_id}' not found.")
            return False
        book = self.books[book_id]
        if title is not None: book.title = title
        if author is not None: book.author = author
        if isbn is not None: book.isbn = isbn
        if total_copies is not None:
            if total_copies <= 0:
                print("❌ Invalid number of copies.")
                return False
            diff = total_copies - book.total_copies
            book.total_copies = total_copies
            book.copies_available += diff
        print(f"✅ Book updated successfully: {book}")
        return True
    
    def delete_book(self, book_id: str):
        if book_id not in self.books:
            print(f"❌ Book ID '{book_id}' not found.")
            return False
        for txns in self.active_borrows.values():
            for txn in txns:
                if txn.book_id == book_id and txn.status == "Borrowed":
                    print("❌ Cannot delete book — it’s currently borrowed.")
                    return False
        del self.books[book_id]
        print(f"✅ Book '{book_id}' deleted successfully.")
        return True
    
    # BORROW & RETURN
    def borrow_book(self, user_id: str, book_id: str):
        user = self.get_user(user_id)
        if not user:
            print(f"❌ User ID '{user_id}' not found.")
            return False
        book = self.books.get(book_id)
        if not book:
            print(f"❌ Book ID '{book_id}' not found.")
            return False
        if not book.is_available():
            print(f"❌ Book '{book.title}' is unavailable.")
            return False
        if not user.can_borrow():
            print(f"❌ {user.name} reached borrow limit.")
            return False
        
        txn = Transaction(user_id, book_id, datetime.now())
        book.borrow_book()
        user.add_borrowed_book(book_id)
        self.transactions[txn.transaction_id] = txn
        self.active_borrows[user_id].append(txn)
        
        # Send borrow notification email
        EmailNotifier.send_borrow_notification(user, book, txn)
        
        print(f"✅ Book borrowed successfully: {book.title}")
        print(f"   Transaction ID: {txn.transaction_id}")
        print(f"   Due Date: {txn.due_date.strftime('%Y-%m-%d')}")
        return True
    
    def return_book(self, user_id: str, book_id: str):
        user = self.get_user(user_id)
        if not user:
            print(f"❌ User ID '{user_id}' not found.")
            return False
        active_txn = None
        for txn in self.active_borrows[user_id]:
            if txn.book_id == book_id and txn.status == "Borrowed":
                active_txn = txn
                break
        if not active_txn:
            print(f"❌ No active borrow found for book '{book_id}'")
            return False
        
        book = self.books[book_id]
        return_date = datetime.now()
        fine = 0.0
        if user.is_fine_applicable():
            fine = active_txn.complete_return(return_date, 5.0)
        else:
            active_txn.complete_return(return_date, 0.0)
        
        book.return_book()
        user.remove_borrowed_book(book_id)
        
        # Send return notification email
        EmailNotifier.send_return_notification(user, book, active_txn, fine)
        
        print(f"✅ Book returned successfully: {book.title}")
        if fine > 0:
            print(f"⚠️  Fine: ₹{fine}")
        else:
            print("✅ Returned on time, no fine.")
        return True
    
    # VIEW TRANSACTIONS
    def view_all_transactions(self, user_id: Optional[str] = None):
        txns = list(self.transactions.values()) if user_id is None else [
            txn for txn in self.transactions.values() if txn.user_id == user_id
        ]
        if not txns:
            print("📋 No transactions found.")
            return
        print("\n📋 TRANSACTION HISTORY")
        print("="*90)
        for txn in txns:
            print(txn)
        print("="*90)


# ============================================
# MAIN PROGRAM
# ============================================

def display_menu():
    print("\n" + "="*60)
    print("📚 LIBRARY MANAGEMENT SYSTEM")
    print("="*60)
    print("1. Register User")
    print("2. Add Book (Admin only)")
    print("3. View All Books")
    print("4. Search Books")
    print("5. Update Book (Admin only)")
    print("6. Delete Book (Admin only)")
    print("7. Borrow Book")
    print("8. Return Book")
    print("9. View Transactions")
    print("0. Exit")
    print("="*60)


def main():
    library = Library()

    # Predefined Admin (YOU)
    admin = Admin("1", "Ruman", "ruman@library.com")
    library.users["1"] = admin
    library.active_borrows["1"] = []
    print("✅ Admin (Ruman) initialized successfully!")

    # Sample books
    library.add_book("101", "Python Programming", "John Doe", "978-0-123456-78-9", 5)
    library.add_book("102", "Data Structures", "Jane Smith", "978-0-987654-32-1", 3)

    while True:
        display_menu()
        choice = input("Enter your choice (0-9): ").strip()
        
        if choice == "0":
            print("👋 Exiting Library System. Goodbye!")
            break
        
        elif choice == "1":
            print("\n--- Register User ---")
            user_id = input("User ID (positive integer): ").strip()
            name = input("Name: ").strip()
            email = input("Email (e.g., username@domain.com): ").strip()
            while not validate_email(email):
                print("❌ Invalid email format! Email should be in the format: username@domain.com")
                email = input("Email (e.g., username@domain.com): ").strip()
            role = input("Role (Student/Faculty): ").strip()
            library.register_user(user_id, name, email, role)
        
        elif choice == "2":
            print("\n--- Add Book ---")
            book_id = input("Book ID (integer): ").strip()
            if not book_id.isdigit() or int(book_id) <= 0:
                print("❌ Invalid Book ID.")
                continue
            title = input("Title: ").strip()
            author = input("Author: ").strip()
            isbn = input("ISBN: ").strip()
            copies = input("Total Copies: ").strip()
            if not copies.isdigit() or int(copies) <= 0:
                print("❌ Copies must be a positive number.")
                continue
            library.add_book(book_id, title, author, isbn, int(copies))
        
        elif choice == "3":
            library.view_all_books()
        
        elif choice == "4":
            term = input("Search term: ").strip()
            library.search_books(term)
        
        elif choice == "5":
            book_id = input("Book ID to update: ").strip()
            title = input("New Title (blank=skip): ").strip() or None
            author = input("New Author (blank=skip): ").strip() or None
            isbn = input("New ISBN (blank=skip): ").strip() or None
            copies = input("New Total Copies (blank=skip): ").strip()
            total_copies = int(copies) if copies.isdigit() and int(copies) > 0 else None
            library.update_book(book_id, title, author, isbn, total_copies)
        
        elif choice == "6":
            book_id = input("Book ID to delete: ").strip()
            library.delete_book(book_id)
        
        elif choice == "7":
            user_id = input("User ID (integer): ").strip()
            book_id = input("Book ID (integer): ").strip()
            if not (user_id.isdigit() and book_id.isdigit()):
                print("❌ IDs must be positive integers.")
                continue
            library.borrow_book(user_id, book_id)
        
        elif choice == "8":
            user_id = input("User ID (integer): ").strip()
            book_id = input("Book ID (integer): ").strip()
            if not (user_id.isdigit() and book_id.isdigit()):
                print("❌ IDs must be positive integers.")
                continue
            library.return_book(user_id, book_id)
        
        elif choice == "9":
            uid = input("Enter User ID (or blank for all): ").strip()
            if uid == "":
                library.view_all_transactions()
            else:
                library.view_all_transactions(uid)
        
        else:
            print("❌ Invalid choice.")


if __name__ == "__main__":
    main()