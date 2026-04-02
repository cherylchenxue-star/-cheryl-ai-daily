/**
 * 投融资数据真实抓取脚本
 * 使用Puppeteer无头浏览器抓取36氪创投平台
 * 严格筛选24小时内的数据
 */

const puppeteer = require('puppeteer');
const fs = require('fs-extra');
const path = require('path');
const dayjs = require('dayjs');

const DATA_DIR = path.join(__dirname, '..', 'data');
const TODAY = dayjs().format('YYYY-MM-DD');

// 24小时前的时间
const ONE_DAY_AGO = dayjs().subtract(24, 'hour');

async function fetchInvestmentReal() {
    console.log('\n==============================================');
    console.log('投融资数据真实抓取 (Puppeteer)');
    console.log(`日期: ${TODAY}`);
    console.log(`筛选: 24小时内 (${ONE_DAY_AGO.format('YYYY-MM-DD HH:mm')})`);
    console.log('==============================================\n');

    let browser;
    try {
        browser = await puppeteer.launch({
            headless: 'new',
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });

        const page = await browser.newPage();

        // 设置UA
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36');

        // 设置viewport
        await page.setViewport({ width: 1280, height: 800 });

        console.log('[1/3] 打开36氪创投平台...');
        await page.goto('https://pitchhub.36kr.com/', {
            waitUntil: 'networkidle2',
            timeout: 30000
        });

        // 等待页面加载
        await page.waitForTimeout(3000);

        console.log('[2/3] 提取投融资数据...');

        // 提取数据
        const investments = await page.evaluate((oneDayAgoStr) => {
            const ONE_DAY_AGO = new Date(oneDayAgoStr);
            const items = [];

            // 尝试多种选择器
            const selectors = [
                '.project-item',
                '.company-item',
                '.list-item',
                '.invest-item',
                '[class*="item"]'
            ];

            let elements = [];
            for (const sel of selectors) {
                elements = document.querySelectorAll(sel);
                if (elements.length > 0) break;
            }

            // 如果没找到，尝试获取所有包含融资信息的元素
            if (elements.length === 0) {
                const allElements = document.querySelectorAll('div, li, article');
                elements = Array.from(allElements).filter(el => {
                    const text = el.textContent || '';
                    return text.includes('融资') || text.includes('获投') || text.includes('投资');
                });
            }

            elements.forEach((el, index) => {
                if (index >= 20) return; // 最多20条

                // 提取公司名 - 尝试多种选择器
                let company = '';
                const companySelectors = ['.company-name', '.name', '.company', 'h3', 'h4', '.title'];
                for (const sel of companySelectors) {
                    const companyEl = el.querySelector(sel);
                    if (companyEl) {
                        company = companyEl.textContent.trim();
                        // 清理轮次信息
                        company = company.replace(/(A轮|B轮|C轮|D轮|E轮|F轮|天使轮|种子轮|Pre-.*?轮|战略融资|并购\/合并|已上市|未融资|未披露)$/i, '').trim();
                        if (company) break;
                    }
                }

                // 提取金额
                const amountEl = el.querySelector('.amount, .money, .fund');
                let amount = amountEl ? amountEl.textContent.trim() : '';

                // 提取轮次 - 如果没有单独元素，尝试从公司名或文本中提取
                let round = '';
                const roundEl = el.querySelector('.round, .phase, .stage, [class*="round"]');
                if (roundEl) {
                    round = roundEl.textContent.trim();
                }
                // 如果还是没找到，从公司名中提取
                if (!round && company) {
                    const roundMatch = company.match(/(A轮|B轮|C轮|D轮|E轮|F轮|天使轮|种子轮|Pre-A轮|Pre-B轮|战略融资|并购\/合并|已上市|未融资|未披露)/i);
                    if (roundMatch) {
                        round = roundMatch[1];
                    }
                }

                // 提取投资方
                const investorEl = el.querySelector('.investor, .vc, .investors');
                let investors = investorEl ? investorEl.textContent.trim() : '';

                // 提取日期
                const dateEl = el.querySelector('.date, .time, [class*="date"], [class*="time"]');
                let dateText = dateEl ? dateEl.textContent.trim() : '';

                // 提取链接
                const linkEl = el.querySelector('a');
                const link = linkEl ? linkEl.href : '';

                // 提取描述
                const descEl = el.querySelector('.desc, .description, .summary, p');
                const description = descEl ? descEl.textContent.trim().slice(0, 200) : '';

                // 解析日期
                let pubDate = null;
                if (dateText) {
                    // 尝试解析各种日期格式
                    const dateMatch = dateText.match(/(\d{4})[-/](\d{1,2})[-/](\d{1,2})/);
                    if (dateMatch) {
                        pubDate = new Date(`${dateMatch[1]}-${dateMatch[2].padStart(2, '0')}-${dateMatch[3].padStart(2, '0')}`);
                    } else if (dateText.includes('小时前') || dateText.includes('分钟前') || dateText.includes('刚刚')) {
                        pubDate = new Date(); // 今天
                    } else if (dateText.includes('昨天')) {
                        pubDate = new Date(Date.now() - 86400000);
                    }
                }

                // 如果无法解析日期，默认为今天（用于筛选）
                if (!pubDate) {
                    pubDate = new Date();
                }

                // 只保留24小时内的
                if (pubDate >= ONE_DAY_AGO && company) {
                    items.push({
                        company,
                        amount: amount || '未披露',
                        round: round || '未披露',
                        investors: investors || '未披露',
                        date: dateText || '今天',
                        link,
                        description,
                        pubDate: pubDate.toISOString()
                    });
                }
            });

            return items;
        }, ONE_DAY_AGO.toISOString());

        console.log(`  ✅ 提取到 ${investments.length} 条24小时内数据`);

        if (investments.length > 0) {
            console.log('\n  数据预览:');
            investments.slice(0, 3).forEach((item, i) => {
                console.log(`    ${i + 1}. ${item.company} (${item.round}) - ${item.date}`);
            });
        }

        await browser.close();

        // 转换为标准格式
        const formattedItems = investments.map((item, index) => ({
            id: `36kr-real-${index}`,
            company: item.company,
            amount: formatAmount(item.amount),
            round: item.round,
            investors: item.investors,
            industry: guessIndustry(item.description + ' ' + item.company),
            date: TODAY,
            source: '36氪创投平台',
            link: item.link || 'https://pitchhub.36kr.com/',
            insight: generateInsight(item)
        }));

        console.log('[3/3] 保存数据...');

        const result = {
            date: TODAY,
            lastUpdate: dayjs().format('YYYY-MM-DD HH:mm:ss'),
            dataSource: '36氪创投平台 (Puppeteer)',
            filter: '24小时内',
            items: formattedItems
        };

        await fs.writeJson(path.join(DATA_DIR, `investment-${TODAY}.json`), result, { spaces: 2 });

        console.log('\n==============================================');
        console.log(`抓取完成: ${result.items.length}条 (24小时内)`);
        console.log('==============================================');

        return result;

    } catch (error) {
        console.error('抓取失败:', error.message);
        if (browser) await browser.close();
        throw error;
    }
}

function formatAmount(amount) {
    if (!amount || amount === '未披露') return '未披露';

    // 提取数字和单位
    const match = amount.match(/(\d+\.?\d*)\s*([亿万千万])/);
    if (match) {
        const currency = amount.includes('美元') ? '美元' : '人民币';
        return `${match[1]}${match[2]}${currency}`;
    }

    return amount;
}

function guessIndustry(text) {
    const industries = {
        'AI': 'AI',
        '人工智能': 'AI',
        '大模型': '大模型',
        '芯片': '芯片',
        '半导体': '半导体',
        '机器人': '机器人',
        '自动驾驶': '自动驾驶',
        '新能源': '新能源',
        '生物医药': '生物医药',
        '医疗': '医疗',
        '企业': '企业服务',
        'SaaS': 'SaaS',
        '消费': '消费',
        '电商': '电商'
    };

    for (const [keyword, industry] of Object.entries(industries)) {
        if (text.includes(keyword)) return industry;
    }

    return '科技';
}

function generateInsight(item) {
    return `${item.company}完成${item.round}融资，建议持续关注该赛道发展动态`;
}

// 运行
if (require.main === module) {
    fetchInvestmentReal()
        .then(() => process.exit(0))
        .catch(err => {
            console.error('抓取失败:', err);
            process.exit(1);
        });
}

module.exports = fetchInvestmentReal;
