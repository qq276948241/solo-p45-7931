# 宠物寄养小店管理系统 API 参考文档

> Base URL: `http://your-domain:8000`
> 数据格式: 所有请求和响应均为 `application/json`
> 文档版本: v1.0.0

---

## 认证说明

> ⚠️ 当前版本暂未实现 JWT 认证机制，所有接口均可公开访问。
>
> 下表标注了**推荐的权限策略**，便于后续接入认证系统时参考：

| 标识 | 含义 |
|---|---|
| 🔓 公开 | 无需登录即可调用 |
| 🔒 JWT | 需在请求头携带 `Authorization: Bearer <token>` |

---

## 目录

- [通用约定](#通用约定)
  - [枚举值](#枚举值)
  - [收费与容量配置](#收费与容量配置)
  - [通用错误码](#通用错误码)
  - [分页参数](#分页参数)
- [1. 客户管理](#1-客户管理)
- [2. 宠物档案](#2-宠物档案)
- [3. 寄养订单](#3-寄养订单)
- [4. 候补队列](#4-候补队列)
- [5. 收费结算](#5-收费结算)

---

## 通用约定

### 枚举值

#### CageType 笼位类型

| 值 | 含义 | 日费 |
|---|---|---|
| `standard` | 标准笼 | ¥80/天 |
| `luxury` | 豪华间 | ¥150/天 |

#### OrderStatus 订单状态

| 值 | 含义 |
|---|---|
| `reserved` | 已预约 |
| `checked_in` | 已入住 |
| `checked_out` | 已离店 |

### 收费与容量配置

| 配置项 | standard | luxury |
|---|---|---|
| 单日费用 | ¥80 | ¥150 |
| 同时段最大容纳订单数 | 2 | 1 |

### 通用错误码

| HTTP 状态码 | 说明 |
|---|---|
| `200 OK` | 请求成功 |
| `201 Created` | 创建成功 |
| `204 No Content` | 删除/操作成功，无返回体 |
| `400 Bad Request` | 参数校验失败（手机号重复、时间冲突、笼位已满等） |
| `404 Not Found` | 资源不存在（客户、宠物、订单、账单、候补记录） |
| `422 Unprocessable Entity` | 请求体格式错误（字段缺失、类型不匹配） |

### 分页参数

所有列表接口统一支持以下 Query 参数：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `skip` | int | `0` | 跳过前 N 条 |
| `limit` | int | `100` | 最多返回 N 条 |

---

## 1. 客户管理

所有路径前缀：`/customers`

### 数据结构

#### CustomerCreate 请求体

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | ✅ | 客户姓名，最大 50 字符 |
| `phone` | string | ✅ | 手机号，最大 20 字符，全局唯一 |
| `emergency_contact` | string | ❌ | 紧急联系人电话，最大 20 字符 |

#### CustomerUpdate 请求体

所有字段可选，未传字段不更新。

| 字段 | 类型 | 说明 |
|---|---|---|
| `name` | string | 客户姓名 |
| `phone` | string | 手机号（唯一校验） |
| `emergency_contact` | string | 紧急联系人 |

#### CustomerOut 响应

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | int | 客户 ID |
| `name` | string | 姓名 |
| `phone` | string | 手机号 |
| `emergency_contact` | string \| null | 紧急联系人 |

---

### 1.1 新增客户

| 项目 | 内容 |
|---|---|
| **路径** | `POST /customers/` |
| **权限** | 🔒 JWT |
| **状态码** | `201 Created` |

**请求体**：`CustomerCreate`

**响应**：`CustomerOut`

**可能的 400 错误**：
- `该手机号已注册`

---

### 1.2 客户列表

| 项目 | 内容 |
|---|---|
| **路径** | `GET /customers/` |
| **权限** | 🔒 JWT |
| **状态码** | `200 OK` |

**Query 参数**：

| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `skip` | int | 0 | 分页偏移 |
| `limit` | int | 100 | 每页数量 |

**响应**：`CustomerOut[]`

---

### 1.3 客户详情

| 项目 | 内容 |
|---|---|
| **路径** | `GET /customers/{customer_id}` |
| **权限** | 🔒 JWT |
| **状态码** | `200 OK` |

**路径参数**：

| 参数 | 类型 | 说明 |
|---|---|---|
| `customer_id` | int | 客户 ID |

**响应**：`CustomerOut`

**可能的 404 错误**：
- `客户不存在`

---

### 1.4 更新客户

| 项目 | 内容 |
|---|---|
| **路径** | `PUT /customers/{customer_id}` |
| **权限** | 🔒 JWT |
| **状态码** | `200 OK` |

**路径参数**：`customer_id` (int)

**请求体**：`CustomerUpdate`

**响应**：`CustomerOut`

**可能的错误**：
- `404` `客户不存在`
- `400` `该手机号已注册`

---

### 1.5 删除客户

| 项目 | 内容 |
|---|---|
| **路径** | `DELETE /customers/{customer_id}` |
| **权限** | 🔒 JWT |
| **状态码** | `204 No Content` |

**路径参数**：`customer_id` (int)

**可能的 404 错误**：
- `客户不存在`

---

## 2. 宠物档案

所有路径前缀：`/pets`

### 数据结构

#### PetCreate 请求体

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | ✅ | 宠物名，最大 50 字符 |
| `breed` | string | ❌ | 品种，最大 100 字符 |
| `weight` | float | ❌ | 体重（kg） |
| `vaccination_status` | string | ❌ | 疫苗情况，最大 200 字符 |
| `allergies` | string | ❌ | 过敏信息，最大 200 字符 |
| `owner_id` | int | ✅ | 所属主人（客户）ID |

#### PetUpdate 请求体

所有字段可选。

| 字段 | 类型 | 说明 |
|---|---|---|
| `name` | string | 宠物名 |
| `breed` | string | 品种 |
| `weight` | float | 体重 |
| `vaccination_status` | string | 疫苗情况 |
| `allergies` | string | 过敏信息 |
| `owner_id` | int | 所属主人 ID |

#### PetOut 响应

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | int | 宠物 ID |
| `name` | string | 宠物名 |
| `breed` | string \| null | 品种 |
| `weight` | float \| null | 体重 |
| `vaccination_status` | string \| null | 疫苗情况 |
| `allergies` | string \| null | 过敏信息 |
| `owner_id` | int | 所属客户 ID |

---

### 2.1 新增宠物

| 项目 | 内容 |
|---|---|
| **路径** | `POST /pets/` |
| **权限** | 🔒 JWT |
| **状态码** | `201 Created` |

**请求体**：`PetCreate`

**响应**：`PetOut`

**可能的 404 错误**：
- `主人不存在`

---

### 2.2 宠物列表

| 项目 | 内容 |
|---|---|
| **路径** | `GET /pets/` |
| **权限** | 🔒 JWT |
| **状态码** | `200 OK` |

**Query 参数**：

| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `skip` | int | 0 | 分页偏移 |
| `limit` | int | 100 | 每页数量 |
| `owner_id` | int | — | 按主人筛选（可选） |

**响应**：`PetOut[]`

---

### 2.3 宠物详情

| 项目 | 内容 |
|---|---|
| **路径** | `GET /pets/{pet_id}` |
| **权限** | 🔒 JWT |
| **状态码** | `200 OK` |

**响应**：`PetOut`

**可能的 404 错误**：
- `宠物不存在`

---

### 2.4 更新宠物

| 项目 | 内容 |
|---|---|
| **路径** | `PUT /pets/{pet_id}` |
| **权限** | 🔒 JWT |
| **状态码** | `200 OK` |

**请求体**：`PetUpdate`

**响应**：`PetOut`

**可能的错误**：
- `404` `宠物不存在`
- `404` `主人不存在`（改 owner_id 时）

---

### 2.5 删除宠物

| 项目 | 内容 |
|---|---|
| **路径** | `DELETE /pets/{pet_id}` |
| **权限** | 🔒 JWT |
| **状态码** | `204 No Content` |

**可能的 404 错误**：
- `宠物不存在`

---

## 3. 寄养订单

所有路径前缀：`/orders`

### 数据结构

#### OrderCreate 请求体

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `pet_id` | int | ✅ | — | 宠物 ID |
| `cage_type` | CageType | ❌ | `standard` | `standard` 或 `luxury` |
| `check_in` | datetime | ✅ | — | 入住时间 ISO 8601 |
| `check_out` | datetime | ❌ | null | 离店时间 ISO 8601（离店时自动生成账单，候补时必填） |
| `status` | OrderStatus | ❌ | `reserved` | 订单状态 |

#### OrderUpdate 请求体

所有字段可选。

| 字段 | 类型 | 说明 |
|---|---|---|
| `cage_type` | CageType | 笼位类型 |
| `check_in` | datetime | 入住时间 |
| `check_out` | datetime | 离店时间 |
| `status` | OrderStatus | 状态（改为 checked_out 且有 check_out 时自动生成账单） |

#### OrderOut 响应

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | int | 订单 ID |
| `pet_id` | int | 宠物 ID |
| `cage_type` | CageType | 笼位类型 |
| `check_in` | datetime | 入住时间 |
| `check_out` | datetime \| null | 离店时间 |
| `status` | OrderStatus | 订单状态 |

#### OrderCreateResult 创建订单响应

笼位有空时返回 order，满员时自动加入候补返回 waitlist。

| 字段 | 类型 | 说明 |
|---|---|---|
| `order` | OrderOut \| null | 创建成功时为订单，满员为 null |
| `waitlist` | WaitlistOut \| null | 满员自动入候补时为候补记录，否则 null |
| `message` | string | 结果描述 |

---

### 3.1 创建订单（或自动入候补）

| 项目 | 内容 |
|---|---|
| **路径** | `POST /orders/` |
| **权限** | 🔒 JWT |
| **状态码** | `201 Created` |

**请求体**：`OrderCreate`

**响应**：`OrderCreateResult`

**业务逻辑**：
1. 校验宠物是否存在、时间是否合法
2. 校验该宠物同时段是否已有其他未离店订单
3. 查询所选笼位类型在该时段的占用数
4. **有空闲** → 创建订单，状态为 `checked_out` 且有离店时间时自动生成账单
5. **已满员** → 自动加入候补队列（需提供离店时间），返回候补记录

**可能的 400 错误**：
- `宠物不存在`
- `离店时间必须晚于入住时间`
- `该宠物该时段已有预约`
- `笼位已满，加入候补需提供离店时间`

---

### 3.2 订单列表

| 项目 | 内容 |
|---|---|
| **路径** | `GET /orders/` |
| **权限** | 🔒 JWT |
| **状态码** | `200 OK` |

**Query 参数**：

| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `skip` | int | 0 | 分页偏移 |
| `limit` | int | 100 | 每页数量 |
| `status` | OrderStatus | — | 按状态筛选（可选） |
| `pet_id` | int | — | 按宠物筛选（可选） |

**响应**：`OrderOut[]`

---

### 3.3 查询某日在住宠物

| 项目 | 内容 |
|---|---|
| **路径** | `GET /orders/staying` |
| **权限** | 🔒 JWT |
| **状态码** | `200 OK` |

**Query 参数**：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `date` | date (YYYY-MM-DD) | ✅ | 查询日期，例如 `2026-06-23` |

**响应**：`OrderOut[]`（所有 `status=checked_in` 且入住时间 ≤ 当日的订单）

---

### 3.4 订单详情

| 项目 | 内容 |
|---|---|
| **路径** | `GET /orders/{order_id}` |
| **权限** | 🔒 JWT |
| **状态码** | `200 OK` |

**响应**：`OrderOut`

**可能的 404 错误**：
- `订单不存在`

---

### 3.5 更新订单

| 项目 | 内容 |
|---|---|
| **路径** | `PUT /orders/{order_id}` |
| **权限** | 🔒 JWT |
| **状态码** | `200 OK` |

**请求体**：`OrderUpdate`

**响应**：`OrderOut`

**业务逻辑**：
- 校验笼位是否仍有容量（排除自身）
- 校验该宠物是否有时间冲突（排除自身）
- 若将状态改为 `checked_out` 且有离店时间，自动生成账单（如尚未生成）

**可能的错误**：
- `404` `订单不存在`
- `400` `离店时间必须晚于入住时间`
- `400` `该宠物该时段已有预约`
- `400` `该时段所选笼位已满`

---

### 3.6 取消/删除订单（触发候补递补）

| 项目 | 内容 |
|---|---|
| **路径** | `DELETE /orders/{order_id}` |
| **权限** | 🔒 JWT |
| **状态码** | `204 No Content` |

**业务逻辑**：
1. 删除目标订单
2. 查找该笼位类型、该时段的候补队列
3. 按 `created_at` 升序依次尝试递补：
   - 该候补宠物在候补时段已有其他订单 → **跳过，保留在候补中**
   - 无冲突 → 转为正式订单，从候补队列移除
4. 只递补 1 个（与被取消订单等量替换）

**可能的 404 错误**：
- `订单不存在`

---

## 4. 候补队列

所有路径前缀：`/orders/waitlist`（归属寄养订单模块）

### 数据结构

#### WaitlistCreate 请求体

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `pet_id` | int | ✅ | 宠物 ID |
| `cage_type` | CageType | ✅ | 期望的笼位类型 |
| `check_in` | datetime | ✅ | 期望入住时间 |
| `check_out` | datetime | ✅ | 期望离店时间 |

#### WaitlistOut 响应

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | int | 候补记录 ID |
| `pet_id` | int | 宠物 ID |
| `cage_type` | CageType | 笼位类型 |
| `check_in` | datetime | 期望入住时间 |
| `check_out` | datetime | 期望离店时间 |
| `created_at` | datetime | 入队时间（决定排队顺序） |

#### WaitlistPosition 排队位置响应

| 字段 | 类型 | 说明 |
|---|---|---|
| `waitlist_id` | int | 候补记录 ID |
| `pet_id` | int | 宠物 ID |
| `position` | int | 当前排队位置（从 1 开始） |
| `cage_type` | CageType | 笼位类型 |
| `check_in` | datetime | 期望入住时间 |
| `check_out` | datetime | 期望离店时间 |

---

### 4.1 加入候补队列

| 项目 | 内容 |
|---|---|
| **路径** | `POST /orders/waitlist` |
| **权限** | 🔒 JWT |
| **状态码** | `201 Created` |

**请求体**：`WaitlistCreate`

**响应**：`WaitlistOut`

**可能的 400 错误**：
- `宠物不存在`
- `离店时间必须晚于入住时间`
- `该宠物该时段已有预约`

---

### 4.2 候补列表

| 项目 | 内容 |
|---|---|
| **路径** | `GET /orders/waitlist` |
| **权限** | 🔒 JWT |
| **状态码** | `200 OK` |

**Query 参数**：

| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `cage_type` | CageType | — | 按笼位类型筛选（可选） |

**响应**：`WaitlistOut[]`（按 `created_at` 升序，即排队顺序）

---

### 4.3 查询排队位置

| 项目 | 内容 |
|---|---|
| **路径** | `GET /orders/waitlist/{waitlist_id}/position` |
| **权限** | 🔓 公开 / 🔒 JWT（推荐） |
| **状态码** | `200 OK` |

**路径参数**：`waitlist_id` (int)

**响应**：`WaitlistPosition`

> **说明**：`position` 按「同一笼位类型 + 时间重叠 + 入队时间更早或相等」的候补记录数计算，同宠物重复候补会被递补时去重跳过。

**可能的 404 错误**：
- `候补记录不存在`

---

### 4.4 退出候补队列

| 项目 | 内容 |
|---|---|
| **路径** | `DELETE /orders/waitlist/{waitlist_id}` |
| **权限** | 🔒 JWT |
| **状态码** | `204 No Content` |

**可能的 404 错误**：
- `候补记录不存在`

---

## 5. 收费结算

所有路径前缀：`/billing`

### 数据结构

#### BillingOut 响应

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | int | 账单 ID |
| `order_id` | int | 关联订单 ID（唯一） |
| `days` | int | 计费天数（最少 1 天） |
| `total_amount` | float | 总金额（元） |
| `is_paid` | bool | 是否已付款 |

#### BillingUpdate 请求体

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `is_paid` | bool | ❌ | 标记是否已付款 |

#### MonthlyRevenue 月度营收汇总

| 字段 | 类型 | 说明 |
|---|---|---|
| `year` | int | 年份 |
| `month` | int | 月份（1-12） |
| `total_amount` | float | 总营收 |
| `paid_amount` | float | 已收金额 |
| `unpaid_amount` | float | 未收金额 |
| `order_count` | int | 已离店订单数 |

---

### 5.1 账单列表

| 项目 | 内容 |
|---|---|
| **路径** | `GET /billing/` |
| **权限** | 🔒 JWT |
| **状态码** | `200 OK` |

**Query 参数**：

| 参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `skip` | int | 0 | 分页偏移 |
| `limit` | int | 100 | 每页数量 |
| `is_paid` | bool | — | 按付款状态筛选（可选） |

**响应**：`BillingOut[]`

---

### 5.2 月度营收汇总

| 项目 | 内容 |
|---|---|
| **路径** | `GET /billing/monthly-summary` |
| **权限** | 🔒 JWT |
| **状态码** | `200 OK` |

**Query 参数**：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `year` | int | ✅ | 年份，如 `2026` |
| `month` | int | ✅ | 月份，1-12 |

**响应**：`MonthlyRevenue`

> **说明**：统计口径为「该月内已离店（check_out 在该月）」的订单，按离店时间归属月份。

---

### 5.3 按订单查账单

| 项目 | 内容 |
|---|---|
| **路径** | `GET /billing/order/{order_id}` |
| **权限** | 🔒 JWT |
| **状态码** | `200 OK` |

**路径参数**：`order_id` (int)

**响应**：`BillingOut`

**可能的 404 错误**：
- `该订单暂无账单`（订单未离店时不会生成账单）

---

### 5.4 账单详情

| 项目 | 内容 |
|---|---|
| **路径** | `GET /billing/{billing_id}` |
| **权限** | 🔒 JWT |
| **状态码** | `200 OK` |

**响应**：`BillingOut`

**可能的 404 错误**：
- `账单不存在`

---

### 5.5 更新账单（标记已付款等）

| 项目 | 内容 |
|---|---|
| **路径** | `PUT /billing/{billing_id}` |
| **权限** | 🔒 JWT |
| **状态码** | `200 OK` |

**请求体**：`BillingUpdate`

**响应**：`BillingOut`

**可能的 404 错误**：
- `账单不存在`

---

## 附录：计费规则

账单在以下场景自动生成：
- 创建订单时 `status=checked_out` 且 `check_out` 已设置
- 更新订单时将状态改为 `checked_out` 且 `check_out` 已设置（如账单尚未生成）

计费公式：
```
天数 = max(1, check_out.date - check_in.date)
金额 = 笼位日费 × 天数
```

| 笼位 | 日费 |
|---|---|
| standard | ¥80 |
| luxury | ¥150 |
