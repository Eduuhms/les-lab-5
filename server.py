"""
Flask server exposing the same data via:
  - REST API  : GET /api/books, GET /api/books/<id>
  - GraphQL   : POST /graphql
  - Health    : GET /health
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request
import graphene
from data import generate_books

app = Flask(__name__)
BOOKS = generate_books()

# ── REST ──────────────────────────────────────────────────────────────────────

@app.route("/health")
def health():
    return jsonify({"status": "ok", "books": len(BOOKS)})


@app.route("/api/books", methods=["GET"])
def get_books():
    limit = request.args.get("limit", 10, type=int)
    offset = request.args.get("offset", 0, type=int)
    return jsonify(BOOKS[offset: offset + limit])


@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = next((b for b in BOOKS if b["id"] == book_id), None)
    if book:
        return jsonify(book)
    return jsonify({"error": "Not found"}), 404


# ── GraphQL Schema ────────────────────────────────────────────────────────────

class BookType(graphene.ObjectType):
    id = graphene.Int()
    title = graphene.String()
    author_name = graphene.String()
    author_bio = graphene.String()
    author_nationality = graphene.String()
    year_published = graphene.Int()
    genre = graphene.String()
    description = graphene.String()
    rating = graphene.Float()
    pages = graphene.Int()
    publisher = graphene.String()
    isbn = graphene.String()
    language = graphene.String()
    series_name = graphene.String()
    series_number = graphene.Int()
    awards = graphene.List(graphene.String)
    keywords = graphene.List(graphene.String)
    cover_url = graphene.String()
    price = graphene.Float()
    stock_count = graphene.Int()


def _to_book_type(b: dict) -> BookType:
    return BookType(
        id=b["id"],
        title=b["title"],
        author_name=b["author_name"],
        author_bio=b["author_bio"],
        author_nationality=b["author_nationality"],
        year_published=b["year_published"],
        genre=b["genre"],
        description=b["description"],
        rating=b["rating"],
        pages=b["pages"],
        publisher=b["publisher"],
        isbn=b["isbn"],
        language=b["language"],
        series_name=b["series_name"],
        series_number=b["series_number"],
        awards=b["awards"],
        keywords=b["keywords"],
        cover_url=b["cover_url"],
        price=b["price"],
        stock_count=b["stock_count"],
    )


class RootQuery(graphene.ObjectType):
    book = graphene.Field(BookType, id=graphene.Int(required=True))
    books = graphene.List(
        BookType,
        limit=graphene.Int(default_value=10),
        offset=graphene.Int(default_value=0),
    )

    def resolve_book(self, info, id):
        b = next((book for book in BOOKS if book["id"] == id), None)
        return _to_book_type(b) if b else None

    def resolve_books(self, info, limit=10, offset=0):
        return [_to_book_type(b) for b in BOOKS[offset: offset + limit]]


schema = graphene.Schema(query=RootQuery, auto_camelcase=False)


@app.route("/graphql", methods=["POST"])
def graphql_endpoint():
    data = request.get_json(force=True)
    if not data or "query" not in data:
        return jsonify({"error": "No query provided"}), 400
    result = schema.execute(data["query"])
    if result.errors:
        return jsonify({"errors": [str(e) for e in result.errors]}), 400
    return jsonify({"data": result.data})


if __name__ == "__main__":
    print(f"[server] Loaded {len(BOOKS)} books.")
    print("[server] REST  -> http://127.0.0.1:5000/api/books")
    print("[server] GQL   -> http://127.0.0.1:5000/graphql  (POST)")
    app.run(host="127.0.0.1", debug=False, port=5000, threaded=True)
