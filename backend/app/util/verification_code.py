"""
验证码生成和存储工具
"""
import random
import string
from datetime import datetime, timedelta

# 内存存储验证码（生产环境应使用Redis等）
verification_codes = {}


def generate_verification_code():
    """
    生成6位包含大小写字母和数字的随机验证码
    :return: 验证码字符串
    """
    # 包含大小写字母和数字
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))


def store_verification_code(user_id, role, contact, method, code):
    """
    存储验证码
    :param user_id: 用户ID
    :param role: 角色 'student' 或 'teacher'
    :param contact: 联系方式（邮箱或电话）
    :param method: 验证方式 'email' 或 'phone'
    :param code: 验证码
    :return: 存储的key
    """
    key = f"{role}:{user_id}:{method}"
    verification_codes[key] = {
        'code': code,
        'contact': contact,
        'expires_at': datetime.now() + timedelta(minutes=10),  # 10分钟过期
    }
    return key


def get_verification_code(user_id, role, method):
    """
    获取存储的验证码
    :param user_id: 用户ID
    :param role: 角色 'student' 或 'teacher'
    :param method: 验证方式 'email' 或 'phone'
    :return: (code, contact) 或 (None, None) 如果不存在或已过期
    """
    key = f"{role}:{user_id}:{method}"
    if key not in verification_codes:
        return None, None
    
    stored = verification_codes[key]
    if datetime.now() > stored['expires_at']:
        # 已过期，删除
        del verification_codes[key]
        return None, None
    
    return stored['code'], stored['contact']


def delete_verification_code(user_id, role, method):
    """
    删除验证码
    :param user_id: 用户ID
    :param role: 角色 'student' 或 'teacher'
    :param method: 验证方式 'email' 或 'phone'
    """
    key = f"{role}:{user_id}:{method}"
    if key in verification_codes:
        del verification_codes[key]

