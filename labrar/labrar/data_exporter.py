import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any

class DataExporter:
    @staticmethod
    def serialize_datetime(obj: Any) -> Any:
        """Convert datetime objects to string format for JSON serialization."""
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return obj

    @staticmethod
    def prepare_books_data(books: Dict) -> list:
        """Prepare books data for export."""
        books_data = []
        for book in books.values():
            books_data.append({
                'Book ID': book.book_id,
                'Title': book.title,
                'Author': book.author,
                'ISBN': book.isbn,
                'Total Copies': book.total_copies,
                'Available Copies': book.copies_available
            })
        return books_data

    @staticmethod
    def prepare_users_data(users: Dict) -> list:
        """Prepare users data for export."""
        users_data = []
        for user in users.values():
            users_data.append({
                'User ID': user.user_id,
                'Name': user.name,
                'Email': user.email,
                'Role': user.role,
                'Books Borrowed': len(user.borrowed_books)
            })
        return users_data

    @staticmethod
    def prepare_transactions_data(transactions: Dict) -> list:
        """Prepare transactions data for export."""
        transactions_data = []
        for txn in transactions.values():
            transactions_data.append({
                'Transaction ID': txn.transaction_id,
                'User ID': txn.user_id,
                'Book ID': txn.book_id,
                'Borrow Date': txn.borrow_date,
                'Due Date': txn.due_date,
                'Return Date': txn.return_date,
                'Status': txn.status,
                'Fine Amount': txn.fine_amount
            })
        return transactions_data

    @staticmethod
    def export_to_excel(library, filename: str = "library_data.xlsx") -> str:
        """
        Export library data to Excel file with multiple sheets.
        Returns the path to the saved file.
        """
        # Prepare data for each sheet
        books_data = DataExporter.prepare_books_data(library.books)
        users_data = DataExporter.prepare_users_data(library.users)
        transactions_data = DataExporter.prepare_transactions_data(library.transactions)

        # Convert to DataFrames
        books_df = pd.DataFrame(books_data)
        users_df = pd.DataFrame(users_data)
        transactions_df = pd.DataFrame(transactions_data)

        # Create Excel writer object
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Write each DataFrame to a different sheet
            books_df.to_excel(writer, sheet_name='Books', index=False)
            users_df.to_excel(writer, sheet_name='Users', index=False)
            transactions_df.to_excel(writer, sheet_name='Transactions', index=False)

        return filename

    @staticmethod
    def export_to_json(library, filename: str = "library_data.json") -> str:
        """
        Export library data to JSON file.
        Returns the path to the saved file.
        """
        data = {
            'books': DataExporter.prepare_books_data(library.books),
            'users': DataExporter.prepare_users_data(library.users),
            'transactions': DataExporter.prepare_transactions_data(library.transactions)
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, default=DataExporter.serialize_datetime, indent=4)

        return filename