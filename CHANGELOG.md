# Changelog

## [2.0.0] - 2026-02-11

### 🎉 Major Release: API-Based Notification System

完全重构的通知系统，使用 Epic Games 官方 API 实现智能游戏所有权检查。

### ✨ Added

#### 核心功能
- **API 通知系统** (`notifier/` 目录)
  - 智能免费游戏检测
  - 邮件通知（HTML 格式）
  - Epic Games Entitlements API 集成
  - 游戏所有权自动检查

#### Cookie 管理
- **cookie_manager.py** - 浏览器 Cookie 提取与管理
  - 支持 Chrome/Edge/Brave
  - 自动解密 Cookie（browser-cookie3）
  - Cookie 验证和备份

#### 辅助工具
- **mark_owned.py** - 手动标记已拥有游戏
- **epic_auto_claimer.py** - API 自动领取（实验性）
- **install_notifier_cron.sh** - 定时任务安装

### 🔧 Fixed

- ✅ **URL 404 问题** - ADD_ON/DLC 类型游戏 URL 生成错误
  - 修复前：使用 `urlSlug`（不准确）
  - 修复后：优先使用 `offerMappings.pageSlug`（准确）
  
- ✅ **Cookie 提取失败** - Chrome v80+ Cookie 加密问题
  - 使用 `browser-cookie3` 自动解密
  
- ✅ **重复通知** - 已领取游戏仍然通知
  - 实现 Epic Games Entitlements API 检查
  - 双重去重：API + 本地记录

- ✅ **价格过滤** - 打折游戏被误认为免费
  - 添加 `discountPrice == 0` 检查

### 🚀 Changed

- **README.md** - 完全重写，详细说明新系统
- **.gitignore** - 增强敏感文件保护
- **.env.example** - 简化配置模板

### 📚 Documentation

新增文档：
- `notifier/README.md` - 详细使用指南
- `notifier/API_AUTO_CLAIM_GUIDE.md` - API 自动领取指南
- `notifier/URL_FIX_NOTES.md` - URL 修复技术细节
- `notifier/FINAL_IMPLEMENTATION.md` - 实现总结

### 🔐 Security

- 所有敏感文件已加入 `.gitignore`
- Cookie 仅本地存储
- 邮箱使用授权码而非密码
- 只调用只读 API

### 🎯 Technical Highlights

#### 1. Epic Games API 集成

发现并集成正确的 Entitlements API：
```
GET /entitlement/api/account/{account_id}/entitlements
Authorization: Bearer {EPIC_EG1_TOKEN}
```

**工作原理：**
1. 从 JWT token 提取 account_id
2. 获取所有 entitlements (67 namespaces, 124 items)
3. 比对免费游戏的 namespace
4. 匹配成功 = 已拥有

#### 2. URL 生成优化

三级优先级确保准确性：
```python
# Priority 1: offerMappings (most reliable)
if offerMappings:
    url_slug = offerMappings[0].pageSlug

# Priority 2: catalogNs.mappings  
elif catalogNs_mappings:
    url_slug = mappings[0].pageSlug

# Priority 3: urlSlug (fallback)
else:
    url_slug = game.urlSlug
```

#### 3. Cookie 解密

解决 Chrome v80+ Cookie 加密问题：
- 使用 `browser-cookie3` 库
- 自动从 macOS Keychain 获取密钥
- 支持多浏览器（Chrome/Edge/Brave）

### 📊 Statistics

- **代码行数**: 3739+ 行新增
- **新文件**: 15 个
- **API 集成**: 2个关键 API
- **文档页数**: 4个详细文档

### 🙏 Credits

- Epic Games Store API
- browser-cookie3 项目
- vogler/free-games-claimer

---

## [1.0.0] - 2026-02-10

### Initial Release

- Puppeteer 浏览器自动化
- 基础邮件通知
- Cron 定时任务
- Steam 登录支持

---

**Full Changelog**: https://github.com/wangsibo1993/epic_free_game/compare/v1.0.0...v2.0.0
