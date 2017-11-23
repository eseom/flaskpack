# coding: utf-8

"""
"""

from __future__ import unicode_literals, print_function

import random

from flask import jsonify, redirect
from flask_login import logout_user

from ..base import internal_bp, app


@app.route('/')
def index():
    return ''


@internal_bp.route('/hello')
def api_index():
    """
    헬로 테스트
    ---
    tags:
      - test
    responses:
      200:
        description: OK
        schema:
          $ref: '#/definitions/CommonResult'
    """
    if random.randint(0, 3) == 2:
        return jsonify(dict(result=True))
    else:
        resp = jsonify(dict(result=False))
        resp.status_code = 401
        return resp
