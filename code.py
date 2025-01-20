from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

# Initialize app
app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Contact Model
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)

    def __init__(self, name, email, phone):
        self.name = name
        self.email = email
        self.phone = phone

# Contact Schema
class ContactSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Contact

contact_schema = ContactSchema()
contacts_schema = ContactSchema(many=True)

# Routes

# Create a contact
@app.route('/contact', methods=['POST'])
def add_contact():
    name = request.json['name']
    email = request.json['email']
    phone = request.json['phone']

    new_contact = Contact(name, email, phone)

    try:
        db.session.add(new_contact)
        db.session.commit()
        return contact_schema.jsonify(new_contact)
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# Get all contacts
@app.route('/contacts', methods=['GET'])
def get_contacts():
    all_contacts = Contact.query.all()
    return contacts_schema.jsonify(all_contacts)

# Get a single contact
@app.route('/contact/<int:id>', methods=['GET'])
def get_contact(id):
    contact = Contact.query.get_or_404(id)
    return contact_schema.jsonify(contact)

# Update a contact
@app.route('/contact/<int:id>', methods=['PUT'])
def update_contact(id):
    contact = Contact.query.get_or_404(id)

    name = request.json.get('name', contact.name)
    email = request.json.get('email', contact.email)
    phone = request.json.get('phone', contact.phone)

    contact.name = name
    contact.email = email
    contact.phone = phone

    try:
        db.session.commit()
        return contact_schema.jsonify(contact)
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# Delete a contact
@app.route('/contact/<int:id>', methods=['DELETE'])
def delete_contact(id):
    contact = Contact.query.get_or_404(id)
    try:
        db.session.delete(contact)
        db.session.commit()
        return jsonify({"message": "Contact deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# Initialize the database
@app.before_first_request
def create_tables():
    db.create_all()

# Run Server
if __name__ == '__main__':
    app.run(debug=True)
