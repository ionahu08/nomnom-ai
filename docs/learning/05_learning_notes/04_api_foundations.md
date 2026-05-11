# API 基础理解笔记

> 整理自 Phase 0 学习过程中的对话讨论
> 目的：建立 LLM 工程师必备的 API 基础认知

---

## 目录

1. [API 是什么](#1-api-是什么)
2. [API key 和 token](#2-api-key-和-token)
3. [SDK 是什么](#3-sdk-是什么)
4. [两种 API 视角：消费者 vs 提供者](#4-两种-api-视角消费者-vs-提供者)
5. [现代软件工程的真相](#5-现代软件工程的真相)
6. [Claude Code vs API：彻底分清楚](#6-claude-code-vs-api彻底分清楚)
7. [LLM API 出现前后的世界](#7-llm-api-出现前后的世界)
8. [NomNom 在每个 Phase 的代码形态](#8-nomnom-在每个-phase-的代码形态)
9. [核心要点速查](#9-核心要点速查)

---

## 1. API 是什么

### 定义

**API 是别人家服务的"门"，你写代码敲这扇门，就能用他们的服务。**

API 全称 Application Programming Interface（应用程序接口），但记住"门"这个比喻就够了。

### 生活类比：星巴克买咖啡

去星巴克买咖啡：
- **柜台** = API（标准化的接口）
- **"我要大杯拿铁"** = 请求（request）
- **付钱** = 认证（authentication）
- **拿到咖啡** = 响应（response）

你不需要知道咖啡豆从哪进的、咖啡机怎么工作。**你只通过柜台这个标准化接口和星巴克打交道**。

### 调 API 时发生了什么

你的代码写：
```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    messages=[{"role": "user", "content": "你好"}]
)
```

背后发生：
1. 你的电脑通过**互联网**把请求发到 Anthropic 服务器
2. Anthropic 服务器让 Claude 处理
3. Claude 生成回答
4. 服务器把回答**通过互联网**传回你的电脑
5. 你的代码收到回答

整个过程几秒钟。**你的代码 = 星巴克顾客，Anthropic 服务器 = 柜台，Claude = 后厨**。

### 类比 ML 经验

如果你之前做 ML，你习惯了：
- 有一个模型文件 `.pkl` 或 `.pt`
- 用 `model.predict(x)` 调用
- 跑在你自己的机器上

**LLM 时代不一样**：
- 你**没有**模型文件——Claude 太大了，跑在 Anthropic 服务器上
- 你**只能通过 API 调用**——像调用一个远程函数
- `client.messages.create(...)` 本质上 = 远程的 `model.predict(...)`

**记住：API 调用 = 远程的 model.predict()**

---

## 2. API key 和 token

### API key

**API key 是你的身份证 + 信用卡的合体**。

一串长字符串，类似：
```
sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

每次代码"敲门"时必须带上这把 key，Anthropic 才知道：
1. 是谁在敲门（不然怎么收钱？）
2. 往谁的账上记

**API key 绝对不能泄露**。泄露 = 把信用卡给了别人。这就是为什么：
- 存在 `.env` 文件里
- `.gitignore` 必须排除 `.env`
- **永远不要把 `.env` 提交到 GitHub**

### Token

**token 是 Anthropic 计算用量的单位**，类似"咖啡的盎司数"。

| 维度 | 描述 |
|---|---|
| 输入 token | 你发给 Anthropic 的内容（按输入价格收费） |
| 输出 token | Claude 回给你的内容（按输出价格收费） |

**一个 token 大概等于**：
- 英文：约 3/4 个单词（"hello" = 1 token，"unbelievable" ≈ 3 tokens）
- 中文：约 1 个汉字 = 1-2 tokens

**例子**：
- 发送 "今天天气怎么样？" → 约 10 tokens
- Claude 回 "今天北京晴，25 度" → 约 12 tokens
- 总共 22 tokens，Sonnet 价格大约 $0.0001（不到一分钱）

### 为什么 token 概念重要

**你的账单 = 累积 token 数 × 价格**

调用 API 千万次让账单失控，主要原因就是 token 没控制好。这也是为什么 Phase 4 要专门学：
- **Prompt caching**（缓存重复的 token）
- **模型分层**（简单任务用便宜的 Haiku，省 token 钱）

---

## 3. SDK 是什么

### 定义

**SDK = 官方为某个 API 提供的"傻瓜化封装"包，让调用更方便。**

SDK 全称 Software Development Kit。

### 对比：有 SDK vs 没 SDK

**没有 SDK 的世界**（原始 HTTP 请求）：

```python
import requests
import json

response = requests.post(
    "https://api.anthropic.com/v1/messages",
    headers={
        "x-api-key": "sk-ant-xxxxx",
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    },
    data=json.dumps({
        "model": "claude-sonnet-4-6",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": "你好"}]
    })
)

result = json.loads(response.text)
text = result["content"][0]["text"]
```

**有 SDK 的世界**（用 `anthropic` 包）：

```python
from anthropic import Anthropic

client = Anthropic()  # 自动从环境变量读 key
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "你好"}]
)
text = response.content[0].text
```

少了一半代码，逻辑清楚，不容易写错。**这个 `anthropic` 包就是 Anthropic 的 SDK**。

### 类比

- **API 是星巴克的柜台**（你能买咖啡的接口）
- **SDK 是有人帮你写好的"自动点单器"**（按个按钮就帮你下单）

### 常见的 SDK

每个有 API 的服务通常都提供 SDK：

| 服务 | Python SDK |
|---|---|
| Anthropic API | `anthropic` |
| OpenAI API | `openai` |
| AWS API | `boto3` |
| Stripe API | `stripe` |
| Google Cloud | `google-cloud-*` |

### 两个不要搞混的 Anthropic SDK

| 名字 | 用途 | 何时学 |
|---|---|---|
| `anthropic` SDK | **基础包**，调用 Claude 模型 | Phase 1 Day 1 |
| Claude Agent SDK | **高级包**，建 agent 用的封装 | Phase 6 |

两个都叫 SDK，但解决的问题不同——一个解决"怎么调模型"，一个解决"怎么建 agent"。

---

## 4. 两种 API 视角：消费者 vs 提供者

### 关键洞察

"API" 这个词被用得很乱。它其实有两种**完全不同**的含义：

#### 含义 A：调用别人的 API（消费者视角）

你的代码写 `client.messages.create(...)`，**调用 Anthropic 提供的 API**。

- 你的角色：**API 消费者**（API consumer）
- 你的电脑发请求出去，别人的服务器返回结果
- **API 是别人的，你是用户**

#### 含义 B：提供自己的 API（生产者视角）

你写代码**让你的服务器变成一个被别人调用的"门"**。

- 你的角色：**API 提供者**（API provider）
- 别人的电脑发请求过来，**你的服务器返回结果**

### 真实 App 通常同时是两者

完整的 NomNom 架构：

```
   Iona 的手机（NomNom 客户端）
          │
          │ 1. 调用"你的 API"
          ▼
   ┌──────────────────────────┐
   │  你的 NomNom 服务器       │
   │  （Python 代码跑在云上）   │
   │                           │
   │   收到请求 → 处理 →       │
   │   2. 调 Anthropic API     │  ← 这里你是"消费者"
   │      让 Claude 识别食物    │
   │                           │
   │   ← 拿到结果 ← 返回 Iona  │  ← 这里你是"提供者"
   └──────────────────────────┘
          ▲
          │ 3. Claude 给你结果
          │
   ┌──────────────────────────┐
   │  Anthropic 服务器         │
   │  （Claude 跑在这里）       │
   └──────────────────────────┘
```

**你既是提供者也是消费者**。你提供 NomNom API 给 Iona 用，同时在内部消费 Anthropic API 完成任务。

### 代码风格的对比

| | 消费者代码（你调别人） | 提供者代码（你被别人调） |
|---|---|---|
| **关键代码长什么样** | `response = api.create(...)` | `@app.post("/endpoint")` |
| **谁主动？** | 你主动发请求 | 你被动等请求来 |
| **代码做什么** | 构造请求 → 等待响应 → 处理结果 | 等请求 → 处理 → 返回响应 |
| **代码住在哪** | 任何地方（手机、电脑、服务器都行） | 永远住在服务器上 |
| **典型工具** | `requests`、SDK（如 `anthropic`） | Web 框架（FastAPI、Flask、Express） |

**最直观的区分**：
- 看到 `client.create(...)` 或 `requests.post(...)` → **你在调别人的 API**
- 看到 `@app.post(...)` 或 `@app.get(...)` → **你在提供你的 API**

### 消费者代码示例

跑在 Iona 手机上、或者你电脑上的客户端代码：

```python
import requests

response = requests.post(
    "https://api.nomnom.com/analyze-food",   # ← API 地址
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json={
        "image_base64": photo_data,
        "user_goal": "weight_loss"
    }
)

result = response.json()
```

### 提供者代码示例

跑在你的服务器上的代码：

```python
from fastapi import FastAPI
from anthropic import Anthropic

app = FastAPI()
claude = Anthropic()

@app.post("/analyze-food")   # ← 定义一个"门"
def analyze_food(request):
    image = request.image_base64
    goal = request.user_goal
    
    # 内部调 Anthropic（消费者代码）
    response = claude.messages.create(
        model="claude-sonnet-4-6",
        messages=[{"role": "user", "content": [...]}]
    )
    
    # 返回结果给客户端
    return {
        "food": "番茄炒蛋盖饭",
        "calories": 650,
        "advice": response.content[0].text
    }
```

**这是现代软件的链式结构**——你站在 Anthropic 的肩膀上，再让别人站在你的肩膀上。

---

## 5. 现代软件工程的真相

### 一个深刻的洞察

**真实工作中，90% 的时间程序员在"用 API"，10% 在"提供 API"。**

而这 10% "提供自己 API" 的部分，又是用现成的 Web 框架（FastAPI、Flask、Express）来写——本质上还是站在别人的肩膀上。

### 为什么所有人都在调别人的 API？

铁律：**别造你不需要造的东西**。

为什么 NomNom 不自己训练食物识别模型？
- 训练数据要几十万张图，几年收集
- 训练成本上百万美元
- 训完了还不一定有 Claude 好用

为什么 NomNom 不自己写支付系统？
- 涉及金融合规、银行对接、反欺诈
- Stripe 已经做得近乎完美
- 给 Stripe 付 2.9% 手续费比自己做便宜得多

### App = API 拼接

```
NomNom App = 
    你自己写的业务逻辑（10%）
  + 别人提供的 API 拼接（90%）
        ├── Anthropic API（食物识别 + 营养分析）★ 核心
        ├── AWS S3（图片存储）
        ├── PostgreSQL（数据库）
        ├── Voyage AI API（embedding，RAG 用）
        ├── Stripe（支付）
        └── ...
```

**现代 App 的本质 = 把别人的 API 像乐高一样拼起来，加上你自己的业务逻辑，做出用户想要的产品。**

### "高级"程序员高级在哪？

不是"会写底层"，而是：

1. **会拼**：知道哪些 API 该用、哪些不该用、怎么组合
2. **会判断**：什么时候自己写、什么时候调现成的
3. **会兜底**：API 挂了怎么办、太贵了怎么换、效果不好怎么 fallback
4. **会设计**：自己的 App 要不要也提供 API 给别人用、怎么设计才好用

**LLM 工程师的"高级"特别体现在**：
- 会**设计 prompt**（同样调 API，prompt 不同效果差 10 倍）
- 会**评估**（怎么知道你的 prompt 真的变好了）
- 会**控制成本**（多模型分层、prompt caching、缓存策略）
- 会**做 agent**（让多次 API 调用协作完成复杂任务）

这就是为什么 10 周路线看起来"只是在调 Anthropic API"——但学好了，你就成了能做出 NomNom 这种产品的工程师。

---

## 6. Claude Code vs API：彻底分清楚

### 一个常见误区

> "我用 Claude Code 时从来没写过 API request 啊"

对，因为 **Claude Code 是别人写好的产品，你是用户**。

API request 一直在发生——只是不是你写的，是 Claude Code 这个软件**替你写**的。

### Claude Code 内部发生了什么

你在终端打 `claude`，然后输入"帮我看看这个文件夹结构"。

按下回车的瞬间，Claude Code 偷偷做了这些事：

```python
# 这段代码藏在 Claude Code 内部，你看不见
api_request = {
    "model": "claude-sonnet-4-6",
    "max_tokens": 8000,
    "system": "你是一个编程助手...",
    "messages": [
        {"role": "user", "content": "帮我看看这个文件夹结构"}
    ],
    "tools": [{"name": "bash", ...}, ...]
}

response = anthropic_api.send(api_request, api_key=YOUR_KEY)
```

**你只看到聊天界面**。底层的 API 调用全被 Claude Code 包好了，你看不见。

### 把"产品"和"API"分开

| 你看到的（产品） | 背后发生的（API） | 谁写的 API 代码？ |
|---|---|---|
| Claude.ai 网页聊天 | 调 Anthropic API | Anthropic 自己 |
| Claude Code 终端工具 | 调 Anthropic API | Anthropic 自己 |
| ChatGPT 网页 | 调 OpenAI API | OpenAI 自己 |
| Notion AI | 调 Anthropic API | Notion 公司的工程师 |
| Cursor（AI 代码编辑器） | 调 Anthropic + OpenAI API | Cursor 公司的工程师 |
| **未来的 NomNom App** | **调 Anthropic API** | **你** |

**所有 AI 产品背后都是 API 调用**。区别只是"谁写了那些 API 调用代码"。

### 类比：飞机

- **你现在的位置**：坐飞机的乘客（Claude Code 用户）
- **你的目标**：飞行员（能建产品的工程师）

坐飞机只看到舒服的座位和窗外的云。要成为飞行员，你必须懂引擎、空气动力学、仪表盘。

**坐飞机和开飞机是两个完全不同的视角，需要的知识完全不同。**

### 写 API 调用代码可以用 Claude Code 吗？

**完全可以。这就是你建 NomNom 的真实工作流。**

```
你思考 + 决策 → Claude Code 写代码 → 你 review + 改 → 跑通 → commit
```

**Claude Code 是手，你是脑**。你的脑子懂 API，手才能写出好的 API 代码。

但你必须能看懂它写的每一行。原因：

1. **它会犯错**——用过时的 model 名字、漏了参数、prompt 写得很烂
2. **它需要你做决策**——用 Sonnet 还是 Haiku？max_tokens 设多少？要不要 prompt caching？
3. **它无法替你解释**——面试官问"你这个 API 调用为什么这么设计？"，你不能说"Claude Code 写的我也不知道"

---

## 7. LLM API 出现前后的世界

### 2018 年：建一个营养分析 App 多难

那时候没有 LLM API，小明想做"拍照分析食物"：

**做法 1：自己训练模型**
- 收集 10 万张食物照片，自己打标签
- 用 PyTorch 训练，跑几周
- 把模型放服务器
- 用户拍照 → 调 App API → 服务器跑模型 → 返回结果

**做法 2：调当时的视觉 API（Google Cloud Vision、AWS Rekognition）**

```python
# 2018 年的代码大概长这样
response = google_vision_api.detect_labels(image)
# 返回: ["food", "rice", "chinese cuisine", ...]
```

**但这种 API 不智能**：能告诉你"图里有米饭"，但**没法回答**"这餐多少卡路里"、"对减肥的人合适吗"。

### 2024 年：你的代码

```python
response = anthropic_api.messages.create(
    model="claude-sonnet",
    messages=[
        {"role": "user", "content": [
            food_image,
            "分析这张图：识别食物、估算分量、给出宏量营养素、根据减脂目标给建议"
        ]}
    ]
)
# Claude 一句话搞定上面所有事
```

**一个 API 调用，做完了 2018 年小明做不到的事**。这是 LLM 时代的根本变化。

### API 的形态从未变过

接口形态对比：

**Google Vision API（2018）**：
```python
client = vision.ImageAnnotatorClient()
response = client.label_detection(image=image)
```

**Anthropic API（2024）**：
```python
client = Anthropic()
response = client.messages.create(...)
```

**形态一模一样**：
1. 装 SDK
2. 创建 client（带 API key）
3. 调方法，传参数
4. 拿结果

**API 这个概念从互联网诞生那天就有了**。变的不是 API 的形式，是 API 背后的能力——从"分类器"进化到"通用智能"。

### 更早一点：2010 年的 API

那时候典型的 API：
- **Twitter API**——让代码发推、读时间线
- **Google Maps API**——让代码查地点、画地图
- **Stripe API**——让代码收钱
- **Twilio API**——让代码发短信

形态完全一样。**所以"调 API"是程序员几十年来的日常**，不是 LLM 时代才有的新东西。

---

## 8. NomNom 在每个 Phase 的代码形态

### Phase 1–5：CLI 工具

NomNom 只是你电脑上的脚本。**没有"提供 API"这一层**。

```
你的电脑
   │
   │ 你在终端跑：python nomnom.py photo.jpg
   ▼
nomnom.py
   │
   │ 内部调 Anthropic API（消费者代码）
   ▼
Anthropic 服务器
```

**只有"消费者代码"，没有"提供者代码"**。

### Phase 6：MCP Server

NomNom 第一次变成"被别人调用"的东西。**第一次写"提供者代码"**。

```
Claude Code（或别的 MCP 客户端）
   │
   │ 调用 NomNom MCP server
   ▼
nomnom_mcp_server.py     ← 这里有"提供者代码"
   │
   │ 内部还是调 Anthropic API（消费者代码）
   ▼
Anthropic 服务器
```

代码长这样：

```python
from mcp.server import FastMCP
from anthropic import Anthropic

mcp = FastMCP("nomnom")
claude = Anthropic()

@mcp.tool()   # ← "开门"标记，提供 API
def analyze_food_image(image_path: str) -> dict:
    # 内部调 Anthropic（消费者代码）
    response = claude.messages.create(...)
    return response_to_dict(response)
```

### Roadmap 之后：完整 Web App

如果有一天部署给真实用户：

```python
from fastapi import FastAPI
from anthropic import Anthropic

app = FastAPI()
claude = Anthropic()

@app.post("/analyze-food")   # ← 提供 Web API
def analyze_food(image: UploadFile, goal: str):
    response = claude.messages.create(...)
    return {"food": ..., "calories": ..., "advice": ...}
```

这是 10 周之后的事，**当下不用想**。

---

## 9. 核心要点速查

### Phase 1 之前必须懂的最少知识

**概念层（理解就行，不用记）**：
1. **API 是别人家服务的门**——你的代码敲门，他们的服务给你结果
2. **API key 是身份证 + 信用卡合体**——绝对不能泄露
3. **Token 是计费单位**——发出去和收回来都算钱
4. **每次调 API 都要带 model、max_tokens、messages、key 四样东西**

**操作层（要会做的）**：
1. 拿到 API key（console.anthropic.com）
2. 充值（5-10 美元够 Phase 1 玩）
3. 存 key 到 `.env`，`.gitignore` 排除它
4. `pip install anthropic python-dotenv`
5. 跑 Quickstart

### 不用懂的（先跳过）

这些名词用到时再学：
- HTTP / REST / endpoint / request / response
- JSON 细节（Python 自动处理）
- 异步 / async / await（Phase 3 才用）
- streaming events / WebSocket（Phase 1 副线）
- rate limit / retry / exponential backoff

### API 角色快速判断

| 看到的代码 | 你是什么角色 |
|---|---|
| `client.messages.create(...)` | 消费者（调 Anthropic） |
| `requests.post("https://...")` | 消费者（调 HTTP API） |
| `@app.post("/endpoint")` | 提供者（FastAPI） |
| `@mcp.tool()` | 提供者（MCP server） |

### 工具栈快速判断

| 工具 | 用途 | 何时学 |
|---|---|---|
| Anthropic API | 让代码调用 Claude | Phase 1 Day 1 |
| `anthropic` SDK | 调 Anthropic API 的 Python 包 | Phase 1 Day 1 |
| Claude Code | 终端编程助手 | 一直在用 |
| Claude.ai 网页 | 学习对话用 | 一直在用 |
| FastAPI / Flask | 提供 Web API（写 NomNom 服务端） | 10 周之后 |
| Claude Agent SDK | 高级 agent 工具 | Phase 6 |
| MCP | 标准化的"工具暴露"协议 | Phase 6 |

### 一句话总结

> **你的工作是建 App（像 NomNom）。**
> **建 App = 用 Claude Code 当副驾驶 + 写代码 + 这些代码大量调用别人的 API（特别是 Anthropic API） + 偶尔提供自己的 API。**
> **学好 API 不是学怎么手写 HTTP 请求，而是学怎么驾驭 LLM 这个最重要的新型 API。**
> **这就是 LLM Harnessing 的全部含义。**

---

> 笔记完成时间：Phase 0
> 下一步：开始写 `NomNom_v1_spec.md`
