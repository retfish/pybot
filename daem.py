import time
from pb2 import DB
from datetime import *


def hms_to_seconds(t):
    h, m, s = [int(i) for i in t.split(':')]
    return 3600*h + 60*m + s


server_time = datetime.now().strftime('%H:%M:%S')
db = DB()
user_time = db.execute_one('SELECT CreatedTime FROM board_sd_bot_user WHERE code = %s', 579198619)  # брать из базы
time_diff = (hms_to_seconds(server_time) - hms_to_seconds(user_time[0])) // 3600
db.execute('UPDATE board_sd_bot_user SET TimeDiff = %s WHERE Code = %s', (time_diff, 579198619 ))
db.close()
st = server_time + str(timedelta(hours=time_diff))
print('>>>', st[:8])

