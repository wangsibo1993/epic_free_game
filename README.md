# Epic Games Free Games Auto-Claimer

此工具可以自动领取 Epic Games Store 的免费游戏。它基于 [vogler/free-games-claimer](https://github.com/vogler/free-games-claimer)。

## 🚀 快速开始

### 1. 首次运行与登录 (必须)

在能够自动运行之前，你需要先手动运行一次以完成登录。脚本会保存你的登录状态 (Cookies)。

在终端中运行以下命令：

```bash
./setup_login.sh
```

**操作步骤：**
1.  运行脚本后，会弹出一个 Firefox 浏览器窗口。
2.  在浏览器中登录你的 Epic Games 账号。
3.  **重要**：登录成功后，脚本会自动检测并开始尝试领取当周的免费游戏。
4.  领取完成后或看到脚本继续运行后，你可以关闭窗口。登录凭证已保存。

### 2. 测试自动领取

登录成功后，你可以运行以下脚本来测试无头模式 (不显示浏览器窗口)：

```bash
./run_auto.sh
```

如果它成功运行并输出日志，说明配置完成。

### 3. 设置每日自动运行 (Cron)

要实现完全自动化，我们可以使用 macOS 的 `crontab` 来设置定时任务。

1.  打开当前用户的 cron 配置：
    ```bash
    crontab -e
    ```

2.  按 `i` 进入编辑模式，在文件末尾添加以下内容 (每天中午 12:00 运行)：

    ```cron
    0 12 * * * /path/to/your/project/run_auto.sh >> /path/to/your/project/claim.log 2>&1
    ```

3.  按 `Esc`，然后输入 `:wq` 并回车保存退出。

### 🔍 查看日志

自动运行的日志会保存在 `claim.log` 文件中。你可以随时查看该文件来确认游戏是否领取成功。

```bash
tail -f claim.log
```

## ⚠️ 注意事项

- **验证码 (Captcha)**: Epic Games 可能会不定期弹出验证码。如果脚本在日志中报告需要验证码，你可能需要再次运行 `./setup_login.sh` 来手动解决。
- **多重身份验证 (2FA)**: 如果开启了 2FA，首次登录时需要在浏览器中输入验证码。脚本支持保存信任设备的 Token，因此通常不需要每次都输入。
