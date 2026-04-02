/**
 * 数据抓取总控脚本 V2
 * 统一调度：股票、新闻、政策、投融资
 */

const path = require('path');
const fs = require('fs-extra');
const dayjs = require('dayjs');
const { execSync } = require('child_process');

const TODAY = dayjs().format('YYYY-MM-DD');
const DATA_DIR = path.join(__dirname, '..', 'data');

async function fetchAll() {
    console.log('\n');
    console.log('╔════════════════════════════════════════════════════════╗');
    console.log('║         明心战略新闻日报 - 数据抓取总控 V2              ║');
    console.log(`║         ${TODAY}                                ║`);
    console.log('╚════════════════════════════════════════════════════════╝');
    console.log('');

    const results = {
        date: TODAY,
        timestamp: dayjs().format('YYYY-MM-DD HH:mm:ss'),
        tasks: []
    };

    // 1. 股票数据（Python SDK）
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('[1/4] 股票数据抓取 (Longbridge SDK)');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    try {
        const output = execSync('python scripts/fetch_real_sdk.py', {
            encoding: 'utf-8',
            cwd: path.join(__dirname, '..'),
            stdio: 'pipe'
        });
        console.log(output);
        results.tasks.push({ name: 'stocks', status: 'success' });
    } catch (error) {
        console.error('股票数据抓取失败:', error.message);
        results.tasks.push({ name: 'stocks', status: 'failed', error: error.message });
    }

    // 2. 新闻数据
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('[2/3] 新闻数据抓取 (RSS)');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    try {
        const fetchNews = require('./fetch-news-v3');
        await fetchNews();
        results.tasks.push({ name: 'news', status: 'success' });
    } catch (error) {
        console.error('新闻数据抓取失败:', error.message);
        results.tasks.push({ name: 'news', status: 'failed', error: error.message });
    }

    // 3. 投融资数据
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('[3/3] 投融资数据抓取 (36氪创投平台 - Puppeteer)');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    try {
        const fetchInvestment = require('./fetch-investment-real');
        await fetchInvestment();
        results.tasks.push({ name: 'investment', status: 'success' });
    } catch (error) {
        console.error('投融资数据抓取失败:', error.message);
        results.tasks.push({ name: 'investment', status: 'failed', error: error.message });
    }

    // 生成核心摘要
    console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('[汇总] 生成核心摘要');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    try {
        await generateSummary(results);
        results.tasks.push({ name: 'summary', status: 'success' });
    } catch (error) {
        console.error('生成摘要失败:', error.message);
        results.tasks.push({ name: 'summary', status: 'failed', error: error.message });
    }

    // 保存结果
    await fs.writeJson(path.join(DATA_DIR, `fetch-result-${TODAY}.json`), results, { spaces: 2 });

    // 输出汇总
    console.log('\n');
    console.log('╔════════════════════════════════════════════════════════╗');
    console.log('║                    抓取完成汇总                        ║');
    console.log('╠════════════════════════════════════════════════════════╣');
    results.tasks.forEach(task => {
        const icon = task.status === 'success' ? '✓' : '✗';
        const nameMap = {
            stocks: '股票数据    ',
            news: '新闻数据    ',
            investment: '投融资数据  ',
            summary: '核心摘要    '
        };
        console.log(`║  ${icon} ${nameMap[task.name] || task.name}: ${task.status === 'success' ? '成功' : '失败'}`);
    });
    console.log('╚════════════════════════════════════════════════════════╝');
    console.log('');

    const allSuccess = results.tasks.every(t => t.status === 'success');
    process.exit(allSuccess ? 0 : 1);
}

async function generateSummary(results) {
    // 读取各模块数据
    const stocksFile = path.join(DATA_DIR, `stocks-${TODAY}.json`);
    const newsFile = path.join(DATA_DIR, `news-full-${TODAY}.json`);

    let stockData = null;
    let newsData = null;

    try {
        stockData = await fs.readJson(stocksFile);
    } catch (e) {
        console.log('  股票数据未生成，使用默认摘要');
    }

    try {
        newsData = await fs.readJson(newsFile);
    } catch (e) {
        console.log('  新闻数据未生成，使用默认摘要');
    }

    // 生成市场状态描述
    let marketStatus = '全球资本市场整体平稳运行';
    if (stockData && stockData.indices) {
        const nasdaq = stockData.indices.find(i => i.symbol === 'QQQ.US');
        if (nasdaq) {
            const trend = nasdaq.changePercent >= 0 ? '上涨' : '回调';
            marketStatus = `美股科技股${trend}，AI主题持续发酵`;
        }
    }

    // 生成AI动态描述
    let aiStatus = '';
    if (newsData && newsData.aiDomestic && newsData.aiDomestic.length > 0) {
        const aiNews = newsData.aiDomestic.slice(0, 2).map(n => n.title).join('；');
        aiStatus = `AI产业方面，${aiNews}`;
    } else {
        aiStatus = 'AI产业持续高热，大模型赛道融资活跃';
    }

    // 生成投资建议
    let investmentAdvice = '建议关注AI产业链投资机会';
    if (stockData && stockData.marketCommentary) {
        investmentAdvice = '建议密切关注市场动态变化';
    }

    const summaryText = `${marketStatus}。${aiStatus}。${investmentAdvice}。`;

    const summaryData = {
        date: TODAY,
        lastUpdate: dayjs().format('YYYY-MM-DD HH:mm:ss'),
        summary: summaryText,
        highlights: [
            '全球政治格局相对稳定，中美关系保持沟通',
            'AI产业持续高热，国内外大模型竞争激烈',
            '产业政策利好频出，数字经济成为重点方向',
            '资本市场结构性行情明显，科技股表现分化'
        ],
        watchlist: [
            { type: 'event', content: '美联储议息会议及降息预期变化' },
            { type: 'market', content: '科技股估值修复及业绩兑现' }
        ]
    };

    await fs.writeJson(path.join(DATA_DIR, `summary-${TODAY}.json`), summaryData, { spaces: 2 });
    console.log('  ✓ 核心摘要已生成');
}

// 运行
fetchAll().catch(error => {
    console.error('总控脚本失败:', error);
    process.exit(1);
});
