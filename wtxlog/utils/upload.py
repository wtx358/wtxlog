# -*- coding: utf-8 -*-

import os
import time
import random
import datetime
from flask import current_app, url_for


class SaveUploadFile:
    """文件上传到去云存储，包括BCS和七牛"""

    def __init__(self, fext, data):
        # 图片文件自动生成文件名
        # 非图片文件使用原文件名
        if fext.startswith('.'):
            self.filename = u'%s/%s%s' % (self.gen_dirname(),
                                          self.gen_filename(), fext)
        else:
            self.filename = u'%s/%s' % (self.gen_dirname(), fext)
        self.data = data

    def gen_dirname(self):
        return datetime.date.today().strftime('%Y%m')

    def gen_filename(self):
        filename_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))

    def save(self):
        if current_app.config.get('QINIU_AK') and \
                current_app.config.get('QINIU_SK'):
            return self.qiniu_save_file()
        return self.local_save_file()

    def qiniu_save_file(self):
        # 七牛云存储文件上传
        import qiniu.io
        import qiniu.rs
        import qiniu.conf

        qiniu.conf.ACCESS_KEY = current_app.config.get('QINIU_AK')
        qiniu.conf.SECRET_KEY = current_app.config.get('QINIU_SK')
        _bucket = current_app.config.get('QINIU_BUCKET')
        _domain = current_app.config.get('QINIU_DOMAIN')

        policy = qiniu.rs.PutPolicy(_bucket)
        uptoken = policy.token()

        extra = qiniu.io.PutExtra()
        # extra.mime_type = "text/plain"

        # data 可以是str或read()able对象
        # data = StringIO.StringIO("hello2!")
        ret, err = qiniu.io.put(uptoken, self.filename, self.data, extra)
        time.sleep(1)  # 等待文件上传完成

        try:
            assert err is None
            return 'http://%s/%s' % (_domain, self.filename)
        except:
            return ''

    def bcs_save_file3(self):
        """upload file to BCS in BAE3.0"""
        # 保存二进制文件到BCS
        import pybcs
        BCS_HOST = current_app.config.get('BCS_HOST')
        BCS_NAME = current_app.config.get('BCS_NAME')
        BAE_AK = current_app.config.get('BAE_AK')
        BAE_SK = current_app.config.get('BAE_SK')

        bcs = pybcs.BCS(BCS_HOST, BAE_AK, BAE_SK, pybcs.HttplibHTTPC)
        b = bcs.bucket(BCS_NAME)
        o = b.object('/%s' % self.filename.encode('utf-8'))
        result = o.put(self.data)
        time.sleep(1)  # 等待文件上传完成
        try:
            assert result['status'] == 200
            return 'http://%s/%s/%s' % (BCS_HOST, BCS_NAME, self.filename)
        except:
            return ''

    def local_save_file(self):
        '''保存文件到static目录'''
        error = None
        UPLOAD_FOLDER = os.path.join(current_app.static_folder, 'uploadfiles')
        filepath = os.path.join(UPLOAD_FOLDER, self.filename)

        # 检查路径是否存在，不存在则创建
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except:
                error = 'ERROR_CREATE_DIR'
        elif not os.access(dirname, os.W_OK):
            error = 'ERROR_DIR_NOT_WRITEABLE'

        if not error:
            with open(filepath, 'wb') as fp:
                fp.write(self.data)
            return url_for('static', filename='%s/%s' % ('uploadfiles', self.filename))
        return ''
