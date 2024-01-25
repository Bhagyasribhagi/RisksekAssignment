from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Dummy in-memory database
libraries_db = {}
books_db = {}

class Book:
    def __init__(self, title, author, isbn):
        self.title = title
        self.author = author
        self.isbn = isbn

    def display_info(self):
        return f"Title: {self.title}, Author: {self.author}, ISBN: {self.isbn}"

class EBook(Book):
    def __init__(self, title, author, isbn, file_format):
        super().__init__(title, author, isbn)
        self.file_format = file_format

    def display_info(self):
        return super().display_info() + f", File Format: {self.file_format}"

class Library:
    def __init__(self):
        self.books = []

    def add_book(self, book):
        if not isinstance(book, Book):
            raise ValueError("Only instances of Book class can be added to the library.")
        self.books.append(book)

    def display_all_books(self):
        return [book.display_info() for book in self.books]

    def search_by_title(self, title):
        result = [book.display_info() for book in self.books if book.title.lower() == title.lower()]
        return result if result else "Book not found."

library = Library()

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html", books=library.display_all_books())

@app.route("/add_book", methods=["POST"])
def add_book():
    try:
        data = request.get_json()
        title = data["title"]
        author = data["author"]
        isbn = data["isbn"]
        file_format = data.get("file_format")

        if isbn in books_db:
            return jsonify({"error": "Book with the same ISBN already exists."}), 400

        if file_format:
            book = EBook(title, author, isbn, file_format)
        else:
            book = Book(title, author, isbn)

        library.add_book(book)
        books_db[isbn] = book.display_info()
        return jsonify({"message": "Book added successfully."}), 201
    except KeyError:
        return jsonify({"error": "Invalid input data."}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/list_books", methods=["GET"])
def list_books():
    return jsonify({"books": list(books_db.values())})

@app.route("/delete_book/<isbn>", methods=["DELETE"])
def delete_book(isbn):
    if isbn in books_db:
        del books_db[isbn]
        return jsonify({"message": "Book deleted successfully."})
    else:
        return jsonify({"error": "Book not found."}), 404

if __name__ == "__main__":
    app.run(debug=True)
