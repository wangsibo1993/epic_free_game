# 🎮 Epic Games Free Game Auto Notifier

自动检测 Epic Games 免费游戏并发送邮件通知，支持 API 检查游戏所有权，避免重复通知已领取的游戏。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## ✨ 核心特性

- 🎮 **自动检测免费游戏** - 每天定时检测 Epic Games 最新免费游戏
- 📧 **邮件通知** - 发现新游戏后自动发送邮件通知（HTML格式，包含游戏链接）
- ✅ **智能所有权检查** - 通过 Epic Games API 检查游戏库，已拥有的游戏不再通知
- 🔐 **Cookie 自动管理** - 自动提取和解密浏览器 Cookie（支持 Chrome/Edge/Brave）
- 🚫 **双重去重机制** - API检查 + 本地记录，确保不重复通知
- ⏰ **Cron 定时任务** - 每天自动运行，无需手动干预
- 📝 **完整日志记录** - 详细的运行日志，方便调试和追踪

## 📋 系统要求

- Python 3.9+
- macOS/Linux（Windows 需修改路径）
- Chrome/Edge/Brave 浏览器（用于提取 Cookie）
- Epic Games 账号

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/YOUR_USERNAME/epic_free_game.git
cd epic_free_game
```

### 2. 安装 Python 依赖

```bash
pip3 install requests python-dotenv browser-cookie3 pycryptodome
```

### 3. 配置邮箱

复制环境变量模板并编辑：

```bash
cp .env.example .env
nano .env
```

填写以下配置：

```ini
# SMTP 邮件配置
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USER=your_email@qq.com      # 你的QQ邮箱
SMTP_PASS=your_auth_code          # QQ邮箱授权码（不是密码！）
TO_EMAIL=recipient@example.com    # 接收通知的邮箱
```

**获取 QQ 邮箱授权码：**
1. 登录 [QQ 邮箱网页版](https://mail.qq.com)
2. 设置 → 账户 → POP3/IMAP/SMTP 服务
3. 开启 SMTP 服务并生成授权码

### 4. 提取 Cookie（可选但推荐）

在 Chrome 中登录 Epic Games 账号，然后运行：

```bash
cd notifier
python3 cookie_manager.py refresh
```

这步是可选的，但强烈推荐：
- ✅ **有 Cookie**：可以检查游戏所有权，已拥有的游戏不会通知
- ⚠️ **无 Cookie**：仍可检测免费游戏并通知，但无法过滤已拥有的

### 5. 测试运行

```bash
cd notifier
python3 notify_free_games.py
```

成功后你会收到邮件通知！

### 6. 安装定时任务

每天11点自动检测：

```bash
cd notifier
bash install_notifier_cron.sh
```

查看定时任务：
```bash
crontab -l
```

## 📁 项目结构

```
epic_free_game/
├── claimer/                    # 浏览器自动化（旧版，已暂停）
│   └── epic-games.js          # Puppeteer 自动领取脚本
│
├── notifier/                   # ⭐ API 通知系统（推荐使用）
│   ├── notify_free_games.py   # 🎯 主通知脚本（带所有权检查）
│   ├── epic_auto_claimer.py   # API 自动领取（实验性）
│   ├── cookie_manager.py      # Cookie 提取与管理
│   ├── mark_owned.py          # 手动标记已拥有游戏
│   ├── run_notifier.sh        # Cron 包装脚本
│   ├── install_notifier_cron.sh # 定时任务安装脚本
│   └── README.md              # 详细文档
│
├── .env.example               # 环境变量模板
├── .gitignore                 # Git 忽略文件
└── README.md                  # 本文件
```

## 🔧 工作原理

### 1. 免费游戏检测

调用 Epic Games Store API 获取免费游戏列表。

### 2. 所有权检查（核心创新🌟）

使用 Epic Games Entitlement API 检查用户游戏库：

```
GET https://entitlement-public-service-prod08.ol.epicgames.com/entitlement/api/account/{account_id}/entitlements
```

**工作流程：**
1. 从 `EPIC_EG1` token (JWT) 中提取 `account_id`
2. 调用 Entitlements API 获取用户所有权限
3. 提取所有拥有的游戏 `namespace`
4. 将免费游戏的 `namespace` 与已拥有的对比
5. 匹配成功 = 已拥有，不发送通知

**优势：**
- ✅ **100% 准确** - 直接查询官方 API
- ✅ **实时更新** - 反映最新的游戏库状态  
- ✅ **支持所有类型** - BASE_GAME、ADD_ON、DLC 等

### 3. 双重去重

1. **API 检查** - 过滤已拥有的游戏
2. **本地记录** - 过滤已通知过的游戏

## 📚 使用指南

详见 [notifier/README.md](notifier/README.md)

## 🐛 故障排除

### 邮件发送失败

1. 检查 `.env` 配置
2. 确认使用**授权码**而非密码
3. 检查 SMTP 端口

### Cookie 提取失败

1. 在 Chrome 中登录 Epic Games
2. 完全关闭浏览器
3. 重新运行: `python3 cookie_manager.py refresh`

### API 认证失败

Cookie 已过期，重新提取：
```bash
python3 cookie_manager.py refresh
```

## 🔐 安全与隐私

- ✅ 敏感信息仅本地存储
- ✅ 只调用只读 API
- ✅ 开源透明，可审计
- ✅ 无第三方数据上传

## 📝 更新日志

### 2026-02-11
- ✅ 实现 Epic Games Entitlements API 集成
- ✅ 修复 Cookie 提取和解密
- ✅ 修复 URL 404 问题
- ✅ 添加价格过滤
- ✅ 优化所有权检查逻辑

## 📄 许可证

MIT License

## 🙏 致谢

- [vogler/free-games-claimer](https://github.com/vogler/free-games-claimer)
- Epic Games Store API
- browser-cookie3 项目

---

**⚠️ 免责声明**: 本项目仅供学习交流使用。请遵守 Epic Games 服务条款。

**🌟 如果这个项目对你有帮助，请给一个 Star！**
