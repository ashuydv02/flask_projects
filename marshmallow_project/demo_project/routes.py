from demo_project import app, db, ma, bcrypt
from .models import Post, User
from flask import request, jsonify
from marshmallow import fields, ValidationError, validates, validates_schema

# Use of marshmallow without sqlalchemy integration
# class PostSchema(ma.Schema):
#     class Meta:
#         fields = ('title', 'user_id', 'content', 'date_posted')


# post_schema = PostSchema()
# posts_schema = PostSchema(many=True)


# class UserSchema(ma.Schema):
#     class Meta:
#         fields = ('username', 'email')


# user_schema = UserSchema()
# users_schema = UserSchema(many=True)

# Use of marshmallow with sqlalchemy integration
class PostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Post
        include_fk = True


class UserSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    confirm_password = fields.Str(load_only=True, required=True)
    posts = fields.List(fields.Nested(PostSchema), dump_only=True)

    @validates_schema
    def validate_passwords(self, data, **kwargs):
        if data.get('password') != data.get('confirm_password'):
            raise ValidationError("Passwords must match.")
    
    @validates('email')
    def validate_email(self, value):
        if User.query.filter_by(email=value).first():
            raise ValidationError("Email Already in use.")

user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_update_schema = UserSchema(only=('username', 'password', 'confirm_password'))
post_schema = PostSchema()
posts_schema = PostSchema(many=True)


@app.route('/api/posts/')
def posts():
    all_posts = Post.query.all()
    return posts_schema.dump(all_posts)


@app.route('/api/posts/<id>/')
def post_detail(id):
    post = Post.query.get(id)
    return post_schema.dump(post)

@app.route('/api/posts/create/', methods=['POST'])
def create_post():
    json_data = request.get_json()
    try:
        data = post_schema.load(json_data)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    post = Post(title=data['title'], content=data['content'], user_id=data['user_id'])
    db.session.add(post)
    db.session.commit()
    return post_schema.dump(post), 201


@app.route('/api/posts/update/<int:id>/', methods=['PATCH'])
def update_post(id):
    post = Post.query.get(id)
    if post:
        title = request.json.get('title')
        content = request.json.get('content')
        if title:
            post.title = title
        if content:
            post.content = content
        db.session.commit()
        return post_schema.dump(post)
    return jsonify({"message": "No Posts found with this id..."})


@app.route('/api/posts/delete/<int:id>/', methods=['DELETE'])
def delete_post(id):
    post = Post.query.get(id)
    if post:
        db.session.delete(post)
        db.session.commit()
        return jsonify({"Message": "Post has been sucessfully deleted..."})
    return jsonify({"Message": "No Post found with this id..."})


@app.route('/api/users/')
def users():
    all_users = User.query.all()
    return users_schema.dump(all_users)

@app.route('/api/users/create/', methods=['POST'])
def create_user():
    json_data = request.get_json()
    try:
        data = user_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(username=data['username'],email=data['email'],password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return user_schema.dump(user), 201


@app.route('/api/users/update/<id>/', methods=['PUT', 'PATCH'])
def update_user(id):
    json_data = request.get_json()
    try:
        data = user_update_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    user = User.query.get(id)
    if user:
        user.username = data['username']
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        return user_schema.dump(user), 201
    return jsonify({"message": "No User found with this id..."})

