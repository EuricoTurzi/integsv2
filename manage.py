from flask import Flask
from app import db, User

app = Flask(__name__)

@app.cli.command("promote_to_admin")
def promote_to_admin():
    email = input("Enter the email of the user to promote: ")
    user = User.query.filter_by(email=email).first()
    if user is None:
        print(f'No user found with email {email}')
    else:
        user.access_level = 'Admin'
        db.session.commit()
        print(f'User {email} has been promoted to Admin')

if __name__ == "__main__":
    app.run()
