# 游戏 URL 404 问题修复说明

## 🐛 问题描述

某些游戏（特别是 DLC/附加内容）的链接会返回 404 错误。

### 错误示例
- **错误链接**: `https://store.epicgames.com/zh-CN/p/poison-retro-set`
- **正确链接**: `https://store.epicgames.com/zh-CN/p/pixel-gun-3d-poison-retro-set-55a7dd`

## 🔍 问题原因

Epic Games API 返回的数据中，不同类型的游戏有不同的 URL 结构：

### 1. 独立游戏（BASE_GAME）
```json
{
  "title": "Ghostrunner 2",
  "offerType": "BASE_GAME",
  "urlSlug": "ghostrunner-2"  // ✅ 可以直接使用
}
```

### 2. DLC/附加内容（ADD_ON）
```json
{
  "title": "剧毒复古套装",
  "offerType": "ADD_ON",
  "urlSlug": "poison-retro-set",  // ❌ 不能直接使用
  "offerMappings": [{
    "pageType": "offer",
    "pageSlug": "pixel-gun-3d-poison-retro-set-55a7dd"  // ✅ 正确的 slug
  }]
}
```

**关键发现**:
- ADD_ON 类型的游戏，`urlSlug` 字段不准确
- 正确的 URL 应该从 `offerMappings` 中获取

## ✅ 修复方案

### 修改前的逻辑
```python
# 只检查 urlSlug 和 productSlug（不准确）
url_slug = game.get('urlSlug') or game.get('productSlug')
if not url_slug:
    mappings = game.get('catalogNs', {}).get('mappings', [])
    if mappings:
        url_slug = mappings[0].get('pageSlug')
```

### 修改后的逻辑（三级优先级）
```python
url_slug = None

# 优先级 1: offerMappings（最准确，适用于所有类型）
offer_mappings = game.get('offerMappings', [])
if offer_mappings:
    for mapping in offer_mappings:
        if mapping.get('pageType') == 'offer':
            url_slug = mapping.get('pageSlug')
            break

# 优先级 2: urlSlug 或 productSlug（适用于独立游戏）
if not url_slug:
    url_slug = game.get('urlSlug') or game.get('productSlug')

# 优先级 3: catalogNs mappings（兜底方案）
if not url_slug:
    mappings = game.get('catalogNs', {}).get('mappings', [])
    if mappings:
        url_slug = mappings[0].get('pageSlug')
```

## 📝 已修复的文件

1. ✅ `notify_free_games.py` - 通知系统
2. ✅ `epic_auto_claimer.py` - API 自动领取
3. ✅ `epic_api_claimer.py` - API 测试框架

## 🧪 测试结果

修复后的 URL 列表（2026-02-11）：

| 游戏名称 | 类型 | URL 状态 |
|---------|------|---------|
| Eternal Threads | BASE_GAME | ✅ 正常 |
| 幽灵行者 2 | BASE_GAME | ✅ 正常 |
| 纪念碑谷 | BASE_GAME | ✅ 正常 |
| 波坦尼庄园 | BASE_GAME | ✅ 正常 |
| 剧毒复古套装 | ADD_ON | ✅ 已修复 |

所有链接都能正常访问，404 问题已解决！

## 🔄 如何验证修复

### 方法 1：运行通知系统
```bash
# 清除通知记录，重新测试
rm notified_games.json
python3 notify_free_games.py
```

查看输出的 URL 是否正确。

### 方法 2：直接测试 API
```bash
python3 << 'EOF'
import requests

response = requests.get(
    'https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions',
    params={'locale': 'zh-CN', 'country': 'CN'}
)

data = response.json()
elements = data['data']['Catalog']['searchStore']['elements']

for game in elements:
    promotions = game.get('promotions')
    if not promotions:
        continue

    promo_offers = promotions.get('promotionalOffers', [])
    if not promo_offers or not promo_offers[0].get('promotionalOffers'):
        continue

    # 使用新逻辑获取 URL
    url_slug = None
    offer_mappings = game.get('offerMappings', [])
    if offer_mappings:
        for mapping in offer_mappings:
            if mapping.get('pageType') == 'offer':
                url_slug = mapping.get('pageSlug')
                break
    if not url_slug:
        url_slug = game.get('urlSlug') or game.get('productSlug')

    if url_slug:
        url = f"https://store.epicgames.com/zh-CN/p/{url_slug}"
        print(f"{game['title']}: {url}")
EOF
```

### 方法 3：手动访问邮件中的链接
1. 运行通知系统
2. 查收邮件
3. 点击每个游戏链接
4. 确认都能正常打开（无 404 错误）

## 📚 技术细节

### Epic Games API 数据结构

完整的游戏对象包含以下字段：

```json
{
  "id": "游戏ID",
  "namespace": "命名空间",
  "title": "游戏名称",
  "offerType": "BASE_GAME | ADD_ON | DLC | BUNDLE",

  "urlSlug": "简短slug（可能不准确）",
  "productSlug": "产品slug（较少使用）",

  "offerMappings": [
    {
      "pageType": "offer",
      "pageSlug": "完整准确的页面slug"  // ← 最可靠
    }
  ],

  "catalogNs": {
    "mappings": [
      {
        "pageType": "productHome",
        "pageSlug": "产品主页slug"
      }
    ]
  }
}
```

### URL 构建规则

Epic Games 商店的 URL 格式：
```
https://store.epicgames.com/{locale}/p/{page_slug}
```

其中：
- `locale`: 地区代码（如 `zh-CN`、`en-US`）
- `page_slug`: 页面标识符

**重点**:
- 对于 ADD_ON/DLC，必须使用 `offerMappings` 中的 `pageSlug`
- 对于 BASE_GAME，`urlSlug` 通常是准确的
- `offerMappings` 适用于所有类型，是最可靠的来源

## 🎯 未来改进

### 建议 1：URL 验证
在发送通知前验证 URL 是否可访问：

```python
def validate_url(url):
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False
```

### 建议 2：多语言支持
检测用户偏好语言，提供相应的链接：

```python
LOCALES = ['zh-CN', 'en-US', 'ja-JP', 'ko-KR']
game_url = f"https://store.epicgames.com/{user_locale}/p/{url_slug}"
```

### 建议 3：缓存有效 URL
记录已验证的 URL，避免重复检查：

```json
{
  "game_id": "f643a600e99c43cca99d1ca37b41fe33",
  "valid_url": "https://store.epicgames.com/zh-CN/p/...",
  "verified_at": "2026-02-11"
}
```

## ✨ 总结

- ✅ **问题**: ADD_ON 类型游戏的 URL 不正确
- ✅ **原因**: 使用了不准确的 `urlSlug` 字段
- ✅ **修复**: 优先使用 `offerMappings[].pageSlug`
- ✅ **结果**: 所有游戏链接都能正常访问

修复已应用到所有相关文件，未来的通知邮件将包含正确的链接！
