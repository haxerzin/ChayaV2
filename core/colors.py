from os import system
from sys import platform as sys_platform
from platform import version as platform_version
from platform import platform
from datetime import datetime


# Function > Get current time in Hour:Minute:Second format
def get_current_time():
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    return current_time


color = True
checkplatform = platform()
c_white = c_green = c_red = c_yellow = c_blue = c_bold = c_clean = ''

if sys_platform.lower().startswith(('os', 'win', 'darwin', 'ios')):
    color = False
if checkplatform.startswith("Windows-10") and int(platform_version().split(".")[2]) >= 10586:
    color = True
    system('')
if not color:
    c_white = c_green = c_red = c_yellow = c_blue = c_bold = c_clean = ''
else:
    c_white, c_green, c_red, c_yellow, c_blue, c_bold, c_clean = \
    '\033[97m', '\033[92m', '\033[91m', '\033[93m', '\033[94m', \
    '\033[1m', '\033[0m'

# print colored output
def color(msg: str, color_name: str) -> str:
    match color_name:
        case "white":
            msg = f"{c_white}{msg}{c_clean}"
        case "green":
            msg = f"{c_green}{msg}{c_clean}"
        case "red":
            msg = f"{c_red}{msg}{c_clean}"
        case "yellow":
            msg = f"{c_yellow}{msg}{c_clean}"
        case "blue":
            msg = f"{c_blue}{msg}{c_clean}"
        case "clean":
            msg = f"{c_clean}{msg}"
    return msg


# print colored status
# status codes = 0, 1, 2, 3
# 0 = progress
# 1 = alert - success
# 2 = alert - info
# 3 = alert - error
def status(status_code: int, msg: str) -> None:
    match status_code:
        case 0:
            print(f"{color(msg, 'blue')}")
        case 1:
            print(f"{color(msg, 'green')}")
        case 2:
            print(f"{color(msg, 'yellow')}")
        case 3:
            print(f"{color(msg, 'red')}")
