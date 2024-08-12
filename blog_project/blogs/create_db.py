from models import db
from run import app
from models import User,Post

def create_db():
    with app.app_context():
        post_1 = Post(title='Third Blog', content='My Third Blog Post...', user_id=1)
        db.session.add(post_1)
        post_2 = Post(title='Fourth Blog', content='My Fourth Blog Post...', user_id=1)
        db.session.add(post_2)
        db.session.commit()
        # current_user.image_file = 'default.png'
        # db.session.commit()
        print(User.query.all()[0].posts)

if __name__ == '__main__':
    create_db()
