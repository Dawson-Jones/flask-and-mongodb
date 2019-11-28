import time

ctime = time.strftime('%Y%m%d%H%M%S')
print(ctime)
print(type(ctime))

time_p = time.strptime(ctime, '%Y%m%d%H%M%S')
print(time_p)
print(time_p.tm_hour)
