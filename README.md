# 明心战略新闻日报

聚合全球政治与AI核心情报，直击业务决策痛点。

## 功能特性

- **核心摘要**：每日战略洞察与关键趋势
- **政治新闻**：国际/国内政治动态及业务影响分析
- **AI行业资讯**：海外/国内AI公司动态及竞争情报
- **一级市场**：投融资动态及竞争对手监控
- **资本市场**：全球主要指数及业务相关标的股价

## 技术架构

- **前端**：HTML + Tailwind CSS + Font Awesome
- **后端**：Node.js + Express
- **数据抓取**：Cheerio + RSS Parser + Axios
- **定时任务**：node-cron

## 快速开始

### 安装依赖

```bash
npm install
```

### 配置环境变量

复制 `.env.example` 为 `.env`，并配置以下参数：

```bash
# 如需股票数据，配置 Longbridge API
LONGBRIDGE_APP_KEY=your_app_key
LONGBRIDGE_APP_SECRET=your_app_secret
LONGBRIDGE_ACCESS_TOKEN=your_access_token
```

### 启动服务

```bash
# 开发模式
npm run dev

# 生产模式
npm start
```

服务启动后访问：
- 日报页面：http://localhost:3000/index.html
- API文档：http://localhost:3000/api/daily

### 手动抓取数据

```bash
# 抓取所有数据
npm run fetch

# 单独抓取某类数据
npm run fetch:stocks
npm run fetch:news
npm run fetch:investment
```

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/daily` | GET | 获取完整日报数据 |
| `/api/stocks` | GET | 获取股票数据 |
| `/api/news/politics` | GET | 获取政治新闻 |
| `/api/news/ai` | GET | 获取AI新闻 |
| `/api/investment` | GET | 获取投融资数据 |
| `/api/summary` | GET | 获取核心摘要 |
| `/api/fetch/all` | POST | 手动触发数据抓取 |

## 项目结构

```
daily-report/
├── data/               # 数据存储目录
├── scripts/            # 数据抓取脚本
│   ├── fetch-all.js    # 汇总入口
│   ├── fetch-stocks.js # 股票数据
│   ├── fetch-news.js   # 新闻数据
│   └── fetch-investment.js # 投融资数据
├── index.html          # 前端页面
├── server.js           # 后端服务
├── package.json
└── .env                # 环境变量
```

## 定时任务

- **每天 08:00（北京时间）**：自动抓取并生成日报

## 数据来源

- **政治新闻**：中国新闻网、新华网、人民网
- **AI资讯**：OpenAI、Google、Anthropic、DeepSeek、阿里、字节、智谱等
- **投融资**：36氪创投平台
- **股票数据**：Longbridge API

## 许可证

内部使用，数据仅供决策参考。
