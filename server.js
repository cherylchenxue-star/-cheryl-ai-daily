require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs-extra');
const dayjs = require('dayjs');
const cron = require('node-cron');

const app = express();
const PORT = process.env.PORT || 3000;

// 中间件
app.use(cors());
app.use(express.json());
// 静态文件服务 - 根目录存放前端文件
app.use(express.static(__dirname, {
    // 不暴露数据目录
    setHeaders: (res, filePath) => {
        if (filePath.includes('data') || filePath.includes('node_modules')) {
            res.status(403).end();
        }
    }
}));

// 数据存储目录
const DATA_DIR = path.join(__dirname, 'data');
fs.ensureDirSync(DATA_DIR);

// ============ API 路由 ============

// 获取日报数据（聚合所有数据）- 支持日期参数
app.get('/api/daily', async (req, res) => {
    try {
        const date = req.query.date || dayjs().format('YYYY-MM-DD');
        const dailyData = await loadDailyData(date);
        res.json({
            success: true,
            date: date,
            updateTime: dayjs().format('HH:mm:ss'),
            data: dailyData
        });
    } catch (error) {
        console.error('获取日报数据失败:', error);
        res.status(500).json({ success: false, error: error.message });
    }
});

// 获取可用日期列表（最近30天）
app.get('/api/dates', async (req, res) => {
    try {
        const dates = await getAvailableDates();
        res.json({ success: true, dates });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// 获取股票数据 - 支持日期参数
app.get('/api/stocks', async (req, res) => {
    try {
        const date = req.query.date;
        const stocks = await loadData('stocks', date);
        res.json({ success: true, date: date || dayjs().format('YYYY-MM-DD'), data: stocks });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// 获取政治新闻
app.get('/api/news/politics', async (req, res) => {
    try {
        const news = await loadData('politics');
        res.json({ success: true, data: news });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// 获取AI新闻
app.get('/api/news/ai', async (req, res) => {
    try {
        const news = await loadData('ai-news');
        res.json({ success: true, data: news });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// 获取投融资数据
app.get('/api/investment', async (req, res) => {
    try {
        const investments = await loadData('investment');
        res.json({ success: true, data: investments });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// 获取核心摘要
app.get('/api/summary', async (req, res) => {
    try {
        const summary = await loadData('summary');
        res.json({ success: true, data: summary });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// 手动触发数据抓取
app.post('/api/fetch/all', async (req, res) => {
    try {
        const fetchAll = require('./scripts/fetch-all');
        await fetchAll();
        res.json({ success: true, message: '数据抓取完成' });
    } catch (error) {
        res.status(500).json({ success: false, error: error.message });
    }
});

// ============ 辅助函数 ============

async function loadData(type, date) {
    const targetDate = date || dayjs().format('YYYY-MM-DD');
    const filePath = path.join(DATA_DIR, `${type}-${targetDate}.json`);

    if (await fs.pathExists(filePath)) {
        return await fs.readJson(filePath);
    }

    // 如果指定日期的数据不存在，返回空数据
    return { items: [], lastUpdate: null };
}

// 获取最近30天的可用日期列表
async function getAvailableDates() {
    const dates = [];
    const files = await fs.readdir(DATA_DIR);

    // 提取所有日期
    const dateSet = new Set();
    files.forEach(file => {
        const match = file.match(/-(\d{4}-\d{2}-\d{2})\.json$/);
        if (match) {
            dateSet.add(match[1]);
        }
    });

    // 获取最近30天
    for (let i = 0; i < 30; i++) {
        const date = dayjs().subtract(i, 'day').format('YYYY-MM-DD');
        if (dateSet.has(date)) {
            dates.push({
                value: date,
                label: i === 0 ? '今天' : i === 1 ? '昨天' : dayjs(date).format('MM月DD日')
            });
        }
    }

    return dates;
}

async function loadDailyData(date) {
    const types = ['summary', 'politics', 'ai-news', 'investment', 'stocks'];
    const data = {};

    for (const type of types) {
        const filePath = path.join(DATA_DIR, `${type}-${date}.json`);
        if (await fs.pathExists(filePath)) {
            data[type] = await fs.readJson(filePath);
        } else {
            data[type] = { items: [], lastUpdate: null };
        }
    }

    return data;
}

// ============ 定时任务 ============

// 每天北京时间08:00自动抓取数据
cron.schedule('0 8 * * *', async () => {
    console.log('[' + new Date().toISOString() + '] 开始自动抓取数据...');
    try {
        const fetchAll = require('./scripts/fetch-all');
        await fetchAll();
        console.log('[' + new Date().toISOString() + '] 数据抓取完成');
    } catch (error) {
        console.error('自动抓取失败:', error);
    }
}, {
    timezone: 'Asia/Shanghai'
});

// 启动服务器
app.listen(PORT, () => {
    console.log(`
╔════════════════════════════════════════╗
║   明心战略新闻日报 API 服务已启动       ║
╠════════════════════════════════════════╣
║  端口: http://localhost:${PORT}           ║
║  日报: http://localhost:${PORT}/index.html ║
╚════════════════════════════════════════╝
    `);
});

module.exports = app;
