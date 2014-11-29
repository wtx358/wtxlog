# -*- coding: utf-8 -*-

import time
import random
import datetime
from flask import current_app


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
        return self.qiniu_save_file()
        # return self.bcs_save_file3()

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
