from string import Template

from actions_toolkit import core

from app import log
from app.action import Action

action = {
    'action': 'me-1 Action',
    'author': 'lentikr',
    'github': 'https://github.com/lentikr'
}

welcome = Template('欢迎使用 $action ❤\n\n 📣 由 $author 维护: $github\n')
log.info(welcome.substitute(action))

try:
    # 获取输入
    username = core.get_input('username', required=True)
    passwd = core.get_input('passwd', required=True)
    host = core.get_input('host', required=True)
    login_path = core.get_input('login_path', required=True)
    token_path = core.get_input('token_path', required=True)
    checkin_path = core.get_input('checkin_path', required=True)

    action = Action(username, passwd, host, login_path, token_path, checkin_path)
    try:
        # 登录
        res = action.login()
        if res['code'] != 0:
            log.set_failed(f'帐号登录失败，错误信息：{res["msg"]}')
        else:
            log.info(f'帐号登录成功，用户名：{res["userName"]}')

        # 签到
        res = action.get_csrf_token()
        if res == None:
            log.set_failed(f'获取token失败')
        action.checkin()
        res = action.get_csrf_token(True)
        if res == ():
            log.set_failed('签到失败')
        else:
            log.info(f'今日签到获得积分：{res[0]}；积分余额：{res[1]}')

        # 成功运行，退出循环
        log.info(f'me-1 Action 成功结束运行！')
    except Exception as e:
        # 失败，尝试下一个 host
        log.warning(f'me-1 Action 运行异常，错误信息：{str(e)}')

except Exception as e:
    log.set_failed(str(e))
