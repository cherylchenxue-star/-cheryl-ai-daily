/**
 * 新闻数据抓取脚本 V4
 * 严格按用户需求实现白名单和关键词过滤
 */

const Parser = require('rss-parser');
const fs = require('fs-extra');
const path = require('path');
const dayjs = require('dayjs');

const DATA_DIR = path.join(__dirname, '..', 'data');
const TODAY = dayjs().format('YYYY-MM-DD');
const ONE_DAY_AGO = dayjs().subtract(24, 'hour');

const rssParser = new Parser({
    headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    },
    timeout: 20000
});

// RSS源配置
const RSS_SOURCES = {
    // 政治新闻
    politics: {
        international: [
            { name: '中新网-国际新闻', url: 'https://www.chinanews.com.cn/rss/world.xml' }
        ],
        domestic: [
            { name: '中新网-时政新闻', url: 'https://www.chinanews.com.cn/rss/china.xml' }
        ]
    },
    // AI新闻
    ai: {
        international: [
            { name: 'AIbase中文', url: 'https://suy123xb.github.io/aibase_news_rss/feed.xml' }
        ],
        domestic: [
            { name: '36氪快讯', url: 'https://36kr.com/feed-newsflash' },
            { name: 'AIbase中文-国内', url: 'https://suy123xb.github.io/aibase_news_rss/feed.xml' }
        ]
    }
};

// 政治新闻关键词配置
const POLITICS_KEYWORDS = {
    // 国际政治：国际级事件、重大政策、关键经济数据、国际格局变动、中美关系、特朗普政府、关税
    international: {
        // 核心关键词 - 必须包含这些才算相关
        core: ['关税', '贸易', '中美', '特朗普', '拜登', '美国', '美联储', '加息', '降息', '汇率', '美元', '原油', '黄金', '地缘', '冲突', '协议', '谈判', '制裁', '经贸', '外交', '北约', 'G7', 'G20', '世贸', 'WTO', '出口', '进口', '壁垒', '征税', '反倾销', '补贴', '供应链', '脱钩', '限制', '禁令'],
        // 一般关键词 - 包含这些增加相关性
        general: ['欧盟', '俄罗斯', '乌克兰', '中东', '联合国', '世卫', '世界银行', 'IMF', '通胀', '衰退', '增长', 'GDP', 'CPI', 'PMI', '就业', '非农'],
        // 优先级排序 - 越靠前权重越高
        priority: ['关税', '中美', '贸易', '特朗普', '拜登', '制裁', '出口', '进口', '供应链', '脱钩', '美联储', '加息', '降息', '经贸', '谈判', '协议', '冲突', '地缘']
    },
    // 国内政治：国家级事件、关键政策发布、国家领导、地方产业
    domestic: {
        core: ['国务院', '发改委', '工信部', '财政部', '央行', '总书记', '总理', '政策', '规划', '法规', '条例', '意见', '通知', '产业', '经济', '外贸', '科技', '创新', '数字化', '改革', '开放'],
        general: ['京津冀', '长三角', '粤港澳', '大湾区', '海南', '自贸区', '新区', '补贴', '扶持', '奖励', '专项资金'],
        priority: ['国务院', '发改委', '工信部', '总书记', '总理', '政策', '规划', '产业', '科技', '创新', '经济']
    }
};

// AI公司白名单
const AI_WHITELIST = {
    // 海外AI公司
    international: ['Tesla', 'Google', 'Alphabet', 'Apple', 'OpenAI', 'Anthropic', 'Microsoft', 'Meta', 'Facebook', 'Instagram', 'WhatsApp', 'NVIDIA', 'Amazon', 'AWS', 'Claude', 'GPT', 'ChatGPT', 'Gemini', 'Llama', 'Copilot', 'Azure', 'xAI', 'Grok', 'DeepMind', 'Waymo', 'Optimus', 'DALL-E', 'Sora'],
    // 国内AI公司
    domestic: ['Zhipu', '智谱', 'MiniMax', '稀宇', 'Moonshot', '月之暗面', 'Kimi', 'Tencent', '腾讯', 'Alibaba', '阿里', '通义千问', 'Qwen', 'ByteDance', '字节', '豆包', 'DeepSeek', '深度求索', 'Xiaomi', '小米', 'Baidu', '百度', '文心一言', 'Huawei', '华为', '盘古', '昇腾', 'MindSpore', '商汤', 'SenseTime', '讯飞', '科大讯飞', '理想', 'LiAuto', '小鹏', 'Xpeng', '蔚来', 'NIO', '比亚迪', 'BYD', '零一万物', '01.AI', '百川', 'Baichuan', '智元', 'AgiBot']
};

// AI内容类型关键词
const AI_CONTENT_TYPES = ['大模型', '模型', 'AI', '人工智能', '生成式', 'LLM', '算法', '训练', '推理', '算力', '芯片', 'GPU', 'NPU', '落地', '应用', '产品', '发布', '上线', '升级', '融资', 'IPO', '上市', '合作', '战略', '技术突破'];

async function fetchNewsV3() {
    console.log('\n==============================================');
    console.log('新闻数据抓取脚本 V4 - 严格白名单过滤');
    console.log(`日期: ${TODAY}`);
    console.log('==============================================\n');

    const result = {
        date: TODAY,
        lastUpdate: dayjs().format('YYYY-MM-DD HH:mm:ss'),
        international: [],
        domestic: [],
        aiInternational: [],
        aiDomestic: [],
        errors: []
    };

    // 1. 抓取国际政治新闻（2条）
    console.log('[1/4] 抓取国际政治新闻...');
    for (const source of RSS_SOURCES.politics.international) {
        try {
            const news = await fetchPoliticsFromRSS(source, 'international');
            result.international.push(...news);
            console.log(`  ✅ ${source.name}: ${news.length}条符合标准`);
        } catch (error) {
            console.error(`  ❌ ${source.name}: ${error.message}`);
            result.errors.push({ source: source.name, error: error.message });
        }
    }

    // 2. 抓取国内政治新闻（2条）
    console.log('[2/4] 抓取国内政治新闻...');
    for (const source of RSS_SOURCES.politics.domestic) {
        try {
            const news = await fetchPoliticsFromRSS(source, 'domestic');
            result.domestic.push(...news);
            console.log(`  ✅ ${source.name}: ${news.length}条符合标准`);
        } catch (error) {
            console.error(`  ❌ ${source.name}: ${error.message}`);
            result.errors.push({ source: source.name, error: error.message });
        }
    }

    // 3. 抓取海外AI新闻（4条）
    console.log('[3/4] 抓取海外AI动态...');
    for (const source of RSS_SOURCES.ai.international) {
        try {
            const news = await fetchAIFromRSS(source, 'international');
            result.aiInternational.push(...news);
            console.log(`  ✅ ${source.name}: ${news.length}条符合标准`);
        } catch (error) {
            console.error(`  ❌ ${source.name}: ${error.message}`);
            result.errors.push({ source: source.name, error: error.message });
        }
    }

    // 4. 抓取国内AI新闻（4条）
    console.log('[4/4] 抓取国内AI动态...');
    for (const source of RSS_SOURCES.ai.domestic) {
        try {
            const news = await fetchAIFromRSS(source, 'domestic');
            result.aiDomestic.push(...news);
            console.log(`  ✅ ${source.name}: ${news.length}条符合标准`);
        } catch (error) {
            console.error(`  ❌ ${source.name}: ${error.message}`);
            result.errors.push({ source: source.name, error: error.message });
        }
    }

    // 严格限制数量
    result.international = deduplicateAndSort(result.international).slice(0, 2);
    result.domestic = deduplicateAndSort(result.domestic).slice(0, 2);
    result.aiInternational = deduplicateAndSort(result.aiInternational).slice(0, 4);
    result.aiDomestic = deduplicateAndSort(result.aiDomestic).slice(0, 4);

    // 保存数据
    await saveNewsData(result);

    console.log('\n==============================================');
    console.log('抓取完成！');
    console.log(`国际政治: ${result.international.length}条`);
    console.log(`国内政治: ${result.domestic.length}条`);
    console.log(`海外AI: ${result.aiInternational.length}条`);
    console.log(`国内AI: ${result.aiDomestic.length}条`);
    console.log('==============================================');

    return result;
}

// 抓取政治新闻
async function fetchPoliticsFromRSS(source, type) {
    const feed = await rssParser.parseURL(source.url);
    const keywords = POLITICS_KEYWORDS[type];

    const filtered = feed.items
        .filter(item => isWithin24Hours(item.pubDate || item.isoDate))
        .filter(item => {
            const text = (item.title + ' ' + (item.contentSnippet || item.content || '')).toLowerCase();
            // 必须包含至少一个核心关键词或一般关键词
            const hasCore = keywords.core.some(kw => text.includes(kw.toLowerCase()));
            const hasGeneral = keywords.general.some(kw => text.includes(kw.toLowerCase()));
            return hasCore || hasGeneral;
        })
        .map((item, index) => {
            const title = cleanText(item.title || '');
            const content = cleanText((item.contentSnippet || item.content || '').slice(0, 300));
            const summary = generatePoliticsSummary(title, content);
            const insight = generatePoliticsInsight(title, content, type);
            const priorityScore = calculatePoliticsPriorityScore(title, content, keywords.priority);

            return {
                id: `${source.name}-${index}`,
                title: title,
                link: item.link || '',
                summary: summary,
                content: content,
                pubDate: item.pubDate || item.isoDate || TODAY,
                source: source.name,
                category: type === 'international' ? 'international' : 'domestic',
                timeAgo: getTimeAgo(item.pubDate || item.isoDate),
                businessInsight: insight,
                priorityScore: priorityScore // 添加优先级分数用于排序
            };
        });

    // 按优先级分数排序（分数高的在前）
    return filtered.sort((a, b) => b.priorityScore - a.priorityScore);
}

// 抓取AI新闻
async function fetchAIFromRSS(source, type) {
    const feed = await rssParser.parseURL(source.url);
    const whitelist = AI_WHITELIST[type === 'international' ? 'international' : 'domestic'];

    const filtered = feed.items
        .filter(item => isWithin24Hours(item.pubDate || item.isoDate))
        .filter(item => {
            const text = item.title + ' ' + (item.contentSnippet || item.content || '');
            // 必须包含白名单中的公司
            const hasWhitelistCompany = whitelist.some(company =>
                text.toLowerCase().includes(company.toLowerCase())
            );
            // 必须包含AI内容类型关键词
            const hasAIContent = AI_CONTENT_TYPES.some(kw =>
                text.toLowerCase().includes(kw.toLowerCase())
            );
            return hasWhitelistCompany && hasAIContent;
        })
        .map((item, index) => {
            const title = cleanText(item.title || '');
            const content = cleanText((item.contentSnippet || item.content || '').slice(0, 300));
            const summary = generateAISummary(title, content);
            const insight = generateAIInsight(title, content, type);

            return {
                id: `${source.name}-${index}`,
                title: title,
                link: item.link || '',
                summary: summary,
                content: content,
                pubDate: item.pubDate || item.isoDate || TODAY,
                source: source.name,
                category: type === 'international' ? 'ai-international' : 'ai-domestic',
                timeAgo: getTimeAgo(item.pubDate || item.isoDate),
                businessInsight: insight
            };
        });

    return filtered;
}

// 生成政治新闻摘要（50字内）
function generatePoliticsSummary(title, content) {
    // 提取核心信息：事件核心、关键主体、核心数据/结论
    let summary = content.slice(0, 80);

    // 清理修饰词
    summary = summary
        .replace(/据悉|据了解|据报道|值得注意的是|业内人士指出/g, '')
        .replace(/[^。]*表示[^，]*，/g, '')
        .trim();

    // 限制50字
    if (summary.length > 50) {
        summary = summary.slice(0, 47) + '...';
    }

    return summary;
}

// 生成政治新闻深度解读
function generatePoliticsInsight(title, content, type) {
    const text = (title + ' ' + content).toLowerCase();

    if (type === 'international') {
        // 关税/贸易相关（最高优先级）
        if (text.includes('关税') || text.includes('贸易战') || text.includes('贸易壁垒') || text.includes('301调查')) {
            return '关税政策变动将直接冲击进出口成本，建议本周内启动供应链风险评估，锁定远期汇率对冲，并制定替代采购方案。';
        }
        if (text.includes('中美') && (text.includes('贸易') || text.includes('经济'))) {
            return '中美经贸关系变化影响供应链布局，建议评估产业链转移可行性，建立多元化供应渠道，降低单一市场依赖。';
        }
        if (text.includes('出口管制') || text.includes('技术封锁') || text.includes('芯片') || text.includes('半导体')) {
            return '出口管制扩大影响关键技术获取，建议加速国产替代方案评估，调整技术路线，储备替代供应商。';
        }
        if (text.includes('制裁') || text.includes('实体清单')) {
            return '制裁扩大影响技术供应链，建议评估国产替代可行性，调整采购策略，建立合规审查机制。';
        }
        if (text.includes('贸易') || text.includes('出口') || text.includes('进口')) {
            return '贸易政策变化影响跨境业务，建议建立政策跟踪机制，评估对现有合同履行的影响，及时调整物流方案。';
        }
        if (text.includes('美联储') || text.includes('加息') || text.includes('降息')) {
            return '货币政策变化影响融资成本，建议下月重新评估海外融资结构，关注美元走势，锁定汇率风险。';
        }
        if (text.includes('汇率') || text.includes('美元') || text.includes('人民币')) {
            return '汇率波动影响汇兑损益，建议评估外汇敞口，使用远期/期权等工具对冲，优化跨境资金配置。';
        }
        if (text.includes('地缘') || text.includes('冲突') || text.includes('战争')) {
            return '地缘政治风险上升影响全球供应链，建议评估关键原材料库存，制定应急预案，分散供应来源。';
        }
        return '国际局势变化可能影响跨境业务，建议持续关注并制定应对预案。';
    } else {
        if (text.includes('政策') || text.includes('规划')) {
            return '政策利好释放产业红利，建议下月启动补贴申报，争取政策支持。';
        }
        if (text.includes('科技') || text.includes('创新')) {
            return '科技创新政策利好硬科技企业，建议立项研发投入，申请税收优惠。';
        }
        if (text.includes('产业')) {
            return '产业政策明确发展方向，建议调整业务布局，抢占市场先机。';
        }
        return '国内政策动向影响产业发展，建议评估对业务的具体影响并调整策略。';
    }
}

// 生成AI新闻摘要（50字内）
function generateAISummary(title, content) {
    let summary = content.slice(0, 80);

    // 清理修饰词
    summary = summary
        .replace(/据悉|据了解|据报道|值得注意的是|业内人士指出/g, '')
        .replace(/[^。]*表示[^，]*，/g, '')
        .trim();

    // 限制50字
    if (summary.length > 50) {
        summary = summary.slice(0, 47) + '...';
    }

    return summary;
}

// 生成AI新闻深度解读
function generateAIInsight(title, content, type) {
    const text = (title + ' ' + content).toLowerCase();

    if (type === 'international') {
        if (text.includes('openai') || text.includes('gpt') || text.includes('claude')) {
            return '海外大模型能力持续突破，建议本月试用评估，规划AI应用落地场景。';
        }
        if (text.includes('google') || text.includes('gemini')) {
            return 'Google AI战略加速，建议关注搜索/广告AI化趋势，评估业务替代风险。';
        }
        if (text.includes('microsoft') || text.includes('copilot')) {
            return '微软AI商业化加速，建议评估办公软件AI化需求，考虑采购试点。';
        }
        if (text.includes('nvidia') || text.includes('芯片')) {
            return '算力军备竞赛持续，建议关注国产算力替代，评估算力采购策略。';
        }
        if (text.includes('tesla') || text.includes('optimus')) {
            return '特斯拉AI/机器人进展加速，建议关注自动驾驶和机器人产业链机会。';
        }
        return '海外AI技术进展加速，建议跟踪技术路线变化，评估对业务的影响。';
    } else {
        if (text.includes('阿里') || text.includes('通义')) {
            return '阿里大模型能力跃升，建议评估阿里云AI服务，考虑接入通义API。';
        }
        if (text.includes('百度') || text.includes('文心')) {
            return '百度AI商业化提速，建议关注文心一言B端应用，评估合作机会。';
        }
        if (text.includes('字节') || text.includes('豆包')) {
            return '字节AI产品快速迭代，建议关注流量入口AI化，评估营销新机会。';
        }
        if (text.includes('智谱') || text.includes('zhipu')) {
            return '智谱大模型融资活跃，建议关注智谱生态，评估接入或合作可能。';
        }
        if (text.includes('华为') || text.includes('昇腾')) {
            return '华为昇腾生态扩张，建议评估国产算力方案，降低供应链风险。';
        }
        if (text.includes('小米') || text.includes('小鹏') || text.includes('理想')) {
            return '智能汽车AI化加速，建议关注智能驾驶产业链，评估投资或合作机会。';
        }
        return '国内AI产业快速发展，建议关注产业机会，评估AI应用落地场景。';
    }
}

// 计算政治新闻优先级分数
function calculatePoliticsPriorityScore(title, content, priorityKeywords) {
    if (!title) return 0;
    const text = (title + ' ' + (content || '')).toLowerCase();
    let score = 0;

    // 优先级关键词权重（越靠前权重越高）
    priorityKeywords.forEach((kw, index) => {
        const kwLower = kw.toLowerCase();
        // 标题中出现权重更高
        if (title.toLowerCase().includes(kwLower)) {
            score += (priorityKeywords.length - index) * 3;
        }
        // 内容中出现
        if (content && content.toLowerCase().includes(kwLower)) {
            score += (priorityKeywords.length - index);
        }
    });

    // 特别关注：关税/中美贸易相关的新闻额外加分
    const tradeKeywords = ['关税', '中美贸易', '贸易战', '贸易摩擦', '贸易壁垒', '出口管制', '技术封锁', '301调查', '反倾销', '反补贴'];
    tradeKeywords.forEach(kw => {
        if (text.includes(kw.toLowerCase())) {
            score += 20; // 高额加分
        }
    });

    return score;
}

// 检查是否在24小时内
function isWithin24Hours(dateString) {
    if (!dateString) return true;
    const date = dayjs(dateString);
    return date.isAfter(ONE_DAY_AGO) || date.isSame(ONE_DAY_AGO, 'day');
}

// 按优先级排序
function sortByPriority(news, priorityKeywords) {
    return news.sort((a, b) => {
        const scoreA = calculatePriorityScore(a.title, priorityKeywords);
        const scoreB = calculatePriorityScore(b.title, priorityKeywords);
        return scoreB - scoreA;
    });
}

// 计算优先级得分
function calculatePriorityScore(title, priorityKeywords) {
    if (!title) return 0;
    const lowerTitle = title.toLowerCase();
    let score = 0;
    priorityKeywords.forEach((kw, index) => {
        if (lowerTitle.includes(kw.toLowerCase())) {
            // 越靠前的关键词权重越高
            score += priorityKeywords.length - index;
        }
    });
    return score;
}

// 去重并排序
function deduplicateAndSort(news) {
    const seen = new Set();
    const unique = news.filter(item => {
        const key = item.title ? item.title.slice(0, 30) : '';
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
    });

    return unique.sort((a, b) => new Date(b.pubDate) - new Date(a.pubDate));
}

// 保存新闻数据
async function saveNewsData(result) {
    // 政治新闻
    const politicsData = {
        date: TODAY,
        lastUpdate: dayjs().format('YYYY-MM-DD HH:mm:ss'),
        items: [...result.international, ...result.domestic]
    };

    // AI新闻
    const aiNewsData = {
        date: TODAY,
        lastUpdate: dayjs().format('YYYY-MM-DD HH:mm:ss'),
        items: [...result.aiInternational, ...result.aiDomestic]
    };

    // 使用原生fs.writeFile保存UTF-8编码的JSON（避免中文被转义）
    const writeJsonFile = async (filePath, data) => {
        const jsonStr = JSON.stringify(data, null, 2);
        await fs.writeFile(filePath, jsonStr, 'utf8');
    };

    await writeJsonFile(path.join(DATA_DIR, `politics-${TODAY}.json`), politicsData);
    await writeJsonFile(path.join(DATA_DIR, `ai-news-${TODAY}.json`), aiNewsData);
    await writeJsonFile(path.join(DATA_DIR, `news-full-${TODAY}.json`), result);

    console.log(`\n数据已保存:`);
    console.log(`  - politics-${TODAY}.json (${politicsData.items.length}条)`);
    console.log(`  - ai-news-${TODAY}.json (${aiNewsData.items.length}条)`);
    console.log(`  - news-full-${TODAY}.json`);
}

// 清理文本
function cleanText(text) {
    if (!text) return '';
    return text
        .replace(/\s+/g, ' ')
        .replace(/[\n\r\t]/g, ' ')
        .trim();
}

// 获取时间 ago
function getTimeAgo(dateString) {
    if (!dateString) return '刚刚';
    const date = new Date(dateString);
    const now = new Date();
    const diff = Math.floor((now - date) / (1000 * 60 * 60));

    if (diff < 1) return '刚刚';
    if (diff < 24) return `${diff}h`;
    return `${Math.floor(diff / 24)}d`;
}

if (require.main === module) {
    fetchNewsV3().then(() => process.exit(0)).catch(err => {
        console.error('抓取失败:', err);
        process.exit(1);
    });
}

module.exports = fetchNewsV3;
