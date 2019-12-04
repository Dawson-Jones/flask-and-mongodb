## api

### generate *csv* file

#### request: 

> Nomaly will generate a *csv* file

| method | url | necessary param? | default |
| ---- | ---- | ---- | ---- |
| get | /gen_csv?hour=\<int> | no | 4 |

#### response:  

> json data

   yield|description|data type  
    -|-|-  
    resno | result code|str   
    msg | tips message|str  

   - eg: 
   
     ```json
     {
       "errno": "4002", 
       "msg": "there is no matching data"
     }
     ```

### increase some data in mongoDB

#### request

| method | url             |
| ------ | --------------- |
| get    | /add_panel_test |

#### response

ibid.

### Query by barcode

#### Request

| method | url                  | necessary param? |
| ------ | -------------------- | ---------------- |
| get    | /barcode/find/\<int> | yes              |

#### Response

- Eg

  ```json
  {
    "mes_defects": {},
    "defects": [],
    "barcode": 9988776,
    "cell_type": "mono",
    "origin_defects": {},
    "cell_shape": "half",
    "status": {
      "EL_AI": "OK",
      "EL_OP": "OK",
      "AP_OP": "OK"
    },
    "el_no": "1",
    "ap_defects": {},
    "cell_amount": 144,
    "create_time": 10.0,
    "display_mode": 1
  }
  ```

  