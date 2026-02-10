# 如何导出 Cookie 使用

为了避免脚本自动登录时遇到的验证码和反爬虫检测，您可以手动在浏览器登录 Epic Games，然后将 Cookie 导出给脚本使用。

## 步骤 1: 安装浏览器插件

推荐使用 **EditThisCookie** 或类似的插件：
- [Chrome 商店链接](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)
- [Edge 商店链接](https://microsoftedge.microsoft.com/addons/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)

## 步骤 2: 登录 Epic Games

1. 打开浏览器，访问 [Epic Games Store](https://store.epicgames.com/)。
2. 登录您的账号（建议勾选“记住我”）。
3. 确保能够正常访问个人资料页面，且没有弹窗验证。

## 步骤 3: 导出 Cookie

1. 点击浏览器工具栏上的 EditThisCookie 图标。
2. 点击“导出”按钮（通常是一个向右的箭头图标 ➡），这会将 Cookie 复制到剪贴板。
3. **重要**：确保导出的格式是 JSON 数组。

## 步骤 4: 保存文件

1. 在本项目根目录下，找到 `claimer/data` 目录（如果没有请创建）。
2. 创建一个名为 `cookies.json` 的文件。
3. 将剪贴板中的内容粘贴到 `cookies.json` 中并保存。
   - 文件路径应为：`epic_free_game/claimer/data/cookies.json`

## 步骤 5: 运行脚本

现在您可以运行脚本了，它会自动加载您刚才保存的 Cookie：

```bash
./run_auto.sh
```

脚本启动时应该会显示：
`✅ Loaded X cookies from external file`

## 注意事项

- Cookie 可能会过期。如果脚本提示登录失效，请重复上述步骤更新 `cookies.json`。
- 请勿将 `cookies.json` 分享给他人，其中包含您的登录凭证。
