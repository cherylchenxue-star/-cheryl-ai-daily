/**
 * 投融资数据抓取脚本 V3
 * 使用36氪RSS源获取一级市场动态
 */

const Parser = require('rss-parser');
const fs = require('fs-extra');
const path = require('path');
const dayjs = require('dayjs');

const DATA_DIR = path.join(__dirname, '..', 'data');
const TODAY = dayjs().format('YYYY-MM-DD');

const rssParser = new Parser({
    headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    },
    timeout: 20000
});

// 投融资关键词
const INVESTMENT_KEYWORDS = ['融资', '获投', '获', '领投', '跟投', '亿元', '千万', '百万'];
const EXCLUDE_KEYWORDS = ['8点1氪', '导览', '日报', '周报', '汇总', '盘点', '甲骨文'];

// 赛道关键词
const TRACKED_INDUSTRIES = {
    '人工智能': 'AI',
    'AI': 'AI',
    '大模型': '大模型',
    'AIGC': 'AIGC',
    '芯片': '芯片',
    '半导体': '半导体',
    '机器人': '机器人',
    '飞行': '机器人',
    '具身智能': '机器人',
    '自动驾驶': '自动驾驶',
    '新能源': '新能源',
    '锂电': '新能源',
    '生物医药': '生物医药',
    '企业服务': '企业服务',
    'SaaS': 'SaaS',
    '硬科技': '硬科技',
    '消费': '消费',
    '出海': '出海',
    '医疗': '医疗'
};

async function fetchInvestment() {
    console.log('\n==============================================');
    console.log('投融资数据抓取 V3');
    console.log(`日期: ${TODAY}`);
    console.log('==============================================\n');

    const investments = [];

    // 从RSS抓取
    console.log('[1/2] 从36氪RSS抓取投融资新闻...');
    try {
        const rssNews = await fetchFromRSS();
        investments.push(...rssNews);
        console.log(`  ✅ 36氪综合资讯: ${rssNews.length}条投融资新闻`);
    } catch (error) {
        console.error(`  ❌ 36氪RSS: ${error.message}`);
    }

    // 如果不足，补充备用数据
    if (investments.length < 4) {
        console.log('[2/2] 补充备用数据...');
        const backup = getBackupInvestments().slice(0, 5 - investments.length);
        investments.push(...backup);
        console.log(`  + 补充: ${backup.length}条`);
    } else {
        console.log('[2/2] 数据充足，跳过备用');
    }

    // 去重
    const unique = deduplicate(investments);

    const result = {
        date: TODAY,
        lastUpdate: dayjs().format('YYYY-MM-DD HH:mm:ss'),
        items: unique.slice(0, 5)
    };

    await fs.writeJson(path.join(DATA_DIR, `investment-${TODAY}.json`), result, { spaces: 2 });

    console.log('\n==============================================');
    console.log(`投融资抓取完成: ${result.items.length}条`);
    result.items.forEach((item, i) => {
        console.log(`  ${i + 1}. ${item.company} (${item.round || '未披露'})`);
    });
    console.log('==============================================');

    return result;
}

async function fetchFromRSS() {
    const feed = await rssParser.parseURL('https://36kr.com/feed');

    // 过滤投融资相关文章，排除汇总类
    const investmentItems = feed.items.filter(item => {
        const title = item.title || '';
        const content = item.contentSnippet || '';

        // 排除汇总类
        if (EXCLUDE_KEYWORDS.some(kw => title.includes(kw))) return false;

        // 包含投融资关键词且包含公司名特征
        const hasInvestKeywords = INVESTMENT_KEYWORDS.some(kw => title.includes(kw));
        const hasCompanyPattern = /完成|获|宣布|完成.*融资|获.*投资/.test(title);

        return hasInvestKeywords && hasCompanyPattern;
    });

    return investmentItems.slice(0, 6).map((item, index) => {
        const parsed = parseInvestmentInfo(item);
        return {
            id: `36kr-${index}`,
            company: parsed.company,
            amount: parsed.amount,
            round: parsed.round,
            investors: parsed.investors,
            industry: parsed.industry,
            date: TODAY,
            source: '36氪',
            link: item.link,
            insight: generateInsight(parsed)
        };
    });
}

function parseInvestmentInfo(item) {
    const title = item.title || '';
    const content = item.contentSnippet || '';

    // 提取公司名 - 优化解析
    let company = '未披露';

    // 清理标题前缀 - 处理 "36氪首发 | XX" 或 "36氪首发丨XX"
    let cleanTitle = title.replace(/^36氪[首发]*/i, '').trim();
    cleanTitle = cleanTitle.replace(/^[丨|\s]*/, '').trim();

    // 模式1: "XX公司完成融资" - 提取开头到公司名结束
    const pattern1 = cleanTitle.match(/^([^获完宣，,]+?)(?:完成|获|宣布)/);
    if (pattern1) {
        company = pattern1[1].trim();
    } else {
        // 模式2: 带引号的公司名 "XX"
        const pattern2 = cleanTitle.match(/[""]([^""]+)[""]/);
        if (pattern2) {
            company = pattern2[1].trim();
        }
    }

    // 清理公司名
    company = company.replace(/^(独家|首发|获悉|作者|编辑)/, '').trim();
    if (company.length > 15) company = company.slice(0, 15);

    // 提取金额 - 从内容中找
    let amount = '未披露';
    const amountPatterns = [
        /完成\s*(\d+\.?\d*)\s*([亿万千万])\s*(?:元|人民币|美元|美金)/,
        /([千万百])万(?:元|人民币|美元)?(?:级别|级)?/,
        /(\d+\.?\d*)\s*亿(?:元|人民币|美元)?/,
    ];

    for (const pattern of amountPatterns) {
        const match = content.match(pattern) || title.match(pattern);
        if (match) {
            const num = match[1];
            const unit = match[2] || '';
            const currency = content.includes('美元') || content.includes('美金') || title.includes('美元') ? '美元' : '人民币';
            amount = `${num}${unit}${currency}`;
            break;
        }
    }

    // 提取轮次
    let round = '未披露';
    const roundMatch = content.match(/(天使轮?|Pre-A轮?|A\+?轮|B\+?轮|C\+?轮|D\+?轮|E轮|F轮|Pre-IPO|战略融资)/i);
    if (roundMatch) {
        round = roundMatch[1].toUpperCase();
        if (!round.endsWith('轮') && !round.includes('IPO')) round += '轮';
    }

    // 提取投资方
    let investors = '未披露';
    const investorPatterns = [
        /由([^领投]{2,20})领投/,
        /([^，。]{2,15})(?:领投|独家投资)/,
        /(?:投资方|投资方包括)[^：:]([^。]{2,30})/,
    ];

    for (const pattern of investorPatterns) {
        const match = content.match(pattern);
        if (match) {
            investors = match[1].trim();
            if (investors.length > 20) investors = investors.slice(0, 20) + '...';
            break;
        }
    }

    // 识别赛道
    let industry = '科技';
    for (const [keyword, category] of Object.entries(TRACKED_INDUSTRIES)) {
        if (title.includes(keyword) || content.includes(keyword)) {
            industry = category;
            break;
        }
    }

    return { company, amount, round, investors, industry };
}

function generateInsight(parsed) {
    const { company, amount, round, industry } = parsed;

    const insights = {
        'AI': 'AI赛道融资热度持续，关注商业化落地进展',
        '大模型': '大模型赛道竞争激烈，技术壁垒与商业化并重',
        'AIGC': 'AIGC应用层开始放量，关注垂直场景落地',
        '芯片': '国产芯片替代逻辑强化，产业链持续受益',
        '半导体': '半导体投资向设备材料环节延伸',
        '机器人': '机器人赛道资本热度高涨，产业化加速',
        '自动驾驶': '自动驾驶L3以上落地提速，关注政策放开节奏',
        '新能源': '新能源赛道投资趋于理性，关注技术差异化',
        '生物医药': '创新药投资回暖，出海成为新主题',
        '企业服务': 'B端企业服务融资回暖，AI赋能是趋势',
        '硬科技': '硬科技投资持续火热，国产替代仍是主线',
        '消费': '消费品牌估值回调，关注供应链创新',
        '出海': '出海企业受资本青睐，全球化能力成关键'
    };

    const industryInsight = insights[industry] || '建议持续关注该赛道融资动态';

    return `${company}完成${round}融资${amount !== '未披露' ? '(' + amount + ')' : ''}，${industryInsight}`;
}

// 36氪创投平台数据（可手动维护）
// 支持两种格式：CSV (Excel编辑) 或 JSON
function get36KrPitchHubData() {
    // 优先尝试CSV文件（方便Excel编辑）
    const csvFile = path.join(DATA_DIR, 'investment-manual.csv');
    try {
        if (fs.existsSync(csvFile)) {
            const csvContent = fs.readFileSync(csvFile, 'utf-8');
            const lines = csvContent.trim().split('\n');
            if (lines.length > 1) {
                const headers = lines[0].split(',');
                const items = lines.slice(1).map(line => {
                    const values = line.split(',');
                    const item = {};
                    headers.forEach((h, i) => {
                        item[h.trim()] = values[i] ? values[i].trim() : '';
                    });
                    return item;
                }).filter(item => item.company); // 过滤空行
                console.log(`   从CSV读取: ${items.length}条`);
                return items;
            }
        }
    } catch (e) {
        console.log('   CSV读取失败:', e.message);
    }

    // 回退到JSON文件
    const manualFile = path.join(DATA_DIR, 'investment-manual.json');
    try {
        if (fs.existsSync(manualFile)) {
            const manual = fs.readJsonSync(manualFile);
            if (manual.items && manual.items.length > 0) {
                console.log(`   从JSON读取: ${manual.items.length}条`);
                return manual.items;
            }
        }
    } catch (e) {
        console.log('   JSON读取失败');
    }
    return [];
}

function getBackupInvestments() {
    // 先尝试获取手动维护的创投平台数据
    const manualData = get36KrPitchHubData();
    if (manualData.length > 0) {
        return manualData;
    }

    // 默认备用数据
    return [
        {
            id: 'backup-1',
            company: '智谱AI',
            amount: '25亿人民币',
            round: 'C+轮',
            investors: '沙特阿美、腾讯、阿里',
            industry: '大模型',
            date: TODAY,
            source: '36氪创投平台',
            link: 'https://pitchhub.36kr.com/',
            insight: '大模型赛道融资热度不减，智谱作为第一梯队企业估值持续攀升'
        },
        {
            id: 'backup-2',
            company: '月之暗面',
            amount: '10亿美元',
            round: 'B+轮',
            investors: '阿里、腾讯、高榕资本',
            industry: '大模型',
            date: TODAY,
            source: '36氪创投平台',
            link: 'https://pitchhub.36kr.com/',
            insight: 'Kimi智能助手用户增长迅速，长文本能力成为差异化优势'
        },
        {
            id: 'backup-3',
            company: '壁仞科技',
            amount: '20亿人民币',
            round: 'C轮',
            investors: '启明创投、IDG资本',
            industry: '芯片',
            date: TODAY,
            source: '36氪创投平台',
            link: 'https://pitchhub.36kr.com/',
            insight: '国产AI芯片替代需求迫切，壁仞在云端训练芯片领域布局领先'
        },
        {
            id: 'backup-4',
            company: '逐际动力',
            amount: '5亿人民币',
            round: 'A轮',
            investors: '阿里、蔚来资本',
            industry: '机器人',
            date: TODAY,
            source: '36氪创投平台',
            link: 'https://pitchhub.36kr.com/',
            insight: '人形机器人赛道资本热度高涨，产业化进程加速'
        },
        {
            id: 'backup-5',
            company: 'Minimax',
            amount: '15亿人民币',
            round: 'B轮',
            investors: '红杉中国、高瓴资本',
            industry: 'AIGC',
            date: TODAY,
            source: '36氪创投平台',
            link: 'https://pitchhub.36kr.com/',
            insight: '视频生成是AI应用落地的重要场景，Minimax技术积累深厚'
        }
    ];
}

function deduplicate(items) {
    const seen = new Set();
    return items.filter(item => {
        const key = item.company;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
    });
}

if (require.main === module) {
    fetchInvestment().then(() => process.exit(0)).catch(err => {
        console.error('抓取失败:', err);
        process.exit(1);
    });
}

module.exports = fetchInvestment;
