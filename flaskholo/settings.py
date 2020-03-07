# -*- coding: utf-8 -*-

import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


class Operations:
    CONFIRM = 'confirm'
    RESET_PASSWORD = 'reset-password'
    CHANGE_EMAIL = 'change-email'


class BaseConfig:
    FLASKHOLO_ADMIN_EMAIL = os.getenv('FLASK_HOLO_ADMIN', 'admin@flaskholo.com')
    FLASKHOLO_PHOTO_PER_PAGE = 12
    FLASKHOLO_COMMENT_PER_PAGE = 15
    FLASKHOLO_NOTIFICATION_PER_PAGE = 20
    FLASKHOLO_USER_PER_PAGE = 20
    FLASKHOLO_MANAGE_PHOTO_PER_PAGE = 20
    FLASKHOLO_MANAGE_USER_PER_PAGE = 30
    FLASKHOLO_MANAGE_TAG_PER_PAGE = 50
    FLASKHOLO_MANAGE_COMMENT_PER_PAGE = 30
    FLASKHOLO_SEARCH_RESULT_PER_PAGE = 20
    FLASKHOLO_MAIL_SUBJECT_PREFIX = '[Flask-Holo]'
    FLASKHOLO_UPLOAD_PATH = os.path.join(basedir, 'uploads')
    FLASKHOLO_PHOTO_SIZE = {'small': 400,
                         'medium': 800}
    FLASKHOLO_PHOTO_SUFFIX = {
        FLASKHOLO_PHOTO_SIZE['small']: '_s',  # thumbnail
        FLASKHOLO_PHOTO_SIZE['medium']: '_m',  # display
    }

    SECRET_KEY = os.getenv('SECRET_KEY', 'secret string')
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024  # file size exceed to 3 Mb will return a 413 error response.

    BOOTSTRAP_SERVE_LOCAL = True

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    AVATARS_SAVE_PATH = os.path.join(FLASKHOLO_UPLOAD_PATH, 'avatars')
    AVATARS_SIZE_TUPLE = (30, 100, 200)

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('Flask-Holo Admin', MAIL_USERNAME)

    DROPZONE_ALLOWED_FILE_TYPE = 'image'
    DROPZONE_MAX_FILE_SIZE = 3
    DROPZONE_MAX_FILES = 30
    DROPZONE_ENABLE_CSRF = True

    WHOOSHEE_MIN_STRING_LEN = 1


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = \
        prefix + os.path.join(basedir, 'data-dev.db')
    REDIS_URL = "redis://localhost"


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'  # in-memory database


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',
                                        prefix + os.path.join(basedir, 'data.db'))


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}

class FasterRCNNConfig(object):

    def __init__(self):
        self.verbose = True

        # base CNN model
        self.network =  'resnet50'

        # setting for data augmentation
        self.use_horizontal_flips = False
        self.use_vertical_flips = False
        self.rot_90 = False

        # 比赛的时候，调整anchor_box_scales和anchor_box_ratios
        # anchor box scales
        self.anchor_box_scales = [128, 256, 512]

        # anchor box ratios
        self.anchor_box_ratios = [[1, 1], [1, 2], [2, 1]]

        # size to resize the smallest side of the image
        self.im_size = 600

        # image channel-wise mean to subtract
        self.img_channel_mean = [103.939, 116.779, 123.68]
        self.img_scaling_factor = 1.0

        # number of ROIs at once
        self.num_rois = int(32) #300

        # stride at the RPN (this depends on the network configuration)
        self.rpn_stride = 16

        self.balanced_classes = False

        # scaling the stdev
        # 基于样本估算标准偏差。标准偏差反映数值相对于平均值(mean) 的离散程度。
        self.std_scaling = 4.0
        self.classifier_regr_std = [8.0, 8.0, 4.0, 4.0]

        # overlaps for RPN
        self.rpn_min_overlap = 0.3
        self.rpn_max_overlap = 0.7

        # overlaps for classifier ROIs
        self.classifier_min_overlap = 0.1 # 0.3
        self.classifier_max_overlap = 0.5 # 0.8

        # placeholder for the class mapping, automatically generated by the parser
        self.class_mapping = {'door': 0, 'door_hole': 1, 'dual_door': 2, 'four_door': 3, 'window': 4, 'bg': 5}

        #location of pretrained weights for the base network
        self.model_path = os.path.join(basedir, 'model.h5')
        self.base_net_weights = os.path.join(basedir, 'model.h5')

class YOLOConfig(object):
    def __init__(self):
        pass

detector_config = {
    'frcnn': FasterRCNNConfig,
    'yolov3': YOLOConfig
}