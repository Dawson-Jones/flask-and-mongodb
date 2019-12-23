## 启动 start project  
`pip install -r requirements.txt`  

### mode
**debug**: python manager.py runserver  

> 部署时, 把manager中的create_app("develop")改为create_app("product")  
> when deploy, change the create_app("develop") to create_app("product") which in manager.py

**product**:   
- regular start up  
  `gunicorn -w 4 -b 0.0.0.0:5000 -D --access-logfile ./log manager:app`  
  or  
  `gunicorn manager:app -c gunicorn.conf.py`  
- start in docker  
  `sudo docker-compose -f docker-compose.yml up`

> here's when you start successful command input `ps -ef | grep gunicorn` will appeared like this:
```
/root/ihome/venv/bin/python3 /root/ihome/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 -D --access-logfile ./logs/log manager:app
/root/app/venv/bin/python3 /root/app/venv/bin/gunicorn blogproject.wsgi -D -w 2 -k gthread -b 0.0.0.0:8000
```

### tip
export a container: `sudo docker export <container id> > <name.tar>`  
import a container snapshot file make it become to image  
`cat <snapshot.tar> | docker import - <rebo/image name:tag>`
