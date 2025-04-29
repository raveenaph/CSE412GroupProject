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
#@app.route("/searchISBNPage")
#def search_isbn_page():
 #   return render_template("search_by_isbn.html")

# Show Library page (form)
@app.route("/showLibraryPage")
def show_library_page():
    return render_template("library_view.html")

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
    return render_template("search_by_isbn.html", search_results=search_results)

@app.route("/showLibrary", methods=["GET"])
def showLibrary():
    search_results = []
    if request.method == "GET":
        user_id = request.args.get("user_id") 

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM user_books
            JOIN books ON ub_bookid = b_bookid
            WHERE ub_userkey = %s
        """, (user_id,))

        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    
        if not rows:
            return jsonify({"error": "Sorry! No reviews found. Please try again!"}), 404

        for row in rows:
            search_results.append({
                "book_id": row[1],
                "your rating": row[2],
                "title": row[4],
                "authors": row[5],
                "isbn": row[7]
        })
    return render_template("library_view.html", search_results=search_results)

@app.route("/addReview", methods=["POST"])
def addReview():
    data = request.get_json()

    # Extract required fields
    user_id = data.get("user_id")
    book_id = data.get("book_id")
    rating = data.get("rating")

    # Basic validation
    if not all([user_id, book_id, rating]):
        return jsonify({"error": "Missing user_id, book_id, or rating"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO USER_BOOKS (UB_USERKEY, UB_BOOKID, UB_RATING)
            VALUES (%s, %s, %s)
        """, (user_id, book_id, rating))

        conn.commit()  

    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": "Rating added successfully!"}), 201


if __name__ == "__main__":
    app.run(debug=True)
