/**
 * 股票数据抓取脚本 - 使用 Longbridge CLI
 * 获取宏观指数、美股M7、港股业务标的、A股财税标的
 */

const { execSync } = require('child_process');
const fs = require('fs-extra');
const path = require('path');
const dayjs = require('dayjs');

const DATA_DIR = path.join(__dirname, '..', 'data');
const TODAY = dayjs().format('YYYY-MM-DD');

// 股票代码配置
const STOCK_CONFIG = {
    // 宏观指数
    indices: [
        { symbol: 'SPX.US', name: '标普500', market: '美股', flag: '🇺🇸' },
        { symbol: 'IXIC.US', name: '纳斯达克综合', market: '美股', flag: '🇺🇸' },
        { symbol: '000001.SH', name: '上证指数', market: 'A股', flag: '🇨🇳' },
        { symbol: '399001.SZ', name: '深证成指', market: 'A股', flag: '🇨🇳' },
        { symbol: '000688.SH', name: '科创50', market: 'A股', flag: '🇨🇳' },
        { symbol: '399006.SZ', name: '创业板指', market: 'A股', flag: '🇨🇳' },
        { symbol: 'HSI.HK', name: '恒生指数', market: '港股', flag: '🇭🇰' },
        { symbol: 'HSTECH.HK', name: '恒生科技指数', market: '港股', flag: '🇭🇰' },
    ],
    // 美股M7
    m7: [
        { symbol: 'NVDA.US', name: '英伟达', flag: '🇺🇸', desc: 'GTC大会催化，订单预期乐观' },
        { symbol: 'MSFT.US', name: '微软', flag: '🇺🇸', desc: 'AI服务收入超预期，Azure增长稳健' },
        { symbol: 'AAPL.US', name: '苹果', flag: '🇺🇸', desc: 'Vision Pro销量平淡，关注AI进展' },
        { symbol: 'GOOGL.US', name: '谷歌', flag: '🇺🇸', desc: 'Gemini企业版发布，估值修复中' },
        { symbol: 'AMZN.US', name: '亚马逊', flag: '🇺🇸', desc: 'AWS增速回升，电商业务稳健' },
        { symbol: 'META.US', name: 'Meta', flag: '🇺🇸', desc: 'Reels变现加速，AI推荐提升广告效率' },
        { symbol: 'TSLA.US', name: '特斯拉', flag: '🇺🇸', desc: '欧洲销量下滑，FSD入华待批' },
    ],
    // 港股业务相关标的
    hkStocks: [
        { symbol: '00700.HK', name: '腾讯控股', flag: '🇭🇰', desc: '游戏+云业务稳健，AI应用落地加速' },
        { symbol: '09988.HK', name: '阿里巴巴-W', flag: '🇭🇰', desc: '通义千问3.0发布，云业务增速回升' },
        { symbol: '03690.HK', name: '美团-W', flag: '🇭🇰', desc: '本地生活龙头，闪购业务高增长' },
        { symbol: '01810.HK', name: '小米集团-W', flag: '🇭🇰', desc: 'SU7销量超预期，AIoT生态扩张' },
        { symbol: '02513.HK', name: '智谱AI', flag: '🇭🇰', desc: '完成新一轮融资，大模型商业化加速' },
        { symbol: '00100.HK', name: 'Minimax', flag: '🇭🇰', desc: '视频生成模型能力领先，B端落地快' },
        { symbol: '01384.HK', name: '滴普科技', flag: '🇭🇰', desc: '完成B+轮融资，AI+财税赛道热门' },
        { symbol: '02706.HK', name: '海致科技', flag: '🇭🇰', desc: '企业评估AI系统受关注，C轮融资后估值提升' },
        { symbol: '00020.HK', name: '商汤-W', flag: '🇭🇰', desc: '大模型日日新能力迭代，亏损收窄' },
        { symbol: '06687.HK', name: '聚水潭', flag: '🇭🇰', desc: '电商SaaS龙头，AI客服产品上线' },
    ],
    // A股财税相关
    aStocks: [
        { symbol: '603171.SH', name: '税友股份', flag: '🇨🇳', desc: '财税SaaS龙头，金税四期受益标的' },
    ],
    // 美股对标
    usPeers: [
        { symbol: 'INTU.US', name: '财捷(Intuit)', flag: '🇺🇸', desc: '北美财税SaaS龙头，TurboTax母公司' },
    ]
};

async function fetchStockData() {
    console.log('开始抓取股票数据...');

    // 首先尝试使用 Python SDK 获取真实数据
    try {
        console.log('尝试使用 Python SDK 获取实时数据...');
        const pythonResult = await fetchWithPythonSDK();
        if (pythonResult) {
            console.log('Python SDK 获取数据成功！');
            return pythonResult;
        }
    } catch (error) {
        console.log('Python SDK 获取失败，回退到 CLI/mock:', error.message);
    }

    const result = {
        date: TODAY,
        lastUpdate: dayjs().format('YYYY-MM-DD HH:mm:ss'),
        indices: [],
        m7: [],
        hkStocks: [],
        aStocks: [],
        usPeers: [],
        marketCommentary: {
            us: '',
            cn: '',
            hk: ''
        }
    };

    try {
        // 获取宏观指数
        console.log('获取宏观指数...');
        result.indices = await fetchQuoteBatch(STOCK_CONFIG.indices);

        // 获取M7
        console.log('获取美股M7...');
        result.m7 = await fetchQuoteBatch(STOCK_CONFIG.m7);

        // 获取港股
        console.log('获取港股标的...');
        result.hkStocks = await fetchQuoteBatch(STOCK_CONFIG.hkStocks);

        // 获取A股
        console.log('获取A股标的...');
        result.aStocks = await fetchQuoteBatch(STOCK_CONFIG.aStocks);

        // 获取美股对标
        console.log('获取美股对标...');
        result.usPeers = await fetchQuoteBatch(STOCK_CONFIG.usPeers);

        // 生成市场解读（后续可由AI生成）
        result.marketCommentary = generateMarketCommentary(result);

        // 保存数据
        await fs.writeJson(path.join(DATA_DIR, `stocks-${TODAY}.json`), result, { spaces: 2 });
        console.log(`股票数据已保存: stocks-${TODAY}.json`);

        return result;
    } catch (error) {
        console.error('抓取股票数据失败:', error);
        throw error;
    }
}

// 使用 Python SDK 获取真实数据
async function fetchWithPythonSDK() {
    const scriptPath = path.join(__dirname, 'fetch_real_sdk.py');

    try {
        // 运行 Python 脚本
        const output = execSync(`python "${scriptPath}"`, {
            encoding: 'utf8',
            timeout: 60000,
            stdio: ['pipe', 'pipe', 'pipe']
        });

        console.log(output);

        // 读取生成的数据文件
        const dataPath = path.join(DATA_DIR, `stocks-${TODAY}.json`);
        if (fs.existsSync(dataPath)) {
            const data = await fs.readJson(dataPath);

            // 转换为统一格式
            return {
                date: data.date,
                lastUpdate: data.lastUpdate,
                indices: data.indices.map(idx => ({
                    symbol: idx.symbol,
                    name: idx.name,
                    market: idx.market,
                    flag: idx.flag === 'US' ? '🇺🇸' : idx.flag === 'HK' ? '🇭🇰' : '🇨🇳',
                    price: idx.price,
                    change: idx.change,
                    changePercent: idx.changePercent,
                    volume: idx.volume,
                    _source: 'real-time'
                })),
                m7: data.m7.map(stock => ({
                    symbol: stock.symbol,
                    name: stock.name,
                    flag: '🇺🇸',
                    price: stock.price,
                    change: stock.change,
                    changePercent: stock.changePercent,
                    _source: 'real-time'
                })),
                hkStocks: data.hkStocks.map(stock => ({
                    symbol: stock.symbol,
                    name: stock.name,
                    flag: '🇭🇰',
                    price: stock.price,
                    change: stock.change,
                    changePercent: stock.changePercent,
                    _source: 'real-time'
                })),
                aStocks: [],
                usPeers: [],
                marketCommentary: data.marketCommentary,
                _dataSource: 'Longbridge SDK (Real-time)'
            };
        }
    } catch (error) {
        console.error('Python SDK 执行失败:', error.message);
        throw error;
    }

    return null;
}

// 模拟股票数据（当Longbridge不可用时使用）
const MOCK_STOCK_DATA = {
    'SPX.US': { price: 5650.38, change: 47.52, changePercent: 0.85 },
    'IXIC.US': { price: 17850.22, change: 250.18, changePercent: 1.42 },
    '000001.SH': { price: 3345.86, change: -7.72, changePercent: -0.23 },
    '399001.SZ': { price: 10520.35, change: -25.14, changePercent: -0.24 },
    '000688.SH': { price: 1025.65, change: 15.38, changePercent: 1.52 },
    '399006.SZ': { price: 2125.45, change: -18.32, changePercent: -0.85 },
    'HSI.HK': { price: 23150.32, change: -104.58, changePercent: -0.45 },
    'HSTECH.HK': { price: 5250.18, change: -85.42, changePercent: -1.60 },
    // M7
    'NVDA.US': { price: 142.35, change: 4.35, changePercent: 3.15, marketCap: '3.48万亿' },
    'MSFT.US': { price: 432.18, change: 5.35, changePercent: 1.25, marketCap: '3.21万亿' },
    'AAPL.US': { price: 238.52, change: 1.62, changePercent: 0.68, marketCap: '3.62万亿' },
    'GOOGL.US': { price: 186.45, change: 3.39, changePercent: 1.85, marketCap: '2.31万亿' },
    'AMZN.US': { price: 198.72, change: 1.81, changePercent: 0.92, marketCap: '2.08万亿' },
    'META.US': { price: 625.18, change: 14.38, changePercent: 2.35, marketCap: '1.59万亿' },
    'TSLA.US': { price: 268.45, change: -3.40, changePercent: -1.25, marketCap: '0.86万亿' },
    // 港股
    '00700.HK': { price: 520.50, change: -4.45, changePercent: -0.85, marketCap: '4.85万亿', southboundFlow: '+12.5亿' },
    '09988.HK': { price: 128.30, change: -1.45, changePercent: -1.12, marketCap: '2.47万亿', southboundFlow: '+8.3亿' },
    '03690.HK': { price: 142.80, change: 2.85, changePercent: 2.04, marketCap: '8850亿', southboundFlow: '+5.2亿' },
    '01810.HK': { price: 18.52, change: 0.35, changePercent: 1.93, marketCap: '4620亿', southboundFlow: '+3.8亿' },
    '02513.HK': { price: 28.50, change: 1.58, changePercent: 5.85, marketCap: '285亿', southboundFlow: '-' },
    '00100.HK': { price: 45.20, change: 1.40, changePercent: 3.20, marketCap: '180亿', southboundFlow: '-' },
    '01384.HK': { price: 12.35, change: 0.53, changePercent: 4.50, marketCap: '45亿', southboundFlow: '-' },
    '02706.HK': { price: 35.80, change: 0.99, changePercent: 2.85, marketCap: '120亿', southboundFlow: '-' },
    '00020.HK': { price: 1.85, change: 0.06, changePercent: 3.35, marketCap: '620亿', southboundFlow: '+1.2亿' },
    '06687.HK': { price: 8.95, change: -0.05, changePercent: -0.55, marketCap: '65亿', southboundFlow: '-' },
    // A股
    '603171.SH': { price: 32.58, change: 1.25, changePercent: 3.99, marketCap: '125亿' },
    // 美股对标
    'INTU.US': { price: 625.85, change: 8.52, changePercent: 1.38, marketCap: '1750亿' }
};

async function fetchQuoteBatch(stocks) {
    const symbols = stocks.map(s => s.symbol).join(' ');

    try {
        // 检查 Longbridge CLI 是否可用
        execSync('longbridge --version', { encoding: 'utf8', timeout: 5000 });

        // 使用 Longbridge CLI 获取行情
        const output = execSync(`longbridge quote ${symbols}`, {
            encoding: 'utf8',
            timeout: 30000
        });

        // 解析输出
        const lines = output.trim().split('\n');
        const results = [];

        for (const stock of stocks) {
            const line = lines.find(l => l.includes(stock.symbol) || l.includes(stock.symbol.split('.')[0]));

            if (line) {
                const parts = line.trim().split(/\s+/);
                results.push({
                    ...stock,
                    price: parseFloat(parts[1]) || 0,
                    change: parseFloat(parts[2]) || 0,
                    changePercent: parseFloat(parts[3]?.replace('%', '')) || 0,
                    volume: parts[4] || '-',
                    marketCap: '-',
                    southboundFlow: null,
                    northboundFlow: null
                });
            } else {
                // 使用模拟数据
                results.push(getMockStockData(stock));
            }
        }

        return results;
    } catch (error) {
        console.log(`Longbridge CLI 不可用，使用模拟数据: ${error.message}`);
        // 返回模拟数据
        return stocks.map(s => getMockStockData(s));
    }
}

function getMockStockData(stock) {
    const mock = MOCK_STOCK_DATA[stock.symbol] || { price: 0, change: 0, changePercent: 0 };

    return {
        ...stock,
        price: mock.price,
        change: mock.change,
        changePercent: mock.changePercent,
        volume: mock.volume || '-',
        marketCap: mock.marketCap || '-',
        southboundFlow: mock.southboundFlow || null,
        _note: '模拟数据'
    };
}

function generateMarketCommentary(data) {
    // 简化版市场解读，后续可由Claude生成
    return {
        us: "M7集体上涨，英伟达领涨，市场对AI商业化落地信心增强",
        cn: "科创50逆势上涨，资金聚焦硬科技，财税信息化板块活跃",
        hk: "南向资金抄底科技股，内外资分歧明显，关注财报指引"
    };
}

// 如果直接运行此脚本
if (require.main === module) {
    fetchStockData().then(() => {
        console.log('股票数据抓取完成');
        process.exit(0);
    }).catch(error => {
        console.error('抓取失败:', error);
        process.exit(1);
    });
}

module.exports = fetchStockData;
