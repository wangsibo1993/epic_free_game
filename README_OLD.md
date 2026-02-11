# 🎮 Epic Games 自动免费游戏领取助手

这是一个全自动的 Epic Games Store 免费游戏领取工具。它基于 [vogler/free-games-claimer](https://github.com/vogler/free-games-claimer) 进行封装和优化，增加了**邮件通知**功能，并优化了**登录体验**。

核心功能：
- ✅ **全自动领取**：每天自动检查并领取本周免费游戏。
- 📧 **智能邮件通知**：只有成功领取新游戏或发生错误时才会发邮件，避免垃圾邮件打扰。
- 🛡️ **抗检测优化**：使用定制的 Chromium 内核和伪装参数，降低被识别为机器人的概率。

---

## 🚀 快速开始

### 1. 环境准备
确保你的 macOS 已安装 Node.js 和 Git。

```bash
git clone git@github.com:wangsibo1993/epic_free_game.git
cd epic_free_game
npm install
```

### 2. 🌐 网络访问说明

> ✅ **好消息：中国大陆用户无需代理！**
>
> 本脚本支持智能区域选择：
> - **不配置代理**：自动使用中国区（`zh-CN`），直接访问，无需代理
> - **配置代理**：自动切换到美区（`en-US`），获取完整游戏列表
>
> **推荐配置：**
> - **中国大陆用户**：不配置代理，使用中国区（更稳定，不触发反爬虫）
> - **需要全部游戏**：在 `.env` 中配置 `PROXY_HOST`，使用美区
>
> **注意事项：**
> - ⚠️ 中国区和美区的免费游戏可能不完全相同
> - ✅ 不使用代理避免了 Cloudflare 检测，更稳定
> - ✅ 账号是全球通用的，任何区域领取的游戏都能玩

### 3. 首次登录 (关键步骤)

在能够自动运行之前，必须先手动运行一次以保存登录凭证 (Cookies)。

**💡 强烈建议：**
由于 Epic Games 的网页登录验证非常严格（尤其是直接使用账号密码时容易出现 Captcha 错误），**强烈建议使用第三方账号（如 Steam、Google、Apple）进行关联登录**。
> **经验证，使用 Steam 账号关联登录是最稳定、最不容易报错的方式。**

运行登录脚本：

```bash
./setup_login.sh
```

**操作指南：**
1.  脚本会弹出一个 Chromium 浏览器窗口。
2.  在登录页面，点击底部的图标选择 **"Sign in with Steam"** (或其他第三方方式)。
3.  登录成功后，脚本会自动跳转并检测当周免费游戏。
4.  看到终端提示 `Signed in as ...` 并且浏览器开始自动跳转页面时，说明登录凭证已保存成功。
5.  如果脚本自动开始领取游戏，你可以等待它完成；如果已保存凭证，直接关闭窗口即可。

### 4. 配置邮件通知

复制配置文件模版：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的邮箱配置（推荐使用 QQ 邮箱）：

```ini
# QQ邮箱 SMTP 配置示例
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USER=your_email@qq.com
SMTP_PASS=your_auth_code  # 在QQ邮箱设置中获取的授权码
TO_EMAIL=your_email@qq.com # 接收通知的邮箱

# 反检测配置（推荐开启）
ENABLE_ANTI_DETECTION=1  # 启用随机延迟和人类行为模拟，降低被识别为机器人的概率

# 网络代理配置（不推荐 - 仅特殊情况使用）
# Epic Games 已支持中国区，无需代理。启用代理反而容易触发 Cloudflare 检测
# PROXY_HOST=127.0.0.1:8118
```

### 5. 测试自动运行

配置完成后，运行以下命令测试无头模式（后台静默运行）：

```bash
./run_auto.sh
```

如果看到 `Auto-claim finished successfully` 的日志，且没有报错，说明一切正常。

---

## ⏰ 设置每日自动任务

使用 macOS 的 `crontab` 设置每天定时检查（例如每天上午 11:00）。

1.  运行项目自带的安装脚本（会自动获取当前路径并写入 crontab）：

```bash
chmod +x install_cron.sh
./install_cron.sh
```

2.  或者手动添加：

```bash
crontab -e
```

添加以下行（请修改为你的实际路径）：
```cron
0 11 * * * /path/to/epic_free_game/run_auto.sh >> /path/to/epic_free_game/claim.log 2>&1
```

---

## 🔍 常见问题

**Q: 登录时一直提示 "Incorrect response" 怎么办？**
A: 这是 Epic 的反爬虫拦截。
1. 请确保使用了 `./setup_login.sh` 启动浏览器。
2. **不要**直接输入 Epic 账号密码。
3. **改用 Steam / Google 等第三方账号登录**，通常能直接绕过此错误。
4. 如果依然不行，尝试在弹出的浏览器中按 `Cmd+R` 刷新页面，或等待几小时后再试。

**Q: 邮件通知没有收到？**
A: 
1. 检查 `.env` 中的 `SMTP_PASS` 是否正确（是授权码，不是邮箱密码）。
2. 只有在 **"成功领取了新游戏"** 或者 **"脚本运行出错"** 时才会发邮件。如果游戏已经领过了，脚本会静默退出，不发送邮件。

**Q: 出现 "net::ERR_CONNECTION_CLOSED" 或 "Timeout" 错误怎么办？**
A: 这通常是网络连接问题：
1. **测试中国区连接**：
   ```bash
   curl -I https://store.epicgames.com/zh-CN/free-games
   ```
   如果返回 200 说明网络正常
2. **检查本地网络**：确保可以正常访问国际网站
3. **清除浏览器缓存**：`rm -rf claimer/data/browser && ./setup_login.sh`
4. **增加超时时间**：在 `.env` 文件中设置 `TIMEOUT=180`

**Q: 遇到 Cloudflare "One more step" 验证怎么办？**
A: 这是 Epic Games 的反爬虫保护：
1. **等待重试**：等待几个小时后再运行（推荐）
2. **手动验证**：运行 `./bypass_cloudflare.sh` 在可见浏览器中完成验证
3. **清除数据**：`rm -rf claimer/data/browser && ./setup_login.sh` 重新登录
4. **更换代理**：尝试使用不同的代理节点
5. **启用反检测**：确保 `.env` 中 `ENABLE_ANTI_DETECTION=1`（已默认启用）

该脚本已内置反检测功能：
- ✅ 随机延迟模拟人类操作节奏
- ✅ 人类化的鼠标移动和点击
- ✅ 随机页面滚动
- ✅ 隐藏自动化特征（navigator.webdriver等）
- ✅ 增强的浏览器参数配置

**Q: 如何查看运行日志？**
A: 日志保存在项目目录下的 `claim.log` 文件中：
```bash
tail -f claim.log
```
