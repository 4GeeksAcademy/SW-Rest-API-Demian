import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    serialized = [user.serialize() for user in users]
    return jsonify(serialized), 200


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.serialize()), 200


@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    favorites = Favorite.query.filter_by(user_id=user_id).all()
    return jsonify([fav.serialize() for fav in favorites]), 200


@app.route('/people', methods=['GET'])
def get_people():
    people_list = People.query.all()
    serialized_people = [person.serialize() for person in people_list]
    return jsonify(serialized_people), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get(people_id)
    if person is None:
        return jsonify({"error": "Person not found"}), 404
    return jsonify(person.serialize()), 200


@app.route('/people', methods=['POST'])
def create_person():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('description') or not data.get('image_url'):
        return jsonify({"error": "Missing required fields"}), 400

    new_person = People(
        name=data['name'],
        description=data['description'],
        image_url=data['image_url'],
    )
    db.session.add(new_person)
    db.session.commit()
    return jsonify(new_person.serialize()), 201


@app.route('/people/<int:id>', methods=['PUT'])
def update_person(id):
    person = People.query.get(id)
    if not person:
        return jsonify({"error": "Person not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON data"}), 400

    if 'name' in data:
        person.name = data['name']
    if 'description' in data:
        person.description = data['description']
    if 'image_url' in data:
        person.image_url = data['image_url']

    db.session.commit()
    return jsonify(person.serialize()), 200


@app.route('/people/<int:id>', methods=['DELETE'])
def delete_person(id):
    person = People.query.get(id)
    if not person:
        return jsonify({"error": "Person not found"}), 404

    db.session.delete(person)
    db.session.commit()
    return jsonify({"message": "Person deleted"}), 200


@app.route('/planets', methods=['GET'])
def get_planets():
    planets_list = Planets.query.all()
    serialized_planets = [planet.serialize() for planet in planets_list]
    return jsonify(serialized_planets), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planets.query.get(planet_id)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200


@app.route('/planets', methods=['POST'])
def create_planet():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('description'):
        return jsonify({"error": "Missing required fields"}), 400

    new_planet = Planets(
        name=data['name'],
        description=data['description'],
        image_url=data.get('image_url')
    )
    db.session.add(new_planet)
    db.session.commit()
    return jsonify(new_planet.serialize()), 201


@app.route('/planets/<int:id>', methods=['PUT'])
def update_planet(id):
    planet = Planets.query.get(id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON data"}), 400

    if 'name' in data:
        planet.name = data['name']
    if 'description' in data:
        planet.description = data['description']
    if 'image_url' in data:
        planet.image_url = data['image_url']

    db.session.commit()
    return jsonify(planet.serialize()), 200


@app.route('/planets/<int:id>', methods=['DELETE'])
def delete_planet(id):
    planet = Planets.query.get(id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    db.session.delete(planet)
    db.session.commit()
    return jsonify({"message": "Planet deleted"}), 200


@app.route('/users/<int:user_id>/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(user_id, planet_id):
    user = User.query.get(user_id)
    planet = Planets.query.get(planet_id)
    if not user or not planet:
        return jsonify({"error": "User or Planet not found"}), 404

    existing_fav = Favorite.query.filter_by(
        user_id=user_id, planet_id=planet_id).first()
    if existing_fav:
        return jsonify({"message": "Favorite planet already added"}), 400

    new_fav = Favorite(user_id=user_id, planet_id=planet_id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify(new_fav.serialize()), 201


@app.route('/users/<int:user_id>/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(user_id, people_id):
    user = User.query.get(user_id)
    person = People.query.get(people_id)
    if not user or not person:
        return jsonify({"error": "User or Person not found"}), 404

    existing_fav = Favorite.query.filter_by(
        user_id=user_id, people_id=people_id).first()
    if existing_fav:
        return jsonify({"message": "Favorite person already added"}), 400

    new_fav = Favorite(user_id=user_id, people_id=people_id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify(new_fav.serialize()), 201


@app.route('/users/<int:user_id>/favorite/planet/<int:planet_id>', methods=['DELETE'])
def remove_favorite_planet(user_id, planet_id):
    fav = Favorite.query.filter_by(
        user_id=user_id, planet_id=planet_id).first()
    if not fav:
        return jsonify({"error": "Favorite planet not found"}), 404

    db.session.delete(fav)
    db.session.commit()
    return jsonify({"message": "Favorite planet removed"}), 200


@app.route('/users/<int:user_id>/favorite/people/<int:people_id>', methods=['DELETE'])
def remove_favorite_people(user_id, people_id):
    fav = Favorite.query.filter_by(
        user_id=user_id, people_id=people_id).first()
    if not fav:
        return jsonify({"error": "Favorite person not found"}), 404

    db.session.delete(fav)
    db.session.commit()
    return jsonify({"message": "Favorite person removed"}), 200


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
