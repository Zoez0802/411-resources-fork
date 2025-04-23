import pytest
from app import create_app, db
from boxing.models.boxers_model import Boxers

@pytest.fixture
def app():
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # Use a test database
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

def test_add_boxer(app):
    """Test adding a new boxer to the database"""
    with app.app_context():
        boxer = Boxers(name="Muhammad Ali", weight=220, height=76, reach=80, age=35)
        db.session.add(boxer)
        db.session.commit()

        # Verify the boxer was added
        added_boxer = Boxers.query.filter_by(name="Muhammad Ali").first()
        assert added_boxer is not None
        assert added_boxer.name == "Muhammad Ali"
        assert added_boxer.weight == 220

def test_get_boxer_by_id(app):
    """Test retrieving a boxer by ID"""
    with app.app_context():
        boxer = Boxers(name="Mike Tyson", weight=240, height=75, reach=78, age=54)
        db.session.add(boxer)
        db.session.commit()
        
        added_boxer = Boxers.query.get(1)  # Assuming this is the ID of the first boxer
        assert added_boxer is not None
        assert added_boxer.name == "Mike Tyson"
