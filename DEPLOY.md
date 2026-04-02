# Cloudflare Pages 部署指南

## 部署架构

```
GitHub Repository
├── .github/workflows/daily-fetch.yml  (定时抓取数据)
├── index.html                          (前端页面)
├── data/                               (JSON 数据文件)
└── scripts/                            (抓取脚本)

       ↓ GitHub Actions 定时更新

Cloudflare Pages (静态托管)
└── https://your-site.pages.dev
```

## 步骤一：准备代码

### 1. 重命名静态页面

将 `index-static.html` 重命名为 `index.html`（覆盖原文件）：

```bash
mv index-static.html index.html
```

### 2. 创建 GitHub 仓库

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/daily-report.git
git push -u origin main
```

## 步骤二：配置 Cloudflare Pages

### 1. 登录 Cloudflare Dashboard

访问 https://dash.cloudflare.com → Pages

### 2. 创建项目

1. 点击 **"Create a project"**
2. 选择 **"Connect to Git"**
3. 授权 GitHub 访问，选择你的仓库
4. 配置构建设置：

| 设置项 | 值 |
|--------|-----|
| Project name | `mingxin-daily` (自定义) |
| Production branch | `main` |
| Framework preset | `None` |
| Build command | 留空 |
| Build output directory | `.` (根目录) |

5. 点击 **"Save and Deploy"**

### 3. 获取网站地址

部署完成后，你会获得类似 `https://mingxin-daily.pages.dev` 的网址。

## 步骤三：配置定时任务（GitHub Actions）

### 1. 启用 GitHub Actions

进入仓库 → Actions → 点击 "I understand my workflows, go ahead and enable them"

### 2. 配置 Secrets（可选，仅股票数据需要）

如果需要股票数据，添加以下 Secrets：

进入仓库 → Settings → Secrets and variables → Actions → New repository secret

| Secret 名称 | 说明 |
|-------------|------|
| `LONGBRIDGE_APP_KEY` | Longbridge API Key |
| `LONGBRIDGE_APP_SECRET` | Longbridge API Secret |
| `LONGBRIDGE_ACCESS_TOKEN` | Longbridge Access Token |

### 3. 测试手动运行

进入仓库 → Actions → Daily News Fetch → Run workflow

等待任务完成后，确认 `data/` 目录有更新。

## 步骤四：验证部署

1. 访问 Cloudflare Pages 提供的网址
2. 确认页面能正常加载
3. 下拉选择日期，验证数据展示正常

## 更新网站内容

部署后修改内容的方式：

### 方式一：本地修改后推送

```bash
git add .
git commit -m "update: 修改内容"
git push
```

Cloudflare 会自动重新部署。

### 方式二：GitHub 在线编辑

1. 打开 GitHub 仓库
2. 找到要修改的文件
3. 点击右上角的 ✏️ 编辑按钮
4. 修改后 "Commit changes"

### 方式三：更新数据

数据每天自动更新，如需手动更新：

进入仓库 → Actions → Daily News Fetch → Run workflow

## 自定义域名（可选）

1. Cloudflare Dashboard → Pages → 你的项目 → Custom domains
2. 点击 **"Set up a custom domain"**
3. 输入你的域名（如 `daily.mingxin.com`）
4. 按提示添加 DNS 记录
5. 等待 SSL 证书自动颁发

## 故障排查

### 页面显示 "加载中..."

检查浏览器控制台 (F12 → Console)，确认 JSON 文件路径正确。

### 数据未更新

1. 检查 GitHub Actions 是否成功运行
2. 确认 `data/` 目录下有对应日期的 JSON 文件
3. 检查 Cloudflare Pages 是否已重新部署

### 中文显示乱码

确保所有 JSON 文件是 UTF-8 编码，且 HTML 文件包含 `<meta charset="UTF-8">`。

## 成本说明

| 服务 | 费用 |
|------|------|
| GitHub 仓库 | 免费 (Public) |
| GitHub Actions | 免费 (每月 2000 分钟) |
| Cloudflare Pages | 免费 (无限带宽、10万次/天请求) |
| 自定义域名 | 域名注册费用 |

**完全免费的部署方案！**
