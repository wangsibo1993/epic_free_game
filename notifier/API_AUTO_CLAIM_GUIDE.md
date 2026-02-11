# 🤖 Epic Games API 自动领取完整指南

## 📋 项目概述

完整的基于 API 的自动领取系统，包含两个核心部分：

### 第一部分：Cookie 管理系统 ✅
- 自动从浏览器提取 Cookie
- Cookie 验证和过期检测
- 自动备份和刷新机制

### 第二部分：API 自动领取系统 🎯
- 使用逆向工程的 API 端点
- 多种领取方法（GraphQL + Order API）
- 完整的反爬虫对策

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────┐
│          Cookie 管理层（第一部分）                │
│  ┌──────────────┐          ┌───────────────┐   │
│  │ 浏览器Cookie │ ────→    │ Cookie验证器  │   │
│  └──────────────┘          └───────────────┘   │
│         │                          │            │
│         └─────────→ cookies.json ←─┘            │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│          API 领取层（第二部分）                  │
│  ┌──────────────┐          ┌───────────────┐   │
│  │ API 检测器   │ ────→    │ 游戏领取器    │   │
│  └──────────────┘          └───────────────┘   │
│         │                          │            │
│    免费游戏列表           领取成功/失败         │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│          反爬虫保护层                            │
│  • 随机延迟 • UA轮换 • 请求频率控制             │
└─────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 前置条件
```bash
# 1. Python 3.7+
python3 --version

# 2. 安装依赖
pip3 install requests --user

# 3. 在 Chrome 中登录 Epic Games
# 访问：https://store.epicgames.com
```

### 一键运行
```bash
# 方式 1：直接运行（使用现有 Cookie）
python3 epic_auto_claimer.py

# 方式 2：先刷新 Cookie 再运行
python3 cookie_manager.py refresh && python3 epic_auto_claimer.py
```

---

## 📖 详细使用

### 第一部分：Cookie 管理

#### 1.1 查看 Cookie 状态
```bash
python3 cookie_manager.py info
```

**输出示例**：
```
📊 Cookie Statistics:
   Total cookies: 24
   Domains: .epicgames.com, .store.epicgames.com

🔑 Critical Cookies:
   ✅ EPIC_SSO: Expires in 25 days
   ✅ EPIC_BEARER_TOKEN: Expires in 25 days
   ✅ EPIC_DEVICE: Expires in 54 days

🔍 Validation:
   ✅ Cookies are valid

💡 Recommendation:
   ✅ Cookies are fresh
   No action needed
```

#### 1.2 刷新 Cookie
```bash
# 确保 Chrome 已完全关闭，然后运行：
python3 cookie_manager.py refresh
```

**刷新流程**：
1. 备份当前 Cookie
2. 从 Chrome/Edge/Brave 提取新 Cookie
3. 验证 Cookie 完整性
4. 保存到 `claimer/data/cookies.json`

#### 1.3 检查是否需要刷新
```bash
python3 cookie_manager.py check
```

**退出码**：
- 0: Cookie 有效，无需刷新
- 1: Cookie 需要刷新

#### 1.4 备份 Cookie
```bash
python3 cookie_manager.py backup
```

备份保存在：`claimer/data/cookies_backup/`

---

### 第二部分：API 自动领取

#### 2.1 基本使用
```bash
python3 epic_auto_claimer.py
```

**执行流程**：
```
1. 加载 Cookie ✅
2. 验证账户信息
3. 获取免费游戏列表
4. 检查每个游戏的拥有状态
5. 尝试领取未拥有的游戏
6. 输出执行结果
```

#### 2.2 输出示例

```
======================================================================
Epic Games Auto Claimer - Full API Implementation
======================================================================

📋 Step 1: Loading cookies...
✅ Loaded 24 cookies

📋 Step 2: Verifying account...
✅ Logged in as: YourName (your@email.com)

📋 Step 3: Fetching free games...
✅ Found 5 free game(s):
   • Eternal Threads
   • 《幽灵行者 2》
   • 纪念碑谷（Monument Valley）
   • 《波坦尼庄园》
   • 剧毒复古套装

📋 Step 4: Claiming games...

[1/5] Processing: Eternal Threads

🎮 Attempting to claim: Eternal Threads
   Namespace: d207fa946cd640b9ba4cbc1e3a986ca7
   Offer ID: a9152a8924cc4e438f0e61106ec02f7d
   🆕 Not owned, proceeding to claim...
   📡 Method 1: GraphQL Mutation...
   ✅ Claimed successfully via GraphQL!
      Order ID: ORDER-123456
      State: COMPLETED

[2/5] Processing: 《幽灵行者 2》
   ✅ Already owned

...

======================================================================
Summary
======================================================================
✅ Claimed: 3
   • Eternal Threads
   • 纪念碑谷（Monument Valley）
   • 《波坦尼庄园》

📦 Already owned: 2
   • 《幽灵行者 2》
   • 剧毒复古套装

======================================================================
```

---

## 🛡️ 反爬虫机制

### 1. 随机延迟
```python
# 游戏之间：3-6 秒
# API 调用之间：0.5-3 秒
# 领取尝试前：1.5-3 秒
```

### 2. User-Agent 轮换
```python
user_agents = [
    'Chrome/132.0.0.0 on macOS',
    'Chrome/131.0.0.0 on macOS',
    'Chrome/132.0.0.0 on Windows',
]
```

### 3. 真实浏览器 Headers
```python
headers = {
    'User-Agent': '...',
    'Sec-Ch-Ua': '...',
    'Sec-Fetch-Site': 'same-site',
    'Referer': 'https://store.epicgames.com/',
    # ... 完整的浏览器 headers
}
```

### 4. Cookie 真实性
- 使用真实浏览器提取的 Cookie
- 包含所有必需的认证 Token
- 保持 Cookie 的原始格式和属性

### 5. 请求频率控制
- 不并发请求
- 顺序处理每个游戏
- 遵守合理的请求间隔

---

## 🔬 API 端点说明

### 已发现并实现的端点：

#### 1. 获取免费游戏列表 ✅
```
GET https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions
参数: locale=zh-CN, country=CN
状态: 完全可用
```

#### 2. GraphQL API ✅
```
POST https://graphql.epicgames.com/graphql
用途:
  - 查询账户信息
  - 检查游戏拥有状态
  - 领取免费游戏（mutation）
状态: 主要领取方法
```

#### 3. Order API 🔬
```
POST https://payment-website-pci.ol.epicgames.com/purchase/order-preview
POST https://payment-website-pci.ol.epicgames.com/purchase/confirm-order
用途: 创建和确认订单
状态: 备用方法
```

---

## 🔍 领取流程详解

### 方法 1：GraphQL Mutation（主要方法）

```graphql
mutation claimFreeCatalogOffer(
    $namespace: String!,
    $offerId: String!,
    $lineOffers: [LineOfferInput!]!
) {
    Purchase {
        freeOrder(
            namespace: $namespace,
            offerId: $offerId,
            lineOffers: $lineOffers
        ) {
            orderId
            orderState
            message
        }
    }
}
```

**变量**：
```json
{
    "namespace": "游戏命名空间",
    "offerId": "优惠ID",
    "lineOffers": [{
        "offerId": "优惠ID",
        "quantity": 1
    }]
}
```

**成功响应**：
```json
{
    "data": {
        "Purchase": {
            "freeOrder": {
                "orderId": "ORDER-123456",
                "orderState": "COMPLETED",
                "message": null
            }
        }
    }
}
```

### 方法 2：Order API（备用方法）

**Step 1: 创建订单预览**
```python
POST /purchase/order-preview
{
    "namespace": "...",
    "offers": ["offer_id"],
    "country": "CN",
    ...
}
```

**Step 2: 确认订单**
```python
POST /purchase/confirm-order
{
    ...  # 同预览数据
    "orderComplete": true
}
```

---

## 📅 定时任务设置

### 方式 1：使用 Cron（推荐）

```bash
# 编辑 crontab
crontab -e

# 每天上午 11:00 运行
0 11 * * * cd /path/to/epic_free_game && python3 epic_auto_claimer.py >> auto_claim.log 2>&1

# 或每周四上午 11:00 运行（Epic 更新日）
0 11 * * 4 cd /path/to/epic_free_game && python3 epic_auto_claimer.py >> auto_claim.log 2>&1
```

### 方式 2：使用便捷脚本

创建 `run_auto_claim.sh`：
```bash
#!/bin/bash
cd "$(dirname "$0")"

# 检查 Cookie 是否需要刷新
python3 cookie_manager.py check
if [ $? -ne 0 ]; then
    echo "Cookies need refresh"
    python3 cookie_manager.py refresh
fi

# 运行自动领取
python3 epic_auto_claimer.py
```

然后在 Cron 中调用：
```bash
0 11 * * * /path/to/epic_free_game/run_auto_claim.sh >> auto_claim.log 2>&1
```

---

## 🐛 故障排除

### 问题 1：Cookie 过期

**症状**：
```
❌ Failed to load cookies: Expired cookies
```

**解决**：
```bash
# 1. 在 Chrome 中重新登录 Epic Games
# 2. 确保访问了 store.epicgames.com
# 3. 完全关闭 Chrome
# 4. 刷新 Cookie
python3 cookie_manager.py refresh
```

### 问题 2：GraphQL 领取失败

**症状**：
```
❌ GraphQL method failed: Unauthorized
```

**可能原因**：
- EPIC_BEARER_TOKEN 过期
- 账户需要重新认证

**解决**：
```bash
# 刷新 Cookie
python3 cookie_manager.py refresh
```

### 问题 3：所有方法都失败

**症状**：
```
❌ All claim methods failed
```

**可能原因**：
- API 端点变更
- 需要验证码
- 账户被限制

**解决**：
1. 检查日志文件 `auto_claim.log`
2. 手动访问 Epic Store 检查账户状态
3. 等待 24 小时后重试

### 问题 4：Cookie 提取失败

**症状**：
```
❌ Failed to extract cookies from any browser
```

**解决**：
```bash
# 1. 确保 Chrome 完全关闭
killall "Google Chrome"

# 2. 确保已登录 Epic Games
# 3. 重新提取
python3 cookie_manager.py refresh
```

---

## 📊 日志分析

### 日志位置
- Cookie 管理：输出到终端
- 自动领取：`auto_claim.log`

### 查看日志
```bash
# 查看最近 50 行
tail -50 auto_claim.log

# 实时监控
tail -f auto_claim.log

# 搜索错误
grep "❌" auto_claim.log

# 搜索成功
grep "✅ Claimed" auto_claim.log
```

---

## ⚠️ 重要注意事项

### 1. 使用频率
- **建议**：每天运行一次
- **最佳时间**：每周四上午（新游戏发布）
- **避免**：频繁运行（每小时）

### 2. Cookie 安全
- Cookie 包含完整的账户访问权限
- 妥善保管 `claimer/data/cookies.json`
- 不要分享或上传到公开仓库
- 定期备份到安全位置

### 3. 账户安全
- 使用自己的账户和 Cookie
- 不要使用他人的账户
- 如果账户出现异常，立即停止使用

### 4. API 变更
- Epic Games 可能随时变更 API
- 如果领取失败，可能需要更新脚本
- 关注项目更新

### 5. 成功率
- GraphQL 方法：~80%（推测）
- Order API 方法：~60%（推测）
- 整体成功率取决于多个因素

---

## 🔄 Cookie 生命周期管理

### 自动化流程

```bash
#!/bin/bash
# auto_claim_with_refresh.sh

# Step 1: 检查 Cookie
python3 cookie_manager.py check
NEED_REFRESH=$?

# Step 2: 如需刷新
if [ $NEED_REFRESH -ne 0 ]; then
    echo "Refreshing cookies..."
    python3 cookie_manager.py refresh

    if [ $? -ne 0 ]; then
        echo "Failed to refresh cookies. Please login manually."
        exit 1
    fi
fi

# Step 3: 运行领取
python3 epic_auto_claimer.py

# Step 4: 记录执行时间
echo "Last run: $(date)" >> last_run.txt
```

### Cookie 检查计划

- **每次运行前**：检查 Cookie 有效性
- **每周一次**：主动刷新 Cookie
- **过期前 7 天**：自动提醒刷新

---

## 📈 预期效果

### 成功案例
```
输入: 5 款免费游戏
输出:
  ✅ 成功领取: 3 款
  📦 已拥有: 2 款
  ❌ 失败: 0 款
```

### 典型运行时间
- Cookie 验证：< 1 秒
- 获取游戏列表：2-3 秒
- 每款游戏检查：1-2 秒
- 每款游戏领取：3-5 秒
- **总计（5 款游戏）**：约 30-40 秒

### 对比传统方式
| 方式 | 时间 | 成功率 | 稳定性 |
|------|------|--------|--------|
| 浏览器自动化 | 3-5 分钟 | ~50% | 低（Cloudflare） |
| API 方式 | 30-40 秒 | ~80% | 高 |
| 手动领取 | 5-10 分钟 | 100% | 最高 |

---

## 🎯 下一步优化

### 短期（已实现）
- [x] Cookie 自动提取
- [x] Cookie 验证机制
- [x] GraphQL 领取实现
- [x] 反爬虫对策

### 中期（计划中）
- [ ] 更准确的 API 端点（通过网络监控）
- [ ] 验证码自动处理
- [ ] 多账户支持
- [ ] Web UI 管理界面

### 长期（愿景）
- [ ] 完全无需人工干预
- [ ] 智能 Cookie 管理
- [ ] 跨平台支持（GOG, Steam）

---

## 📚 相关资源

### 项目文件
- `epic_auto_claimer.py` - 主要领取程序
- `cookie_manager.py` - Cookie 管理器
- `API_AUTO_CLAIM_GUIDE.md` - 本文档

### 其他文档
- `PARALLEL_PLAN.md` - 并行方案指南
- `API_RESEARCH_GUIDE.md` - API 研究手册
- `SUMMARY.md` - 项目总结

---

**准备好了吗？开始自动领取之旅！** 🚀

```bash
# 立即开始
python3 epic_auto_claimer.py
```
