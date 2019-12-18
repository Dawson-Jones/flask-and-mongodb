# mongoDB 部署复制集

### 启动实例 statr each instance

- #### 命令行启动 command-line options

  `mongod --replSet "rs0" --bind_ip localhost,<hostname(s)|ip address(es)>`

- #### 配置文件启动 strat with specify configuration file

  ```
  replication:
     replSetName: "rs0"
  net:
     bindIp: localhost,<hostname(s)|ip address(es)>
  ```

  `mongod --config <path-to-config>`  默认路径(default file path): `/etc/mongodb.conf`

  ***我的做法 my method***
  
  ```
  # Where to store the data.
  dbpath=/mongodb/29019/data
  
  #where to log
  logpath=/mongodb/29019/log/mongodb.log
  
  logappend=true
  
  # bind_ip = 127.0.0.1
  port = 29019
  
  # Enable journaling, http://www.mongodb.org/display/DOCS/Journaling
  journal=true
  ```
  
  `sudo /usr/bin/mongod -f /mongodb/29019/conf/mongo.conf`

### 设置复制集 Initiate the replica set

- #### 连接一个客户端 Connect a `mongo` shell

  `mongo --host <host> --port <port>`

- #### 复制集初始化

  ```
  rs.initiate( {
     _id : "rs0",
     members: [
        { _id: 0, host: "mongodb0.example.net:27017" },
        { _id: 1, host: "mongodb1.example.net:27017" },
        { _id: 2, host: "mongodb2.example.net:27017" }
     ]
  })
  ```

  或 or

  ```
  config = {_id:'rs0',members:[
      {_id:0,host: '192.168.240.21:27017'},
      {_id:1,host: '192.168.240.21:28018'},
      {_id:2,host: '192.168.240.21:29019'}
  ]}
  rs.initiate(config)
  ```

  **完成 finished**

### 其他的 else

- 查看复制集配置 display the replica set configuration object

  `rs.conf()`

  ```
  {
  	"_id" : "rs0",
  	"version" : 1,
  	"members" : [
  		{
  			"_id" : 0,
  			"host" : "127.0.0.1:28018"
  		},
  		{
  			"_id" : 1,
  			"host" : "127.0.0.1:29019"
  		},
  		{
  			"_id" : 2,
  			"host" : "127.0.0.1:30030"
  		}
  	]
  }
  ```

- 查看复制集状态 status

  `rs.status()`

  ```
  {
  	"set" : "rs0",
  	"date" : ISODate("2019-12-05T04:00:28Z"),
  	"myState" : 1,
  	"members" : [
  		{
  			"_id" : 0,
  			"name" : "127.0.0.1:28018",
  			"health" : 1,
  			"state" : 1,
  			"stateStr" : "PRIMARY",
  			"uptime" : 738,
  			"optime" : Timestamp(1575518167, 1),
  			"optimeDate" : ISODate("2019-12-05T03:56:07Z"),
  			"electionTime" : Timestamp(1575517769, 1),
  			"electionDate" : ISODate("2019-12-05T03:49:29Z"),
  			"self" : true
  		},
  		{
  			"_id" : 1,
  			"name" : "127.0.0.1:29019",
  			"health" : 1,
  			"state" : 2,
  			"stateStr" : "SECONDARY",
  			"uptime" : 669,
  			"optime" : Timestamp(1575518167, 1),
  			"optimeDate" : ISODate("2019-12-05T03:56:07Z"),
  			"lastHeartbeat" : ISODate("2019-12-05T04:00:27Z"),
  			"lastHeartbeatRecv" : ISODate("2019-12-05T04:00:26Z"),
  			"pingMs" : 0,
  			"syncingTo" : "127.0.0.1:28018"
  		},
  		{
  			"_id" : 2,
  			"name" : "127.0.0.1:30030",
  			"health" : 1,
  			"state" : 2,
  			"stateStr" : "SECONDARY",
  			"uptime" : 667,
  			"optime" : Timestamp(1575518167, 1),
  			"optimeDate" : ISODate("2019-12-05T03:56:07Z"),
  			"lastHeartbeat" : ISODate("2019-12-05T04:00:27Z"),
  			"lastHeartbeatRecv" : ISODate("2019-12-05T04:00:28Z"),
  			"pingMs" : 0,
  			"syncingTo" : "127.0.0.1:28018"
  		}
  	],
  	"ok" : 1
  }
  ```