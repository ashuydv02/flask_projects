from blogs import app,db
from models import User,Post

def create_db():
    with app.app_context():
        post_1 = Post(title='First Blog', content='My First Blog Post...', user_id=1)
        db.session.add(post_1)
        post_2 = Post(title='Second Blog', content='My Second Blog Post...', user_id=1)
        db.session.add(post_2)
        db.session.commit()
        print(User.query.all()[0].posts)

if __name__ == '__main__':
    create_db()
