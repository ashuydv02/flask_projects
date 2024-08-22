from demo_project import app, db, ma, bcrypt, jwt
from .models import Post, User
from flask import request, jsonify
from marshmallow import fields, ValidationError, validates, validates_schema, post_load
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token


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
    
    @post_load
    def create_post(self, data, **kwargs):
        return Post(**data)


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
@jwt_required()
def create_post():
    json_data = request.get_json()
    try:
        post = post_schema.load(json_data)
    except ValidationError as e:
        return jsonify(e.messages), 400
    db.session.add(post)
    db.session.commit()
    return post_schema.dump(post), 201


@app.route('/api/posts/update/<int:id>/', methods=['PUT', 'PATCH'])
@jwt_required()
def update_post(id):
    post = Post.query.get(id)
    if post:
        json_data = request.get_json()
        try:
            post_schema.load(json_data, partial=True)
        except ValidationError as err:
            return jsonify(err.messages), 400
        for field in json_data:
            if hasattr(post, field):
                setattr(post, field, json_data[field])
        db.session.commit()
        return post_schema.dump(post)
    return jsonify({"message": "No Posts found with this id..."})


@app.route('/api/posts/delete/<int:id>/', methods=['DELETE'])
@jwt_required()
def delete_post(id):
    post = Post.query.get(id)
    if post:
        db.session.delete(post)
        db.session.commit()
        return jsonify({"Message": "Post has been sucessfully deleted..."})
    return jsonify({"Message": "No Post found with this id..."})


@app.route('/api/users/')
@jwt_required()
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
    
    user = User(username=data['username'], email=data['email'])
    hashed_password = bcrypt.generate_password_hash(json_data['password']).decode('utf-8')
    user.password = hashed_password
    db.session.add(user)
    db.session.commit()
    return user_schema.dump(user), 201


@app.route('/api/users/update/<id>/', methods=['PUT', 'PATCH'])
@jwt_required()
def update_user(id):
    data = request.get_json()
    username = request.json.get('username')
    password = request.json.get('password')
    try:
        user_update_schema.load(data, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400
    user = User.query.get(id)
    if user:
        if username:
            user.username = data['username']
        if password:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user.password = hashed_password
        db.session.commit()
        return user_schema.dump(user), 201
    return jsonify({"message": "No User found with this id..."})


# JWT Authentication
@app.route('/api/login/', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    user = User.query.filter_by(email=email).first()
    if user is not None:
        if bcrypt.check_password_hash(user.password, password):
            access_token = create_access_token(identity=email)
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"Authentication Error": "Wrong password! please use correct password."}), 404
    else:
        return jsonify({"Authentication Error": "No user found with this email."}), 404
