from flask import Flask, render_template, request, jsonify
import psycopg2

app = Flask(__name__)

# Database connection function
def get_db_connection():
    conn = psycopg2.connect(
        dbname="412BookApp", user="postgres", password="raveena123", host="localhost", port="8080"
    )
    return conn

# Home page
@app.route("/")
def index():
    return render_template("index.html")

# Search by Author page (form)
@app.route("/searchAuthorPage")
def search_author_page():
    return render_template("author_search.html")

# Search by Title page (form)
@app.route("/searchTitlePage")
def search_title_page():
    return render_template("title_search.html")

# Search by ISBN page (form)
@app.route("/searchISBNPage")
def search_isbn_page():
    return render_template("isbn_search.html")

# Show Library page (form)
@app.route("/showLibraryPage")
def show_library_page():
    return render_template("library_view.html")

@app.route("/addReviewPage")
def show_review_page():
    return render_template("rate_book.html")

@app.route("/searchByAuthor", methods=["GET"])
def searchByAuthor():
    search_results = []
    if request.method == "GET":
        keyword = request.args.get("keyword") 

        search_pattern = f"%{keyword}%"
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM books
            WHERE b_authors ILIKE %s
        """, (search_pattern,))

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
            return jsonify({"error": "Sorry! No books found. Please try again!"}), 404
    
        for row in rows:
            search_results.append({
                "book_id": row[0],
                "title": row[1],
                "authors": row[2],
                "rating": row[3],
                "isbn" : row[4]
        })
        
        return render_template("author_search.html", search_results=search_results)


@app.route("/searchByTitle", methods=["GET"])
def searchByTitle():
    search_results = []
    if request.method == "GET":
        keyword = request.args.get("keyword") 

        search_pattern = f"%{keyword}%"
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM books
            WHERE b_title ILIKE %s
        """, (search_pattern,))

        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    
        if not rows:
            return jsonify({"error": "Sorry! No books found. Please try again!"}), 404

        for row in rows:
            search_results.append({
                "book_id": row[0],
                "title": row[1],
                "authors": row[2],
                "rating": row[3],
                "isbn" : row[4]

        })
    return render_template("title_search.html", search_results=search_results)

@app.route("/searchByISBN", methods=["GET"])
def searchByISBN():
    search_results = []
    if request.method == "GET":
        keyword = request.args.get("keyword") 

        search_pattern = f"%{keyword}%"
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM books
            WHERE b_isbn ILIKE %s
        """, (search_pattern,))

        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    
        if not rows:
            return jsonify({"error": "Sorry! No books found. Please try again!"}), 404

        for row in rows:
            search_results.append({
                "book_id": row[0],
                "title": row[1],
                "authors": row[2],
                "rating": row[3],
                "isbn" : row[4]

        })
    return render_template("isbn_search.html", search_results=search_results)

@app.route("/showLibrary", methods=["GET"])
def showLibrary():
    search_results = []
    if request.method == "GET":
        user_id = request.args.get("user_id") 

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT UB.UB_USERKEY, B.B_ISBN, UB.UB_RATING, B.B_TITLE, B.B_AUTHORS
            FROM USER_BOOKS UB
            JOIN BOOKS B ON UB.UB_BOOKID = B.B_BOOKID
            WHERE UB.UB_USERKEY = %s
        """, (user_id,))

        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    
        if not rows:
            return render_template("library_view.html", error="Sorry! No reviews found. Please try again!")

        for row in rows:
            search_results.append({
                "user_id": row[0],
                "isbn": row[1],
                "your_rating": row[2],
                "title": row[3],
                "authors": row[4]
            })
    
    return render_template("library_view.html", search_results=search_results)


@app.route("/addReview", methods=["POST"])
def addReview():
    user_id = request.form.get("user_id")
    isbn = request.form.get("isbn")
    rating = request.form.get("rating")
    
    # Basic validation
    if not all([user_id, isbn, rating]):
        return render_template("rate_book.html", error="Missing user ID, ISBN, or rating.")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO USER_BOOKS (UB_USERKEY, UB_BOOKID, UB_RATING)
        SELECT %s, B_BOOKID, %s
        FROM BOOKS
        WHERE B_ISBN = %s
    """, (user_id, rating, isbn))


        conn.commit()  

    except Exception as e:
        conn.rollback()
        return render_template("rate_book.html", error=f"Database error: {str(e)}")

    finally:
        cursor.close()
        conn.close()

    return render_template("rate_book.html", message="Rating added successfully!")


if __name__ == "__main__":
    app.run(debug=True)
