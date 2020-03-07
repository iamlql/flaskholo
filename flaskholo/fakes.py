# -*- coding: utf-8 -*-

import os
import random

from PIL import Image
from faker import Faker
from flask import current_app
from sqlalchemy.exc import IntegrityError

from flaskholo.extensions import db
from flaskholo.models import User, Photo, Tag, Comment, Notification, Location
# from flaskholo.detections import 

fake = Faker()


def fake_admin():
    admin = User(name='Frank Lu',
                 username='luql',
                 email='admin@flaskholo.com',
                 bio=fake.sentence(),
                 website='http://thinker.com',
                 confirmed=True)
    admin.set_password('flaskholo')
    notification = Notification(message='Hello, welcome to Flask-Holo.', receiver=admin)
    db.session.add(notification)
    db.session.add(admin)
    db.session.commit()


def fake_user(count=10):
    for i in range(count):
        user = User(name=fake.name(),
                    confirmed=True,
                    username=fake.user_name(),
                    bio=fake.sentence(),
                    location=fake.city(),
                    website=fake.url(),
                    member_since=fake.date_this_decade(),
                    email=fake.email())
        user.set_password('123456')
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_follow(count=30):
    for i in range(count):
        user = User.query.get(random.randint(1, User.query.count()))
        user.follow(User.query.get(random.randint(1, User.query.count())))
    db.session.commit()


def fake_tag(count=4):
    for i in range(count):
        tag = Tag(name=fake.word())
        db.session.add(tag)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_photo(count=30):
    # photos
    upload_path = current_app.config['FLASKHOLO_UPLOAD_PATH']
    for i in range(count):
        print(i)

        filename = 'random_%d.jpg' % i
        r = lambda: random.randint(128, 255)
        img = Image.new(mode='RGB', size=(800, 800), color=(r(), r(), r()))
        img.save(os.path.join(upload_path, filename))

        photo = Photo(
            #description=fake.text(),
            filename=filename,
            filename_m=filename,
            filename_s=filename,
            author=User.query.get(random.randint(1, User.query.count())),
            timestamp=fake.date_time_this_year()
        )

        # tags
        category_list = []
        for j in range(random.randint(1, 3)):
            tag = Tag.query.get(random.randint(1, Tag.query.count()))
            if tag not in photo.tags:
                photo.tags.append(tag)
                location = Location(xmin=random.randint(128, 255), ymin=random.randint(128, 255), 
                    xmax=random.randint(128, 255), ymax=random.randint(128, 255))
                location.pic = photo
                location.tag = tag
                category_list.append('{}: ({}  {}  {}  {});'.format(tag.name, location.xmin, location.ymin, location.xmax, location.ymax))

        photo.description = '\n'.join(category_list)

        db.session.add(photo)
        db.session.add(location)
    db.session.commit()

def fake_collect(count=50):
    for i in range(count):
        user = User.query.get(random.randint(1, User.query.count()))
        user.collect(Photo.query.get(random.randint(1, Photo.query.count())))
    db.session.commit()


def fake_comment(count=100):
    for i in range(count):
        comment = Comment(
            author=User.query.get(random.randint(1, User.query.count())),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            photo=Photo.query.get(random.randint(1, Photo.query.count()))
        )
        db.session.add(comment)
    db.session.commit()
