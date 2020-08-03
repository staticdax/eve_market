## EVE Swagger Interface 数据API

晨曦: `https://esi.evepc.163.com/`  
宁静: `https://esi.evetech.net/`

说明文档: https://esi.evepc.163.com/ui?version=latest

TODO:
- 运用GC机制
- 星域内物流功能

### 市场数据（不需账号授权）

- GET /markets/{region_id}/history/
  - 商品历史价格
  - 参数：星域ID，商品
  - 返回
    - 平均价格
    - 日期
    - 最高价格
    - 最低价格
    - 成交订单数
    - 成交商品量

- GET /markets/{region_id}/orders/
  - 星域市场挂单数据
  - 参数：挂单类型：买/卖，页数，星域ID，商品ID
  - 返回
    - 挂单时效
    - 是否买单
    - 下单时间
    - 地点（空间站id）
    - 最小成交量
    - 订单ID
    - 价格
    - 成交范围
    - 星系ID
    - 商品ID
    - 商品余量
    - 商品总量

- GET /markets/{region_id}/types/
  - 星域内市场存在的订单数据
  - 参数：星域ID，页数

- GET /markets/groups/
  - 所有商品的分类ID
  - 参数：无

- GET /markets/groups/{market_group_id}/
  - 商品分类ID信息
  - 参数：商品分类ID

- GET /markets/groups/{market_group_id}/
  - 返回所有商品的平均价格和调整价格
  - 参数：无

### 物品数据

- GET /universe/types/{type_id}/
  - 返回type_id对应物品的所有信息
  - 参数：
    - language：zh/en-us
    - type_id

### 数据形式

- data_helper.region_markets_orders_dict  
`{regoin_id_1: [{order_1}, {order_2}...], region_id_2: [{}, {}, ...], ...}`

- data_helper.all_orders_by_typeid_dict  
`{type_id_1: [{order_1}, {order_2}, ...], type_id_2: [{}, {},...], ...}`

- data_helper.all_profitable_orders_dict  
`{type_id_1:{'type_name': info, 'profit': info, ..., 'buy': [{order}, ...], 'sell': [{order}, ...]}, type_id_2: {...}, ...}`
  - 经过sorted()得到的列表在转换为all_profitable_orders_sorted_dict字典  
  `{type_id_1: {'type_name': info, 'profit': info, ..., 'buy': [{order}, ...], 'sell': [{order}, ...]}, type_id_2: {...}, ...}`

- 中间结果
  - profitable_bns_orders_dict  
  `{type_id_1: {'buy':[{order_1}, {order_2}, ...],'sell':[{}, {}, ...]}, type_id_2: {...}, ...}`  
  'buy'列表是买家订单列表，价格按降序排列  
  'sell'列表是卖家订单列表，价格按升序排列  

  - bns_orders_dict
  `{'buy':[{order_1}, {order_2}, ...],'sell':[{}, {}, ...]}`


### 历史数据记录

路径: `data/markets/{region_id}/history/{type_id}.json`




### 辅助查询

#### typeID, typeName互查

<https://www.fuzzwork.co.uk/api/typeid.php?typeid=47115>
<https://www.fuzzwork.co.uk/api/typeid.php?typename=Tritanium>
```
$ curl https://www.fuzzwork.co.uk/api/typeid.php\?typeid\=34
{"typeID": 34,"typeName": "Tritanium"}

$ curl https://www.fuzzwork.co.uk/api/typeid.php\?typename\=Tritanium
{"typeID": 34,"typeName": "Tritanium"}

curl https://www.fuzzwork.co.uk/api/typeid.php\?typeid\=47115
{"typeID": 47115,"typeName": "Standup Gravitational Transportation Field Oscillator Blueprint"}
```