# Building Effective Agents — 学习笔记

> **Source**: [Anthropic Engineering — Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) (Erik Schluntz & Barry Zhang, Dec 19, 2024)
> **Phase**: Phase 0 必读
> **下次重读**: Phase 5(深度视角)
> **Core thesis**: Success isn't about building the most sophisticated system — it's about building the right system. Start simple, add complexity only when justified.

---

## 目录

1. [The Three Layers of Agentic Systems](#1-the-three-layers-of-agentic-systems)
2. [How to Choose (Decision Framework)](#2-how-to-choose-decision-framework)
3. [Augmented LLM (Foundational Building Block)](#3-augmented-llm-foundational-building-block)
4. [Workflow → 五种核心模式](#4-workflow--五种核心模式)
5. [Agent → 自主开放任务](#5-agent--自主开放任务)
6. [Key Takeaways](#6-key-takeaways)
7. [两个高价值应用领域](#7-两个高价值应用领域)
8. [辅助理解:披萨店故事](#8-辅助理解披萨店故事)
9. [Interview Q&A](#9-interview-qa)
10. [How this connects to NomNom](#10-how-this-connects-to-nomnom)

---

## 1. The Three Layers of Agentic Systems

"Agentic system" 是一个伞状术语,涵盖从增强单次调用到完全自主 agent 的所有形式。三层,复杂度递增:

| Layer | Essence | Control |
|---|---|---|
| **Augmented LLM** | Enhanced single LLM call | Fully developer-controlled |
| **Workflow** | Multiple LLM calls along predefined code paths | Path hardcoded in advance |
| **Agent** | LLM plans, uses tools, and loops autonomously | LLM makes dynamic decisions |

### Key distinction (Workflow vs Agent)

- **Workflow**: Path is written into code by the developer → **LLM 是执行者**
- **Agent**: Path is decided by the LLM itself → **LLM 是决策者**

---

## 2. How to Choose (Decision Framework)

### Core Principle

> Start with the simplest solution; add complexity only when it demonstrably improves outcomes.

### Increasing Complexity Ladder

```
Single LLM call → Augmented LLM → Workflow → Single Agent → Multi-Agent
   (simplest)                                                (most complex)
```

每升一级:
- ⬆️ More latency
- ⬆️ More cost
- ⬆️ Harder debugging
- ⬆️ Higher error risk(agents 尤其严重 —— compounding errors)
- ⬇️ Less predictability

### Selection Guide

| Scenario | Recommended approach |
|---|---|
| 任务定义清晰、单次完成 | Single LLM call + prompt engineering |
| 需要外部知识 / 工具 / 记忆 | Augmented LLM |
| 任务能拆成固定步骤 | Workflow |
| 任务开放、步数无法预测 | Agent |

---

## 3. Augmented LLM (Foundational Building Block)

### 定义

```
Augmented LLM = LLM + Retrieval + Tools + Memory
```

### 三种增强方式

- **Retrieval** — 模型自己生成搜索 query 来拉外部知识
- **Tools** — 模型自主选择和调用工具/API
- **Memory** — 模型决定保留什么供以后使用

### Implementation

可以用 Model Context Protocol (MCP) 接入越来越大的第三方工具生态。

### 关键强调

重点不是加了多少增强,而是:
1. 是否针对你的具体用例做了**定制**
2. LLM 是否有**清晰、文档化的接口**去用它们

---

## 4. Workflow → 五种核心模式

预测性 & 一致性 —— 适用于定义良好的任务。

### 4.1 Prompt Chaining(流水线)

- **定义**:把任务拆成顺序步骤;每次 LLM 调用处理上一步的输出;可选的程序化"gate"检查中间结果
- **何时用**:任务能干净地拆成固定子任务;用延迟换准确度
- **例子**:
  - 写营销文案 → 翻译成另一种语言
  - 写大纲 → 验证大纲 → 写完整文档

### 4.2 Routing(分类分发)

- **定义**:对输入分类,导向专门的后续流程
- **何时用**:不同类别需要分开处理,而且分类可以做得准(LLM 或传统分类器)
- **例子**:
  - 客服分流(一般/退款/技术)
  - 简单问题 → Haiku,难问题 → Sonnet(成本优化)

### 4.3 Parallelization(并行)

- **定义**:多个 LLM 调用同时跑,程序化汇总输出
- **两种变体**:
  - **Sectioning**:把任务拆成独立子任务并行
  - **Voting**:同一任务跑多次,获得多样输出
- **何时用**:子任务可以并行加速,或多视角能提升置信度
- **例子**:
  - Sectioning:一个模型处理 query,另一个筛查不当内容
  - Voting:多个 prompt 从不同角度审查代码漏洞

### 4.4 Orchestrator-Workers(经理 + 员工)

- **定义**:一个中央 LLM 动态拆任务,委派给 worker LLM,综合结果
- **与 Parallelization 的关键区别**:子任务**不是预定义的** —— orchestrator 根据具体输入决定
- **何时用**:你无法提前预测子任务
- **例子**:
  - 编码任务,文件改动的数量/性质取决于请求
  - 搜索任务,从多个来源收集信息

### 4.5 Evaluator-Optimizer(作者 + 编辑)

- **定义**:一个 LLM 生成响应,另一个评估并提供反馈,循环
- **何时用**:有明确评估标准 **且** 迭代改进能带来可衡量价值
- **两个适用信号**:
  1. 人类反馈能明显改进 LLM 响应
  2. LLM 自己也能产生类似反馈
- **例子**:
  - 文学翻译 —— 捕捉初次翻译漏掉的细微之处
  - 复杂搜索 —— evaluator 判断是否值得继续搜

### Workflow 速查表

| Pattern | 核心特征 | 典型用例 |
|---|---|---|
| Prompt Chaining | 顺序、固定步骤 | 大纲 → 写作 |
| Routing | 分类后分发 | 客服分流 |
| Parallelization | 并发调用 | 护栏 + 主响应 |
| Orchestrator-Workers | 动态拆分任务 | 多文件代码改动 |
| Evaluator-Optimizer | 生成-评估循环 | 翻译润色 |

---

## 5. Agent → 自主开放任务

### 5.1 Characteristics

- 从人类命令或交互对话开始
- 任务明确后,**自主规划和执行**
- 可能在 checkpoint 回来找人要更多信息或判断
- 执行中用环境的"ground truth"(工具结果、代码执行)评估进度
- Checkpoint 或卡住时暂停寻求反馈
- 完成时终止,或触发停止条件(如最大迭代次数)
- **本质**:An LLM using tools in a loop based on environmental feedback

### 5.2 When to Use

- 开放问题,所需步骤无法预测,固定路径无法硬编码
- LLM 可能要操作很多轮 —— 你必须对它的决策有一定信任
- 最适合可信环境下的规模化任务

### 5.3 Trade-offs

| Advantages | Costs |
|---|---|
| 灵活,处理复杂开放任务 | 高成本(多轮调用) |
| 模型驱动决策,可规模化 | Compounding errors |
| 减少硬编码 | 需要沙箱测试和护栏 |

### 5.4 Examples

- **Coding Agent**:解决 SWE-bench 任务 —— 根据任务描述编辑多个文件
- **Computer Use**:参考实现,Claude 操作电脑完成任务

### 5.5 Three Core Implementation Principles ⭐

构建 agent 时:

1. **Simplicity** — agent 设计本身要保持简洁
2. **Transparency** — 显式展示 agent 的规划步骤
3. **ACI(Agent-Computer Interface)** — 通过完善的工具文档和测试精心打磨

> 💡 **额外洞察**:作者在构建 SWE-bench agent 时,**花在优化工具上的时间比 prompt 还多**。Tool engineering 值得和 prompt engineering 同等关注。

---

## 6. Key Takeaways

1. **别默认上 agent** — 大多数应用用一个优化好的单次 LLM 调用 + RAG + few-shot 就够了
2. **Workflow 和 agent 不是替代关系** — 它们是不同复杂度的工具,按需选择
3. **谨慎使用框架** — 先掌握底层 API,再考虑抽象层
4. **通过测量来迭代** — 任何复杂度增加都必须被评估证明合理
5. **Agent ≈ tool loop** — 实现往往简单,难的是工具设计(ACI)和护栏

---

## 7. 两个高价值应用领域

**共同特征**:对话 + 行动、明确成功标准、支持反馈循环、有意义的人类监督

- **客户支持**:对话式 workflow + 工具集成(订单、退款、知识库)。一些公司用"按成功解决付费"的定价 —— 体现了对 agent 效果的信心
- **Coding Agents**:可通过自动化测试验证;问题空间结构良好;输出质量可客观衡量

---

## 8. 辅助理解:披萨店故事

用一个贯穿始终的故事来串这篇文章的所有概念。

### 🍕 场景:开一家 AI 披萨店

想象你要开一家披萨外卖店,客户通过聊天下单。你想用 AI 自动化处理订单。从最简单的方案开始,一步步看什么时候需要升级。

### 第一幕:最朴素的 AI 店员(单次 LLM 调用)

客户发消息说"我要一个玛格丽特披萨"。

你写了个程序:把客户的话扔给 LLM,LLM 回复"好的,30 分钟送到"。

```
客户消息 → LLM → 回复
```

✅ 简单、便宜、快
❌ 但是...LLM 不知道你今天有没有番茄、不知道客户地址、不知道价格

这就是普通的"单次 LLM 调用"。文章说:**很多应用做到这一步就够了。别动不动就上 agent。**

### 第二幕:给店员配点装备(Augmented LLM)🎒

你发现单纯靠 LLM 不行,得给它配点东西:

- 📚 **Retrieval** = 给它一本菜单,它能查"玛格丽特披萨多少钱"
- 🔧 **Tools** = 给它"查库存"按钮、"下订单"按钮
- 🧠 **Memory** = 让它记住"这个客户上次说不要洋葱"

```
客户消息 → LLM(能查菜单 + 能下单 + 能记笔记)→ 回复
```

这就是 **Augmented LLM**。LLM 还是只调用一次,但它"装备升级了"。

> 📌 **类比**:就像普通员工 vs. 配备了 POS 系统、菜单、客户档案的员工。

文章说:这是所有更复杂系统的基础构件。后面无论是 workflow 还是 agent,假设的都是 LLM 已经"装备好了"。

### 第三幕:生意变复杂了,需要流程(Workflow)🏭

订单量大了,各种奇怪需求都来了。

#### 🔗 模式 1: Prompt Chaining(流水线)

客户说:"帮我写一首关于披萨的英文诗,然后翻译成中文。"

你不能让 LLM 一次搞定两件事(效果差)。所以拆成两步:

```
LLM 第 1 次:写英文诗 → LLM 第 2 次:翻译成中文
```

**类比**:像工厂流水线,A 工位做完交给 B 工位。

#### 🚦 模式 2: Routing(分诊台)

客户消息五花八门:
- "我要点餐" → 走点餐流程
- "我的订单到哪了?" → 查订单系统
- "上次的披萨太咸了!" → 走客诉流程

你不能用同一个 prompt 处理所有情况(那 prompt 会臃肿不堪)。所以:

```
              ┌→ 点餐 prompt
客户消息 → 分类器 ┼→ 查单 prompt
              └→ 客诉 prompt
```

**类比**:像医院的分诊台,先判断你该去哪个科,再去看医生。

还有个好处:简单问题用便宜模型(Haiku),难问题用贵模型(Sonnet),省钱。

#### ⚡ 模式 3: Parallelization(分头干 / 投票)

**变体 A — Sectioning(分头干)**:

客户下单的同时,你想:
- 一个 LLM 处理订单
- 另一个 LLM 并行检查这条消息有没有骂人

```
              ┌→ LLM 1:处理订单
客户消息 ──┤
              └→ LLM 2:内容审核
```

**变体 B — Voting(投票)**:

客户问:"你们披萨里有不是清真的成分吗?"

这种问题答错代价很大。所以你让 3 个 LLM 同时回答,3 票里 2 票说"没有"才放行。

```
              ┌→ LLM 1:回答客户问题
客户消息 → ┼→ LLM 2:回答              → 投票决定
              └→ LLM 3:回答
```

**类比**:分头干 = 多个员工各做各的;投票 = 三个员工一起判断,少数服从多数。

#### 👔 模式 4: Orchestrator-Workers(经理 + 员工)

客户说:"帮我策划一个 20 人的生日派对,要披萨、饮料、装饰。"

这件事没法提前知道到底需要几步:
- 可能要查多少种披萨可选
- 可能要算预算
- 可能要安排配送时间

所以你设一个经理 LLM,它自己决定:"先查库存 → 然后算价格 → 然后安排时间"。每一步派一个 worker LLM 去做,最后经理整合结果。

```
              ┌→ Worker 1: 查库存
经理 LLM ─→ ┼→ Worker 2: 算价格       → 经理整合 → 回复
              └→ Worker 3: 排时间
```

**和 Parallelization 的关键区别**:
- Parallelization:你提前写死了要分几路、做什么
- Orchestrator-Workers:**经理 LLM 自己决定**要分几路、做什么

**类比**:Parallelization 像工厂流水线已经设计好了;Orchestrator-Workers 像项目经理临时分派任务。

#### ✍️ 模式 5: Evaluator-Optimizer(作者 + 编辑)

客户说:"帮我把这篇英文菜单文案翻译得有诗意。"

第一次翻译可能很平庸。所以:

```
LLM A(译者):翻译 → LLM B(编辑):评价 → 不够好?→ LLM A 重译 → 直到 B 满意
```

**类比**:像写论文,你写完导师批改,改完再批,改到导师说 OK。

**什么时候用?** 两个条件:
1. 你能说清"什么叫好"(有明确评估标准)
2. LLM 自己也能给出有用的批评

#### 📋 Workflow 五种模式速记

| 模式 | 一句话总结 | 生活类比 |
|---|---|---|
| Prompt Chaining | 流水线,A 做完 B 做 | 工厂装配线 |
| Routing | 先分类再分发 | 医院分诊台 |
| Parallelization | 多人同时干 | 分头办事 / 多人投票 |
| Orchestrator-Workers | 经理临时派活 | 项目经理 + 团队 |
| Evaluator-Optimizer | 写 → 改 → 写 → 改 | 作者 + 编辑 |

**Workflow 的共同点**:路径都是你(开发者)用代码写死的。LLM 只是按你设计的剧本演戏。

### 第四幕:终极店员 —— Agent(自主员工)🤖

某天客户发消息:"你帮我搞一桌适合 5 个素食朋友的晚餐,预算 200 块,2 小时内送到。"

这事儿你没法提前写流程:
- 它可能要先问客户在哪
- 可能要查素食选项
- 可能要算预算分配
- 可能要协调多个商家
- 可能某家店没货,要换方案
- ...到底几步?**不知道!**

这时候你需要一个自主 agent:你给它工具(查菜单、下单、问客户),然后让它自己想办法。

```
任务 → Agent 思考 → 调用工具 → 看结果 → 继续思考 → 调用工具 → ... → 完成
        ↑________________循环________________↓
```

**Agent 的本质**:LLM + 工具 + 循环 + 环境反馈

它就像一个自主员工,你给它任务和工具,然后它自己决定怎么做。

**Agent 的特征**:
1. 从你的命令开始
2. 自己规划、自己执行
3. 每步都看"环境反馈"(工具调用结果)来判断进度
4. 遇到困难可以回来问你
5. 有停止条件(比如最多循环 20 次,防止它发疯)

**Agent 的代价**:
- 💸 贵(循环很多次,token 烧很多)
- 😱 错误会滚雪球(第 3 步错了,第 4 步基于错误继续错)
- 🧪 必须在沙箱里测试,加护栏

**什么时候用 Agent?** 只有当任务真的无法预测步骤,而且你愿意承担成本和风险时。

### 第五幕:逻辑串起来 🧵

**一句话总结**:能简单解决就别复杂化。从单次调用开始,实在不够再升级,Agent 是最后的选择。

**升级阶梯**:

```
任务很简单?
    └→ 单次 LLM 调用 ✅

需要外部知识/工具?
    └→ Augmented LLM ✅

任务能拆成固定步骤?
    └→ Workflow(五种模式选一个)✅

任务步骤完全没法预测?
    └→ 才考虑 Agent ⚠️(代价大)
```

**为什么这个顺序?** 每升一级:
- 💰 成本上升
- 🐌 速度下降
- 🐛 调试变难
- 💥 出错风险增加
- ❓ 可预测性下降

所以默认要保守,需要时才升级。

### 🎯 用披萨店例子检验你的理解

试着回答:
1. 客户问"你们最便宜的披萨是什么?" → 用哪个方案?
2. 客户问"帮我点餐 + 顺便审核我有没有骂人" → 用哪个方案?
3. 客户问"帮我规划一周的素食外卖" → 用哪个方案?
4. 客户问"翻译这首披萨主题的诗,要押韵" → 用哪个方案?

**参考答案**:
1. Augmented LLM(有菜单检索就够了)
2. Parallelization - Sectioning(两件事并行)
3. Agent(步骤无法预测,需要自主规划)
4. Evaluator-Optimizer(翻译 + 评审循环)

---

## 9. Interview Q&A

### 🟢 Level 1: Foundational Understanding

1. What's the difference between a workflow and an agent according to Anthropic's definition?
2. What are the three components that make up an Augmented LLM?
3. The article gives a "complexity ladder" — list the levels from simplest to most complex.
4. What's the article's core principle about when to add complexity?

### 🟡 Level 2: Pattern Recognition

1. For each scenario, name the workflow pattern that best fits and explain why:
   - (a) A customer support system that routes refund requests, technical questions, and general inquiries to different prompts
   - (b) Generating a blog post outline, then writing the full post based on the outline
   - (c) Translating a poem, then having a second LLM critique the translation and suggest improvements
   - (d) Reviewing a piece of code for security vulnerabilities using 5 different prompts focused on different vulnerability types
   - (e) A coding assistant that, given a feature request, decides which files to modify and what changes to make in each
2. What's the key difference between Parallelization (Sectioning) and Orchestrator-Workers? They look similar — what distinguishes them?
3. The article describes two variants of Parallelization. What are they, and when would you use each?

### 🟠 Level 3: Deeper Reasoning

1. Why does the article recommend starting with direct LLM API calls instead of frameworks like LangChain? Give at least two reasons.
2. The article says workflows trade latency for accuracy. Explain how prompt chaining achieves this.
3. The Evaluator-Optimizer pattern has two signs of good fit. What are they, and why does each one matter?
4. Why are agents more prone to compounding errors than workflows? What does this imply for testing?
5. The article emphasizes designing the Agent-Computer Interface (ACI). Why is this so important, and how does it compare to Human-Computer Interface (HCI) design?

### 🔴 Level 4: Application & Synthesis

1. **Scenario**: You're building a system that takes a user's resume and a job description, then produces a tailored cover letter.
   - Would you use a workflow or an agent? Which pattern(s)?
   - Justify your choice using the article's framework.
2. **Scenario**: A startup wants to build an "AI data analyst" that, given a natural language question and access to a database, returns insights with charts.
   - What pattern would you pick?
   - What would the trade-offs be vs. a simpler approach?
3. The article mentions "poka-yoke" your tools. What does this mean, and can you give an example from the article (or invent one) of how this could prevent agent errors?
4. **Critical thinking**: When might an Evaluator-Optimizer loop actually hurt performance instead of helping? What's a failure mode to watch for?

### 🟣 Level 5: ML/MLE Interview-Style Questions

1. If a coding interviewer asked: "How would you design an LLM-based system to automate triaging GitHub issues?" — walk through your reasoning using concepts from this article.
2. **Trade-off question**: You're given a task that could be solved with either an orchestrator-workers workflow or an autonomous agent. What factors would push you toward one or the other?
3. Why do the authors say they spent more time optimizing tools than prompts for the SWE-bench agent? What does this tell us about where the real engineering effort lives in agent development?
4. **Open-ended**: The article was published in Dec 2024. Looking at the patterns described, which do you think will become more vs. less important as models get more capable? Why?

---

## 10. How this connects to NomNom

NomNom 在 10 周里会**走过这篇文章里的好几个阶段**,这是最重要的串联:

| NomNom Phase | 对应的层级 | 用到的模式 |
|---|---|---|
| Phase 1–4 | Augmented LLM | 单次 LLM 调用 + tool use + RAG |
| Phase 5 v3.0(减肥推荐) | Workflow | **Routing**(分类用户意图) + **Prompt Chaining**(提取约束→检索→生成→评估)+ **Evaluator-Optimizer**(候选餐单评估) |
| Phase 5 v3.1(冰箱剩菜) | Single Agent | LLM 自主决定调用工具顺序 |
| Phase 5 副线项目 `tech_comparison_agent` | Multi-Agent (Orchestrator-Workers) | 仅为面试准备,NomNom 本身不需要 |
| **NomNom 永远不会用 multi-agent** | —— | 因为它不需要,这是核心教训 |

### 关键具体对应

**Routing 出现的地方**:NomNom v3.0 开头有一步 routing —— "用户问的是'我吃了什么'还是'我应该吃什么'?",分到不同 pipeline。读到 Routing 那一节时就该认出这个对应关系。

**Evaluator-Optimizer 出现的地方**:NomNom v3.0 里的"evaluator 检查每个候选餐单是否真的满足约束"就是这个模式。

**Workflow vs Agent 决策框架**:Phase 5 你要写的 `workflow_vs_agent_decision.md` 就是这篇文章核心思想的具象化。

### 面试金句

> "Don't build agents when a workflow will do. Don't build multi-agent when a single agent will do."

记住这句话。面试里被问到"什么时候不该用 multi-agent"时,这是开场白。
