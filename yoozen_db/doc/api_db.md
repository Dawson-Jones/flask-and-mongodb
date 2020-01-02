# Database API Design
Version|Time|Revised By|Description
:---:|:---:|:---:|:---:
2.5|2019.04.23|Kevin|add string system
2.6|2019.04.23|Kevin|add thresholds for panel

### 1. send pic
#### Request: wd -> db (/panel/add)
Key|Type|Description
:---:|:---:|:---:
barcode|str|panel barcode
cell_type|str|
cell_amount|int|
cell_shape|str|
el_no|str|
display_mode|int|
module_no|int|
thresholds|dict|
create_time|float|pic created time
ai_result|int|0 for NG; 1 for OK; 2 for ERROR
ai_defects|dict|dict for 4 kinds of defects
gui_result|int|0 for NG; 1 for OK
gui_defects|dict|dict for 4 kinds of defects
```json
{
  "barcode": "201901010000",
  "cell_type": "mono",
  "cell_amount": 120,
  "cell_shape": "half",
  "el_no": "line0",
  "display_mode": 1,
  "module_no": 2,
  "thresholds": {
    "cr_size": 60,
    "cs_width": 50,
    "mr_tolerance": 50
  },
  "create_time": 1548056846.8,
  "ai_result": 0,
  "ai_defects": {
    "cr": [
      {
        "x": 5,
        "y": 11,
        "w": 20,
        "h": 20,
        "c": "5 11"
      }
    ],
    "cs": [],
    "mr": [],
    "bc": []
  },
  "gui_result": 0,
  "gui_defects": {
    "cr": [
      {
        "x": 5,
        "y": 11,
        "w": 20,
        "h": 20,
        "c": "5 11"
      },
      {
        "x": 1,
        "y": 1,
        "w": 1,
        "h": 1,
        "c": "1 1"
      }
    ],
    "cs": [],
    "mr": [],
    "bc": []
  }
}
```
#### Response: db -> wd
only status code

### 2. el send string
#### Request: wd -> db (/string/add)
Key|Type|Description
:----:|:----:|:----:
image_id|str|
cell_type|str|"poly" or "mono"
cell_amount|int|
cell_shape|str|
string_line|str|the name of the string line
create_time|float|create time of the string image
result|int|0 for NG, 1 for OK, 2 for ERROR
defects|dict|dict for 4 kinds of defects
```json
{
  "image_id": "11111",
  "cell_type": "poly",
  "cell_amount": 13,
  "cell_shape": "half",
  "string_line": "line0",
  "create_time": 1548047485.24,
  "result": 0,
  "defects": {
    "cr": [
      {
        "x": 5,
        "y": 11,
        "w": 20,
        "h": 20,
        "c": "5 11"
      },
      {
        "x": 1,
        "y": 1,
        "w": 1,
        "h": 1,
        "c": "1 1"
      }
    ],
    "cs": [],
    "mr": [],
    "bc": []
  }
}
```
#### Response: db -> wd
only status code

### 3. check el_panel config
#### Request: wd -> db (/el_panel/config/check)
Key|Type|Description
:---:|:---:|:---:
el_no|str|
```json
{
  "el_no": "line0"
}
```
#### Response: db -> wd
Key|Type|Description
:---:|:---:|:---:
cell_type|str|
cell_amount|int|
cell_shape|str|
display_mode|int|
thresholds|dict|
gui_url|str|
```json
{
  "el_no": "line0",
  "cell_type": "mono",
  "cell_amount": 120,
  "cell_shape": "half",
  "display_mode": 1,
  "thresholds": {
    "cr_size": 60,
    "cs_width": 50,
    "mr_tolerance": 50
  },
  "gui_url": "192.168.2.26:3000"
}
```

### 4. check el_string config
#### Request: wd -> db (/el_string/config/check)
Key|Type|Description
:---:|:---:|:---:
string_line|str|
```json
{
  "string_line": "line0"
}
```
#### Response: db -> wd
Key|Type|Description
:---:|:---:|:---:
string_line|str|
cell_type|str|
cell_amount|int|
cell_shape|str|
```json
{
  "string_line": "line0",
  "cell_type": "mono",
  "cell_amount": 120,
  "cell_shape": "half"
}
```

### 5. check gui config
#### Request: wd -> db (/gui/config/check)
Key|Type|Description
:---:|:---:|:---:
gui_no|str|
```json
{
  "gui_no": "gui1"
}
```
#### Response: db -> wd 
Key|Type|Description
:---:|:---:|:---:
gui_no|str|
gui_url|str|
mode|str|"auto" or "manual"
auto_time|int|
manual_time|int|
el_limit|int|
```json
{
  "gui_no": "gui1",
  "gui_url": "192.168.2.26:8093",
  "mode": "auto",
  "auto_time": 5,
  "manual_time": 20,
  "el_limit": 3
}
```

### 6. operator login
#### Request: wd -> db (/user/login/operator)
Key|Type|Description
:---:|:---:|:---:
user_name|str|
user_pw|str|
time|float|time for the login request
```json
{
  "user_name": "kevin",
  "user_pw": "9436",
  "time": 1548056846.8
}
```
#### Response: db -> wd
only response code

### 7. admin login
#### Request: wd -> db (/user/login/admin)
Key|Type|Description
:---:|:---:|:---:
user_name|str|
user_pw|str|
admin_url|str|
time|float|time for the login request
```json
{
  "user_name": "kevin",
  "user_pw": "9436",
  "admin_url": "192.168.2.26",
  "time": 1548056846.8
}
```
#### Response: db -> wd
Key|Type|Description
:---:|:---:|:---:
type|str|
user_mng|list|
permission_mng|list|
line_setting|list|
string_setting|list|
gui_setting|list|
thresholds|list|
previous_url|str|
```json
{
  "type": "yc admin",
  "permission_mng": [
    {
      "type": "super admin",
      "level_mng": 1,
      "user_mng": 1,
      "display_mode": 1,
      "ai_module": 1,
      "threshold": 1,
      "el_gui": 1,
      "auto_manual": 1,
      "shift_mng": 1,
      "pic_upload": 1,
      "update_time": 0
    }
  ],
  "line_setting": [
    {
      "el_no": "line0",
      "pre_wd_url": "192.168.2.26:8080",
      "cell_type": "mono",
      "cell_amount": 120,
      "cell_shape": "half",
      "display_mode": 1,
      "gui_no": 1,
      "gui_url": "192.168.2.26:3000",
      "update_time": 0
    }
  ],
  "string_setting": [
    {
      "string_line": "string_line",
      "el_url": "192.168.2.26:8080",
      "cell_type": "mono",
      "cell_amount": 13,
      "cell_shape": "half",
      "update_time": 0
    }
  ],
  "gui_setting": [
    {
      "gui_no": 1,
      "gui_url": "192.168.2.26:3000",
      "mode": "auto",
      "auto_time": 5,
      "manual_time": 20,
      "el_limit": 3,
      "update_time": 0
    }
  ],
  "thresholds": [
    {
      "el_no": "EL1",
      "el_url": "192.168.2.26:8080",
      "cr_size": 60,
      "cs_width": 50,
      "mr_tolerance": 50,
      "update_time": 0
    }
  ],
  "previous_url": "192.168.2.26"
}
```

### 8. add user
#### Request: wd -> db (/user/add)
Key|Type|Description
:---:|:---:|:---:
type|int|0 for operator, 1 for admin
user_name|str|user name to be added
user_pw|str| user password to be added
time|float|time for the add user request
admin_name|str|name for the current admin
```json
{
  "type": "operator",
  "user_name": "kevin",
  "user_pw": "9436",
  "time": 1548056846.8,
  "admin_name": "root"
}
```
#### Response: db -> wd
status code|respond body
:---:|:---:
413|json data to update
422|json data to update
others|str message data

### 9. delete user
#### Request: wd -> db (/user/delete)
Key|Type|Description
:---:|:---:|:---:
user_name|str|user name to be deleted
time|float|time for the delete user request
admin_name|str|name for the current admin
```json
{
  "user_name": "kevin",
  "time": 1548056846.8,
  "admin_name": "root"
}
```
#### Response: wd -> gui
only status code

### 10. modify user
#### Request: wd -> db (/user/modify)
Key|Type|Description
:---:|:---:|:---:
user_name|str|origin user's name
changed_items|dict|
admin_name|str|
time|float|
```json
{
  "user_name": "kevin",
  "changed_items": {
    "user_name": "hello_kitty",
    "type": "admin",
    "update_time": 0
  },
  "admin_name": "root",
  "time": 1548133162.51
}
```
#### Response: db -> wd 
status code|respond body
:---:|:---:
422|json data to update
others|str message data

### 11. display all user
#### Request: wd -> db (/user/display)
methods = \['GET']
#### Response: db -> wd
Key|Type|Description
:---:|:---:|:---:
users|list|list of users' info
```json
{
  "users": [
    {
      "user_name": "kevin",
      "type": "operator",
      "update_time": 0
    },
    {
      "user_name": "patrick",
      "type": "admin",
      "update_time": 0
    }
  ]
}
```

### 12. modify el_panel config
#### Request: wd -> db (/el_panel/config/modify)
Key|Type|Description
:---:|:---:|:---:
admin_name|str|name for the current admin
time|float|time for the change operation
el_no|str|
changed_items|dict|include key-value pair of the pre_wd config
```json
{
  "admin_name": "kevin",
  "time": 1548056846.8,
  "el_no": "line0",
  "changed_items": {
    "cell_type": "mono",
    "display_mode": 2,
    "update_time": 0
  }
}
```
#### Response: db -> wd
status code|respond body
:---:|:---:
422|json data to update
others|str message data

### 13. modify el_string config
#### Request: wd -> db (el_string/config/modify)
Key|Type|Description
:---:|:---:|:---:
admin_name|str|name for the current admin
time|float|time for the change operation
string_line|str|
changed_items|dict|include key-value pair of the el_string config
```json
{
  "admin_name": "kevin",
  "time": 1548056846.8,
  "el_no": "line0",
  "changed_items": {
    "cell_type": "mono",
    "display_mode": 2,
    "update_time": 0
  }
}
```
#### Response: db -> wd
status code|respond body
:---:|:---:
422|json data to update
others|str message data

### 14. modify gui setting
#### Request: wd -> db (/gui/config/modify)
Key|Type|Description
:---:|:---:|:---:
admin_name|str|
time|float|
gui_no|str|
changed_items|dict
```json
{
  "admin_name": "kevin",
  "time": 1548056846.8,
  "gui_no": "gui1",
  "changed_items": {
    "mode": "auto",
    "manual_time": 30,
    "update_time": 0
  }
}
```
#### Response: db -> wd
status code|respond body
:---:|:---:
422|json data to update
others|str message data

### 15. modify permission
#### Request: wd -> db (/permission/modify)
Key|Type|Description
:---:|:---:|:---:
admin_name|str|
time|float|
changed_items|dict|
```json
{
  "admin_name": "kevin",
  "time": 1548056846.8,
  "changed_items": [
    {
      "type": "admin",
      "level_mng": 1,
      "user_mng": 1,
      "display_mode": 1,
      "ai_module": 1,
      "threshold": 1,
      "el_gui": 1,
      "auto_manual": 1,
      "shift_mng": 1,
      "pic_upload": 1,
      "update_time": 0
    }
  ]
}
```
#### Response: db -> wd 
status code|respond body
:---:|:---:
422|json data to update
others|str message data

### 16. modify thresholds
#### Requests: wd -> db (el_panel/thresholds/modify)
Key|Type|Description
:---:|:---:|:---:
admin_name|str|name for the current admin
time|float|time for the change operation
el_no|str|
thresholds|dict|new thresholds
```json
{
  "admin_name": "kevin",
  "time": 1548056846.8,
  "el_no": "line0",
  "thresholds": {
    "cr_size": 60,
    "cs_width": 50,
    "mr_tolerance": 50
  }
}
```
#### Response: db -> wd 
status code|respond body
:---:|:---:
422|json data to update
others|str message data