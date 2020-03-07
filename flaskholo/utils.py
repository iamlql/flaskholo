# -*- coding: utf-8 -*-

import os
import uuid

try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

import PIL
from PIL import Image
import numpy as np
import cv2
from flask import current_app, request, url_for, redirect, flash
from itsdangerous import BadSignature, SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from flaskholo.extensions import db, md
from flaskholo.models import User
from flaskholo.settings import Operations


def generate_token(user, operation, expire_in=None, 
    **kwargs):
    s = Serializer(current_app.config['SECRET_KEY'], expire_in)

    data = {'id': user.id, 'operation': operation}
    data.update(**kwargs)
    return s.dumps(data)


def validate_token(user, token, operation, new_password=None):
    s = Serializer(current_app.config['SECRET_KEY'])

    try:
        data = s.loads(token)
    except (SignatureExpired, BadSignature):
        return False

    if operation != data.get('operation') or user.id != data.get('id'):
        return False

    if operation == Operations.CONFIRM:
        user.confirmed = True
    elif operation == Operations.RESET_PASSWORD:
        user.set_password(new_password)
    elif operation == Operations.CHANGE_EMAIL:
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if User.query.filter_by(email=new_email).first() is not None:
            return False
        user.email = new_email
    else:
        return False

    db.session.commit()
    return True


def rename_image(old_filename):
    ext = os.path.splitext(old_filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename


def detect_image(filename):
    image_path = os.path.join(current_app.config['FLASKHOLO_UPLOAD_PATH'], filename)
    filename, ext = os.path.splitext(filename)
    
    # print(image_path)
    img, key_list, index_list = md.detect_img(image_path)
    filename += '_d' + ext
    cv2.imwrite(os.path.join(current_app.config['FLASKHOLO_UPLOAD_PATH'], filename), img)
    return img, filename, key_list, index_list

# def resize_image(image, filename, base_width):
#     filename, ext = os.path.splitext(filename)
#     img = Image.open(image)
#     if img.size[0] <= base_width:
#         return filename + ext
#     w_percent = (base_width / float(img.size[0]))
#     h_size = int((float(img.size[1]) * float(w_percent)))
#     img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)

#     filename += current_app.config['FLASKHOLO_PHOTO_SUFFIX'][base_width] + ext
#     img.save(os.path.join(current_app.config['FLASKHOLO_UPLOAD_PATH'], filename), optimize=True, quality=85)
#     return filename


def resize_image(img, filename, base_width):
    filename, ext = os.path.splitext(filename)
    if img.shape[0] <= base_width:
        return filename + ext
    w_percent = (base_width / float(img.shape[0]))
    h_size = int((float(img.shape[1]) * float(w_percent)))
    img = cv2.resize(img, (h_size, base_width), interpolation=cv2.INTER_CUBIC)

    filename += current_app.config['FLASKHOLO_PHOTO_SUFFIX'][base_width] + ext
    cv2.imwrite(os.path.join(current_app.config['FLASKHOLO_UPLOAD_PATH'], filename), img)
    return filename


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def redirect_back(default='main.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))
