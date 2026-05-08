#!/usr/bin/env python3
"""Generate all HSK prep guide content for all 7 levels."""

import json, os, re
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # v2-weasyprint root

# ── POS mapping: Chinese → English ──
POS_MAP = {
    '名': 'noun',
    '动': 'verb',
    '形': 'adjective',
    '副': 'adverb',
    '介': 'preposition',
    '连': 'conjunction',
    '助': 'particle',
    '代': 'pronoun',
    '叹': 'interjection',
    '拟': 'onomatopoeia',
    '拟声': 'onomatopoeia',
    '象声': 'onomatopoeia',
    '量': 'classifier',
    '数': 'numeral',
    '方位': 'localizer',
    '前缀': 'prefix',
    '后缀': 'suffix',
    '数量': 'numeral+classifier',
    '': '',
}

def translate_pos(pos):
    """Convert Chinese POS tag(s) to English. Handles compound tags like '名、量'."""
    pos = pos.strip()
    if not pos:
        return ''
    # Split on common delimiters
    parts = re.split(r'[、,/|]', pos)
    translated = []
    for p in parts:
        p = p.strip()
        translated.append(POS_MAP.get(p, p))
    return ', '.join(t for t in translated if t)


# ── Minimal English translation map for common HSK words ──
# Covers the most frequently tested HSK 1-3 vocabulary.
# For words not in this map, the vocab table will show the Chinese word itself
# as a fallback in the English column.
COMMON_TRANSLATIONS = {
    # HSK 1 core
    '八': 'eight', '爸爸': 'father', '吧': '[particle]', '白天': 'daytime',
    '包子': 'steamed bun', '杯': 'cup (classifier)', '杯子': 'cup',
    '北京': 'Beijing', '本': 'bound volume (classifier)', '不': 'not',
    '不客气': "you're welcome", '菜': 'dish/vegetable', '吃': 'eat',
    '吃饭': 'eat (a meal)', '喝茶': 'drink tea', '大': 'big',
    '的': '[possessive/descriptive particle]', '点': "o'clock; dot",
    '电话': 'telephone', '电脑': 'computer', '电视': 'television',
    '电影': 'movie', '东西': 'thing', '都': 'all/both',
    '读': 'read', '对不起': 'sorry', '多': 'many/much',
    '多少': 'how many/much', '饿': 'hungry', '二': 'two',
    '饭': 'rice/meal', '饭店': 'restaurant', '飞机': 'airplane',
    '非常': 'very', '高兴': 'happy', '个': '(general classifier)',
    '工作': 'work', '狗': 'dog', '汉语': 'Chinese (language)',
    '好': 'good', '号': 'date/number', '喝': 'drink',
    '和': 'and/with', '很': 'very', '后面': 'behind',
    '回': 'return', '会': 'can/know how', '几': 'how many',
    '家': 'home/family', '叫': 'called', '今天': 'today',
    '九': 'nine', '开': 'open', '看': 'look/read/watch',
    '看病': 'see a doctor', '看见': 'see', '考': 'test/examine',
    '可是': 'but/however', '块': 'piece/lump; yuan (colloquial)',
    '来': 'come', '老师': 'teacher', '了': '[completed action particle]',
    '冷': 'cold', '里': 'inside', '零': 'zero', '六': 'six',
    '妈妈': 'mother', '吗': '[question particle]', '买': 'buy',
    '慢': 'slow', '忙': 'busy', '猫': 'cat',
    '没关系': "it doesn't matter", '米饭': 'cooked rice',
    '名字': 'name', '明年': 'next year', '明天': 'tomorrow',
    '哪': 'which', '哪儿': 'where', '哪国': 'which country',
    '哪里': 'where', '那': 'that', '呢': '[particle]',
    '能': 'can/able to', '你': 'you', '年': 'year',
    '女儿': 'daughter', '朋友': 'friend', '七': 'seven',
    '前面': 'front', '钱': 'money', '请': 'please',
    '去': 'go', '热': 'hot', '人': 'person',
    '认识': 'recognize/know', '三': 'three', '商店': 'shop/store',
    '上': 'up/on/above', '上午': 'morning', '少': 'few/little',
    '谁': 'who', '什么': 'what', '十': 'ten',
    '时候': 'time/moment', '是': 'is/am/are', '书': 'book',
    '水': 'water', '水果': 'fruit', '睡觉': 'sleep',
    '说': 'speak/say', '四': 'four', '岁': 'years old',
    '他': 'he/him', '她': 'she/her', '太': 'too (much)',
    '天气': 'weather', '听': 'listen', '同学': 'classmate',
    '喂': 'hello (on phone); hey', '我': 'I/me', '我们': 'we/us',
    '五': 'five', '喜欢': 'like', '下': 'down/under/next',
    '下午': 'afternoon', '下雨': 'rain', '现在': 'now',
    '想': 'think/want/miss', '小': 'small/little',
    '小姐': 'Miss (young woman)', '些': 'some; a few',
    '写': 'write', '谢谢': 'thank you', '星期': 'week',
    '星期日': 'Sunday', '学生': 'student', '学习': 'study',
    '学校': 'school', '一': 'one', '衣服': 'clothes',
    '医生': 'doctor', '医院': 'hospital', '椅子': 'chair',
    '有': 'have/there is', '月': 'month; moon', '在': 'at/in/on',
    '再见': 'goodbye', '怎么': 'how', '怎么样': 'how about',
    '这': 'this', '中国': 'China', '中午': 'noon',
    '住': 'live/reside', '桌子': 'table/desk', '字': 'character',
    '坐': 'sit', '做': 'do/make', '分钟': 'minute',
    '苹果': 'apple', '车站': 'bus/train station', '超市': 'supermarket',
    '出租车': 'taxi', '床': 'bed', '从': 'from',
    '错': 'wrong', '打篮球': 'play basketball',
    '大家': 'everyone', '到': 'arrive/to', '得': '[structural particle]',
    '等': 'wait', '弟弟': 'younger brother', '第一': 'first',
    '懂': 'understand', '对': 'correct/to/toward', '房间': 'room',
    '非常': 'extremely', '服务员': 'waiter/server',
    '高': 'tall/high', '告诉': 'tell', '哥哥': 'older brother',
    '给': 'give/to', '公共汽车': 'bus', '公斤': 'kilogram',
    '公司': 'company', '贵': 'expensive', '过': '[experiential particle]',
    '还': 'still/also', '孩子': 'child', '好吃': 'delicious',
    '火车站': 'train station', '火车': 'train', '或者': 'or',
    '机场': 'airport', '鸡蛋': 'egg', '件': 'piece (classifier for items)',
    '教室': 'classroom', '姐姐': 'older sister',
    '介绍': 'introduce', '进': 'enter', '近': 'near/close',
    '就': 'then/just', '觉得': 'feel/think', '咖啡': 'coffee',
    '开始': 'begin/start', '考试': 'exam/test', '可能': 'possible/may',
    '课': 'class/lesson', '快': 'fast/quick', '快乐': 'happy/joyful',
    '累': 'tired', '离': 'away from', '两': 'two (with classifier)',
    '路': 'road/way', '旅游': 'travel/tour', '卖': 'sell',
    '毛': 'dime (1/10 yuan); hair', '没': 'not (past)',
    '没有': "don't have/didn't", '每': 'each/every',
    '妹妹': 'younger sister', '门': 'door/gate', '面条': 'noodles',
    '男': 'male', '您': 'you (polite)', '牛奶': 'milk',
    '女人': 'woman', '旁边': 'beside/next to', '跑': 'run',
    '便宜': 'cheap/inexpensive', '票': 'ticket', '妻子': 'wife',
    '起': 'rise/start', '千': 'thousand', '铅笔': 'pencil',
    '晴': 'sunny/clear', '去年': 'last year', '让': 'let/allow',
    '上班': 'go to work', '身体': 'body/health',
    '生病': 'get sick/ill', '生日': 'birthday', '生气': 'angry',
    '时间': 'time', '事情': 'thing/matter', '手表': 'watch',
    '是...的': 'it is...that (emphasis)', '手机': 'mobile phone',
    '说话': 'speak/talk', '送': 'send/give as gift',
    '虽然': 'although', '但是': 'but', '它': 'it',
    '踢足球': 'play soccer', '题': 'question/problem',
    '跳舞': 'dance', '外': 'outside', '玩': 'play/have fun',
    '晚上': 'evening/night', '往': 'toward',
    '为什么': 'why', '问题': 'question/problem',
    '西瓜': 'watermelon', '希望': 'hope/wish', '洗': 'wash',
    '小时': 'hour', '笑': 'laugh/smile', '新': 'new',
    '姓': 'surname/family name', '休息': 'rest', '雪': 'snow',
    '颜色': 'color', '眼睛': 'eye', '药': 'medicine',
    '要': 'want/need', '也': 'also/too', '已经': 'already',
    '一起': 'together', '意思': 'meaning', '因为': 'because',
    '银行': 'bank', '游泳': 'swim', '右边': 'right side',
    '鱼': 'fish', '远': 'far', '运动': 'exercise/sport',
    '再': 'again', '早上': 'early morning', '丈夫': 'husband',
    '找': 'find/look for', '真': 'really/truly', '正在': 'in the process of',
    '知道': 'know', '准备': 'prepare', '走': 'walk/go',
    '最': 'most', '左边': 'left side', '爸爸': 'dad',
    '妈妈': 'mom', '爷爷': 'grandpa (paternal)',
    '奶奶': 'grandma (paternal)', '外公': 'grandpa (maternal)',
    '外婆': 'grandma (maternal)', '儿子': 'son',
    '衣服': 'clothing', '雨伞': 'umbrella', '钥匙': 'key',
    '钱包': 'wallet', '地图': 'map', '新闻': 'news',
    '生气': 'get angry', '快乐': 'happy',
    # HSK 2 common
    '帮助': 'help', '报纸': 'newspaper', '参加': 'participate/join',
    '唱歌': 'sing', '出': 'go out/exit', '出发': 'set off/depart',
    '发': 'send/hair', '发现': 'discover/find out', '方便': 'convenient',
    '放': 'put/place', '放心': 'feel relieved', '附近': 'nearby',
    '交': 'hand over/pay', '交通': 'traffic/transportation',
    '接受': 'accept/receive', '酒店': 'hotel', '决定': 'decide/decision',
    '可爱': 'cute/adorable', '离开': 'leave/depart',
    '礼物': 'gift/present', '联系': 'contact/connect',
    '路': 'road/path', '麻烦': 'trouble/bother',
    '满意': 'satisfied/content', '拿': 'take/hold',
    '奶奶': 'grandmother', '南': 'south', '年级': 'grade (school)',
    '暖和': 'warm', '爬山': 'mountain climbing', '裙子': 'skirt/dress',
    '全': 'all/entire', '然后': 'then/after that', '热闹': 'bustling/lively',
    '散步': 'take a walk', '商量': 'discuss/consult',
    '上课': 'attend class', '生气': 'angry',
    '世界': 'world', '试': 'try/test',
    '首先': 'first of all', '说话': 'speak',
    '送': 'give/send', '踢': 'kick',
    '突然': 'suddenly', '忘记': 'forget',
    '危险': 'dangerous', '温度': 'temperature',
    '西': 'west', '习惯': 'habit/be accustomed to',
    '相信': 'believe/trust', '香蕉': 'banana',
    '向': 'toward/facing', '需要': 'need/require',
    '选择': 'choose/choice', '要求': 'require/request',
    '已经': 'already', '以为': 'thought (mistakenly)',
    '音乐': 'music', '应该': 'should/ought to',
    '影响': 'influence/affect', '用': 'use',
    '重要': 'important', '主要': 'main/primary',
    '注意': 'pay attention', '祝': 'wish (blessing)',
    '作业': 'homework', '着急': 'anxious/worried',
    '准确': 'accurate/precise', '照顾': 'take care of',
    '真正': 'real/genuine', '整理': 'organize/tidy up',
    '正常': 'normal', '正好': 'just right/exactly',
    '支': 'branch (classifier)', '知识': 'knowledge',
    '只': 'only/just', '中间': 'middle/center',
    '中文': 'Chinese language', '终于': 'finally/at last',
    '种': 'kind/type; plant', '重': 'heavy/serious',
    '周末': 'weekend', '专门': 'specifically/specially',
    '准确': 'accurate', '仔细': 'careful/meticulous',
    '自然': 'natural/nature', '总是': 'always',
    '嘴': 'mouth', '最近': 'recently/latest',
    '左边': 'left side', '右边': 'right side',
    '北': 'north', '春': 'spring', '夏': 'summer',
    '秋': 'autumn/fall', '冬': 'winter',
    # HSK 3 common
    '啊': 'ah/oh [particle]', '安排': 'arrange/arrangement',
    '暗': 'dark', '岸': 'shore/bank', '把': 'take/hold; [ba-construction]',
    '棒': 'great/excellent', '包子': 'steamed bun',
    '保护': 'protect', '保证': 'guarantee/ensure',
    '报名': 'sign up/register', '抱': 'hug/embrace',
    '倍': 'times (multiplier)', '本来': 'originally',
    '笨': 'stupid/clumsy', '比如': 'for example',
    '遍': 'times (frequency)', '标准': 'standard',
    '表格': 'form/table', '表演': 'perform/performance',
    '别的': 'other/different', '冰箱': 'refrigerator',
    '不但': 'not only', '部分': 'part/section',
    '擦': 'wipe/rub', '猜': 'guess',
    '材料': 'material', '参观': 'visit (a place)',
    '餐厅': 'dining hall/restaurant', '厕所': 'toilet/restroom',
    '差': 'lack/differ; poor', '长': 'long',
    '场': 'field (classifier)', '超过': 'exceed/surpass',
    '吵': 'noisy/argue', '成功': 'succeed/success',
    '成为': 'become', '诚实': 'honest',
    '乘坐': 'ride/take (transport)', '吃惊': 'surprised',
    '重新': 'again/anew', '抽烟': 'smoke (cigarettes)',
    '出差': 'business trip', '出发': 'depart/set out',
    '传真': 'fax', '窗户': 'window',
    '词语': 'word/phrase', '从来': 'always/ever',
    '粗心': 'careless', '错': 'wrong/mistake',
    '答案': 'answer', '打扮': 'dress up',
    '打工': 'work part-time', '打扰': 'disturb/bother',
    '打印': 'print', '大约': 'approximately/about',
    '戴': 'wear (accessories)', '当': 'when/as',
    '当然': 'of course', '蛋糕': 'cake',
    '得': 'get/obtain', '灯': 'lamp/light',
    '低': 'low', '底': 'bottom',
    '地球': 'earth', '地址': 'address',
    '电梯': 'elevator', '电子邮件': 'email',
    '电': 'electricity', '掉': 'drop/fall off',
    '调查': 'investigate/survey', '掉': 'lose/drop',
    '顶': 'top/peak', '冬': 'winter',
    '动物': 'animal', '短': 'short (length)',
    '段': 'paragraph/section', '锻炼': 'exercise/work out',
    '多么': 'how (exclamatory)', '而': 'and/but',
    '发生': 'happen/occur', '发展': 'develop/development',
    '方便': 'convenient', '方法': 'method/way',
    '方面': 'aspect/side', '方向': 'direction',
    '房东': 'landlord', '放弃': 'give up',
    '放假': 'take a vacation', '结婚': 'marry/get married',
    '结束': 'finish/end', '解': 'untie/solve',
    '尽管': 'despite/although', '紧张': 'nervous/tense',
    '经济': 'economy', '经历': 'experience',
    '精神': 'spirit/energy', '镜子': 'mirror',
    '居然': 'unexpectedly', '卡': 'card',
    '开机': 'turn on (machine)', '开心': 'happy',
    '看法': 'opinion/view', '考虑': 'consider',
    '科学': 'science', '棵': 'tree (classifier)',
    '空': 'empty/free', '空调': 'air conditioning',
    '口': 'mouth (classifier)', '哭': 'cry',
    '筷子': 'chopsticks', '蓝': 'blue',
    '老': 'old', '厉害': 'severe/formidable',
    '两': 'two (with classifier)', '聊天': 'chat',
    '了解': 'understand/find out', '邻': 'neighbor',
    '零': 'zero', '另外': 'additionally/other',
    '年龄': 'age', '弄': 'do/make',
    '爬山': 'hike/climb', '盘': 'plate/dish',
    '胖': 'fat', '跑步': 'run/jog',
    '陪': 'accompany', '配合': 'cooperate',
    '朋友': 'friend', '皮': 'leather/skin',
    '脾气': 'temperament', '篇': 'article (classifier)',
    '骗': 'cheat/deceive', '乒乓球': 'table tennis',
    '平时': 'usually/ordinarily', '破': 'broken',
    '葡萄': 'grape', '普遍': 'common/universal',
    '普通话': 'Mandarin', '骑': 'ride',
    '其实': 'actually/in fact', '其他': 'other',
    '其中': 'among them', '气候': 'climate',
    '千': 'thousand', '签证': 'visa',
    '敲': 'knock', '桥': 'bridge',
    '巧克力': 'chocolate', '亲戚': 'relative',
    '轻': 'light (weight)', '清楚': 'clear',
    '请假': 'ask for leave', '穷': 'poor',
    '区别': 'difference/distinction', '取': 'take/get',
    '全部': 'all/entire', '缺少': 'lack/be short of',
    '却': 'however/yet', '确实': 'indeed/really',
    '热闹': 'lively/bustling', '任何': 'any',
    '任务': 'task/mission', '仍然': 'still',
    '如果': 'if', '上网': 'go online',
    '稍微': 'slightly/a bit', '森林': 'forest',
    '沙发': 'sofa', '商量': 'discuss',
    '稍微': 'slightly', '社会': 'society',
    '申请': 'apply', '深刻': 'profound',
    '甚至': 'even', '生活': 'life',
    '声音': 'sound/voice', '世界': 'world',
    '合适': 'suitable', '护照': 'passport',
    '花': 'flower/spend', '画': 'paint/draw',
    '环境': 'environment', '换': 'change/exchange',
    '黄': 'yellow', '回答': 'answer/respond',
    '会议': 'meeting/conference', '或者': 'or',
    '机场': 'airport', '机会': 'opportunity',
    '极': 'extremely', '记得': 'remember',
    '季节': 'season', '检查': 'check/inspect',
    '简单': 'simple', '健康': 'health/healthy',
    '讲': 'speak/lecture', '教': 'teach',
    '脚': 'foot', '接': 'receive/connect',
    '街': 'street', '节': 'festival/holiday',
    '节目': 'program/show', '节日': 'holiday/festival',
    '结婚': 'get married', '结束': 'end/finish',
    '解决': 'solve/resolve', '借': 'borrow/lend',
    '经常': 'often/frequently', '经过': 'pass through',
    '经理': 'manager', '久': 'long (time)',
    '旧': 'old (things)', '觉得': 'feel/think',
    '咖啡': 'coffee', '开头': 'beginning',
    '开放': 'open up', '看法': 'view/opinion',
    '考试': 'exam/test', '课': 'class',
    '空间': 'space', '恐怕': 'afraid/I\'m afraid',
    '苦': 'bitter', '矿泉水': 'mineral water',
    '困': 'sleepy', '困难': 'difficulty',
    '辣椒': 'chili pepper', '烂': 'rotten/soft',
    '老虎': 'tiger', '冷': 'cold',
    '礼拜天': 'Sunday', '厉害': 'formidable',
    '俩': 'two (people)', '连': 'even/connect',
    '联系': 'contact', '凉': 'cool',
    '辆': 'vehicle (classifier)', '零': 'zero',
    '留': 'stay/keep', '楼': 'building/floor',
    '绿': 'green', '马': 'horse',
    '马上': 'immediately', '满意': 'satisfied',
    '毛': 'hair/dime', '毛巾': 'towel',
    '美丽': 'beautiful', '梦': 'dream',
    '迷路': 'get lost', '密码': 'password',
    '免费': 'free of charge', '民族': 'ethnic group',
    '明白': 'understand/clear', '拿': 'take',
    '奶奶': 'grandma', '南': 'south',
    '难': 'difficult', '难过': 'sad',
    '年级': 'grade', '年轻': 'young',
    '鸟': 'bird', '努力': 'hardworking',
    '爬山': 'mountain climbing', '盘子': 'plate',
    '胖': 'fat', '陪': 'accompany',
    '批评': 'criticize', '皮鞋': 'leather shoes',
    '片': 'slice (classifier)', '骗': 'deceive',
    '拼音': 'pinyin', '乒乓球': 'ping pong',
    '啤酒': 'beer', '票': 'ticket',
    '妻子': 'wife', '骑': 'ride',
    '其实': 'actually', '其他': 'other',
    '奇怪': 'strange/weird', '气候': 'climate',
    '千': 'thousand', '签证': 'visa',
    '敲': 'knock', '桥': 'bridge',
    '巧克力': 'chocolate', '亲戚': 'relative',
    '轻': 'light', '清楚': 'clear',
    '请假': 'ask for leave', '穷': 'poor',
    '区别': 'difference', '取': 'take',
    '全部': 'all', '缺少': 'lack',
    '却': 'however', '确实': 'indeed',
    '群': 'group (classifier)', '然后': 'then',
    '热闹': 'lively', '任何': 'any',
    '扔': 'throw', '仍然': 'still',
    '容易': 'easy', '如果': 'if',
    '伞': 'umbrella', '上网': 'surf the internet',
    '生气': 'angry', '声音': 'sound',
    '世界': 'world', '收': 'receive',
    '舒服': 'comfortable', '熟悉': 'familiar',
    '数': 'count/number', '刷子': 'brush',
    '帅': 'handsome', '双': 'pair (classifier)',
    '谁': 'who', '水平': 'level/standard',
    '瞬间': 'moment', '说法': 'statement',
    '送': 'send/give', '算': 'calculate',
    '虽然': 'although', '所有': 'all',
    '台': 'machine (classifier)', '态度': 'attitude',
    '汤': 'soup', '趟': 'trip (classifier)',
    '讨论': 'discuss', '讨厌': 'hate/dislike',
    '提高': 'improve', '体育': 'sports',
    '甜': 'sweet', '条': 'strip (classifier)',
    '停': 'stop', '挺': 'quite/rather',
    '通过': 'through/pass', '通知': 'notify/notice',
    '同': 'same', '头发': 'hair',
    '突然': 'suddenly', '图书馆': 'library',
    '腿': 'leg', '完成': 'complete/finish',
    '玩': 'play', '晚上': 'evening',
    '往': 'toward', '忘记': 'forget',
    '为': 'for', '为了': 'in order to',
    '位': 'person (polite classifier)',
    '文化': 'culture', '西': 'west',
    '习惯': 'habit', '洗': 'wash',
    '系': 'tie/fasten', '夏': 'summer',
    '先': 'first/before', '相信': 'believe',
    '相反': 'opposite', '香蕉': 'banana',
    '向': 'toward', '像': 'like/resemble',
    '消息': 'news/message', '校长': 'principal',
    '笑': 'laugh', '效果': 'effect',
    '一些': 'some', '已经': 'already',
    '一共': 'in total', '一样': 'same',
    '意思': 'meaning', '因为': 'because',
    '音乐': 'music', '银行': 'bank',
    '应该': 'should', '影响': 'influence',
    '用': 'use', '游戏': 'game',
    '有名': 'famous', '又': 'again',
    '遇到': 'encounter/meet', '原来': 'originally',
    '约': 'about/approximately', '愿意': 'willing',
    '月亮': 'moon', '越': 'more and more',
    '站': 'stand/station', '张': 'sheet (classifier)',
    '长': 'long', '着急': 'anxious',
    '照顾': 'take care of', '真': 'really',
    '正在': 'in progress', '知识': 'knowledge',
    '直': 'straight', '只有': 'only',
    '中间': 'middle', '中文': 'Chinese',
    '钟': 'clock', '种': 'kind/type',
    '重要': 'important', '周末': 'weekend',
    '主要': 'main', '注意': 'pay attention',
    '桌子': 'table', '仔细': 'careful',
    '自然': 'natural', '总是': 'always',
    '嘴': 'mouth', '最近': 'recently',
    '左边': 'left', '做生意': 'do business',
    '座位': 'seat',
    # HSK 4+ common
    '爱情': 'love/romance', '安全': 'safety/secure',
    '按': 'according to/press', '按照': 'according to',
    '百分之': 'percent', '棒': 'great',
    '包子': 'steamed bun', '保持': 'maintain',
    '保护': 'protect', '保证': 'guarantee',
    '报名': 'register', '抱': 'embrace',
    '抱歉': 'sorry/apologetic', '倍': 'times',
    '本来': 'originally', '笨': 'stupid',
    '比如': 'for example', '比较': 'compare/relatively',
    '比赛': 'competition/match', '必须': 'must',
    '避免': 'avoid', '遍': 'times (frequency)',
    '标准': 'standard', '表格': 'form',
    '表示': 'express/indicate', '表演': 'performance',
    '别的': 'other', '别人': 'others',
    '冰箱': 'refrigerator', '不仅': 'not only',
    '部分': 'part', '擦': 'wipe',
    '猜': 'guess', '材料': 'material',
    '参观': 'visit', '餐厅': 'restaurant',
    '厕所': 'restroom', '曾': 'once/ever',
    '差': 'difference/poor', '产生': 'produce/generate',
    '长': 'long', '场': 'field',
    '超过': 'exceed', '吵': 'noisy',
    '成功': 'success', '成为': 'become',
    '诚实': 'honest', '乘坐': 'take (transport)',
    '吃惊': 'surprised', '重新': 'anew',
    '抽烟': 'smoke', '出差': 'business trip',
    '出发': 'depart', '传真': 'fax',
    '创造': 'create', '词语': 'word',
    '从来': 'always', '粗心': 'careless',
    '存': 'save/store', '错误': 'error/mistake',
    '答案': 'answer', '打扮': 'dress up',
    '打工': 'work part-time', '打扰': 'disturb',
    '打印': 'print', '大约': 'approximately',
    '戴': 'wear (accessory)', '当': 'when',
    '当然': 'of course', '蛋糕': 'cake',
    '得': 'get', '灯': 'lamp',
    '低': 'low', '底': 'bottom',
    '地球': 'earth', '地址': 'address',
    '电梯': 'elevator', '电子邮件': 'email',
    '掉': 'drop', '调查': 'survey',
    '掉': 'lose', '顶': 'top',
    '动物': 'animal', '短': 'short',
    '段': 'paragraph', '锻炼': 'exercise',
    '多么': 'how (exclamatory)', '而': 'and',
    '发生': 'happen', '发展': 'develop',
    '方便': 'convenient', '方法': 'method',
    '方面': 'aspect', '方向': 'direction',
    '房东': 'landlord', '放弃': 'give up',
    '放假': 'vacation', '结婚': 'marry',
    '结束': 'end', '解': 'solve',
    '尽管': 'despite', '紧张': 'nervous',
    '经济': 'economy', '经历': 'experience',
    '精神': 'spirit', '镜子': 'mirror',
    '居然': 'unexpectedly', '卡': 'card',
    '开机': 'turn on', '开心': 'happy',
    '看法': 'view', '考虑': 'consider',
    '科学': 'science', '棵': 'tree (clf)',
    '空': 'empty', '空调': 'air conditioning',
    '口': 'mouth', '哭': 'cry',
    '筷子': 'chopsticks', '蓝': 'blue',
    '老': 'old', '厉害': 'formidable',
    '两': 'two', '聊天': 'chat',
    '了解': 'understand', '邻': 'neighbor',
    '零': 'zero', '另外': 'additionally',
    '年龄': 'age', '弄': 'do',
    '爬山': 'hike', '盘': 'plate',
    '胖': 'fat', '跑步': 'jog',
    '陪': 'accompany', '配合': 'cooperate',
    '朋友': 'friend', '皮': 'leather',
    '脾气': 'temper', '篇': 'article',
    '骗': 'cheat', '乒乓球': 'table tennis',
    '平时': 'usually', '破': 'broken',
    '葡萄': 'grape', '普遍': 'common',
    '普通话': 'Mandarin', '骑': 'ride',
    '其实': 'actually', '其他': 'other',
    '其中': 'among', '气候': 'climate',
    '千': 'thousand', '签证': 'visa',
    '敲': 'knock', '桥': 'bridge',
    '巧克力': 'chocolate', '亲戚': 'relative',
    '轻': 'light', '清楚': 'clear',
    '请假': 'ask leave', '穷': 'poor',
    '区别': 'difference', '取': 'take',
    '全部': 'all', '缺少': 'lack',
    '却': 'however', '确实': 'indeed',
    '热闹': 'lively', '任何': 'any',
    '任务': 'task', '仍然': 'still',
    '如果': 'if', '上网': 'go online',
    '稍微': 'slightly', '森林': 'forest',
    '沙发': 'sofa', '商量': 'discuss',
    '社会': 'society', '申请': 'apply',
    '深刻': 'profound', '甚至': 'even',
    '生活': 'life', '声音': 'sound',
    '世界': 'world', '收': 'receive',
    '舒服': 'comfortable', '熟悉': 'familiar',
    '数': 'count', '刷子': 'brush',
    '帅': 'handsome', '双': 'pair',
    '谁': 'who', '水平': 'level',
    '瞬间': 'moment', '说法': 'statement',
    '送': 'send', '算': 'calculate',
    '虽然': 'although', '所有': 'all',
    '台': 'machine', '态度': 'attitude',
    '汤': 'soup', '趟': 'trip',
    '讨论': 'discuss', '讨厌': 'hate',
    '提高': 'improve', '体育': 'sports',
    '甜': 'sweet', '条': 'strip',
    '停': 'stop', '挺': 'quite',
    '通过': 'through', '通知': 'notify',
    '同': 'same', '头发': 'hair',
    '突然': 'suddenly', '图书馆': 'library',
    '腿': 'leg', '完成': 'complete',
    '玩': 'play', '晚上': 'evening',
    '往': 'toward', '忘记': 'forget',
    '为': 'for', '为了': 'in order to',
    '位': 'person', '文化': 'culture',
    '西': 'west', '习惯': 'habit',
    '洗': 'wash', '系': 'tie',
    '夏': 'summer', '先': 'first',
    '相信': 'believe', '相反': 'opposite',
    '香蕉': 'banana', '向': 'toward',
    '像': 'resemble', '消息': 'news',
    '校长': 'principal', '笑': 'laugh',
    '效果': 'effect', '一些': 'some',
    '已经': 'already', '一共': 'total',
    '一样': 'same', '意思': 'meaning',
    '因为': 'because', '音乐': 'music',
    '银行': 'bank', '应该': 'should',
    '影响': 'influence', '用': 'use',
    '游戏': 'game', '有名': 'famous',
    '又': 'again', '遇到': 'encounter',
    '原来': 'originally', '约': 'about',
    '愿意': 'willing', '月亮': 'moon',
    '越': 'more and more', '站': 'stand',
    '张': 'sheet', '长': 'long',
    '着急': 'anxious', '照顾': 'care for',
    '真': 'really', '正在': 'in progress',
    '知识': 'knowledge', '直': 'straight',
    '只有': 'only', '中间': 'middle',
    '中文': 'Chinese', '钟': 'clock',
    '种': 'kind', '重要': 'important',
    '周末': 'weekend', '主要': 'main',
    '注意': 'attention', '桌子': 'table',
    '仔细': 'careful', '自然': 'natural',
    '总是': 'always', '嘴': 'mouth',
    '最近': 'recently', '左边': 'left',
    '做生意': 'do business', '座位': 'seat',
    '爱情': 'love', '安全': 'safety',
    '按': 'press', '按照': 'according to',
    '百分之': 'percent', '保持': 'maintain',
    '保护': 'protect', '保证': 'guarantee',
    '报名': 'register', '抱歉': 'sorry',
    '倍': 'times', '本来': 'originally',
    '笨': 'stupid', '比如': 'for example',
    '比较': 'compare', '比赛': 'match',
    '必须': 'must', '避免': 'avoid',
    '遍': 'times', '标准': 'standard',
    '表格': 'form', '表示': 'express',
    '表演': 'performance', '别的': 'other',
    '别人': 'others', '冰箱': 'fridge',
    '不仅': 'not only', '部分': 'part',
    '擦': 'wipe', '猜': 'guess',
    '材料': 'material', '参观': 'visit',
    '餐厅': 'restaurant', '厕所': 'toilet',
    '曾': 'once', '产生': 'produce',
    '产生': 'generate', '超过': 'exceed',
    '吵': 'noisy', '成功': 'success',
    '成为': 'become', '诚实': 'honest',
    '乘坐': 'ride', '吃惊': 'surprised',
    '重新': 'anew', '抽烟': 'smoke',
    '出差': 'business trip', '出发': 'depart',
    '创造': 'create', '词语': 'word',
    '从来': 'ever', '粗心': 'careless',
    '存': 'save', '错误': 'error',
    '答案': 'answer', '打扮': 'dress',
    '打工': 'work', '打扰': 'disturb',
    '打印': 'print', '大约': 'about',
    '戴': 'wear', '当': 'when',
    '当然': 'of course', '蛋糕': 'cake',
    '低': 'low', '底': 'bottom',
    '地球': 'earth', '地址': 'address',
    '电梯': 'elevator', '掉': 'drop',
    '调查': 'survey', '顶': 'top',
    '动物': 'animal', '短': 'short',
    '段': 'section', '锻炼': 'exercise',
    '发': 'send', '发现': 'discover',
    '法律': 'law', '翻译': 'translate',
    '烦恼': 'annoyed', '范围': 'scope',
    '方面': 'aspect', '方向': 'direction',
    '方法': 'method', '反映': 'reflect',
    '方式': 'style', '非': 'not',
    '非常': 'very', '符合': 'match',
    '复杂': 'complex', '付款': 'pay',
    '负责': 'responsible', '富': 'rich',
    '改变': 'change', '干': 'dry',
    '感': 'feel', '感动': 'moved',
    '感觉': 'feel', '感谢': 'thank',
    '刚': 'just', '刚才': 'just now',
    '高级': 'senior', '搞': 'do',
    '告状': 'complain', '哥哥': 'brother',
    '各': 'each', '工资': 'salary',
    '公里': 'kilometer', '古代': 'ancient',
    '鼓励': 'encourage', '固': 'solid',
    '顾客': 'customer', '挂': 'hang',
    '关键': 'key', '观察': 'observe',
    '管理': 'manage', '光': 'light',
    '广告': 'advertisement', '逛': 'stroll',
    '规定': 'regulation', '国际': 'international',
    '果然': 'as expected', '过程': 'process',
    '海洋': 'ocean', '害羞': 'shy',
    '寒假': 'winter vacation', '汗': 'sweat',
    '航班': 'flight', '好处': 'benefit',
    '好像': 'seem', '号码': 'number',
    '合格': 'qualified', '合适': 'suitable',
    '合作': 'cooperate', '核心': 'core',
    '恨': 'hate', '猴': 'monkey',
    '厚': 'thick', '互联网': 'internet',
    '互相': 'mutually', '花生': 'peanut',
    '划': 'row', '画': 'draw',
    '坏': 'bad', '回忆': 'recall',
    '活动': 'activity', '火': 'fire',
    '获取': 'obtain', '基础': 'foundation',
    '机场': 'airport', '机会': 'opportunity',
    '极': 'extremely', '记得': 'remember',
    '季节': 'season', '检查': 'check',
    '简单': 'simple', '健康': 'health',
    '讲': 'speak', '教': 'teach',
    '脚': 'foot', '接': 'receive',
    '街': 'street', '节': 'festival',
    '节目': 'program', '节日': 'holiday',
    '结果': 'result', '结构': 'structure',
    '结合': 'combine', '结论': 'conclusion',
    '解释': 'explain', '尽管': 'although',
    '紧张': 'nervous', '进行': 'conduct',
    '经济': 'economy', '经过': 'pass',
    '经历': 'experience', '经验': 'experience',
    '精彩': 'wonderful', '景色': 'scenery',
    '警察': 'police', '竞争': 'compete',
    '竟然': 'unexpectedly', '九': 'nine',
    '酒店': 'hotel', '旧': 'old',
    '句子': 'sentence', '拒绝': 'refuse',
    '距离': 'distance', '聚会': 'gathering',
    '开玩笑': 'joke', '看不起': 'look down',
    '考虑': 'consider', '科学': 'science',
    '棵': 'tree', '空': 'empty',
    '空调': 'AC', '口': 'mouth',
    '哭': 'cry', '苦': 'bitter',
    '矿泉水': 'mineral water', '困': 'sleepy',
    '困难': 'difficulty', '拉': 'pull',
    '辣': 'spicy', '来不及': 'too late',
    '来得及': 'in time', '来不及': 'no time',
    '来自': 'from', '蓝': 'blue',
    '浪漫': 'romantic', '捞': 'fish out',
    '老板': 'boss', '老太太': 'old lady',
    '乐观': 'optimistic', '类型': 'type',
    '冷': 'cold', '厘': 'centimeter',
    '离婚': 'divorce', '礼貌': 'politeness',
    '理想': 'ideal', '力量': 'strength',
    '历史': 'history', '脸': 'face',
    '练习': 'practice', '辆': 'vehicle',
    '聊天': 'chat', '了解': 'understand',
    '邻居': 'neighbor', '灵活': 'flexible',
    '留': 'stay', '流': 'flow',
    '流行': 'popular', '旅游': 'travel',
    '律师': 'lawyer', '乱': 'messy',
    '麻烦': 'trouble', '马上': 'soon',
    '满意': 'satisfied', '毛': 'hair',
    '毛巾': 'towel', '美丽': 'beautiful',
    '梦': 'dream', '迷路': 'lost',
    '密码': 'password', '免费': 'free',
    '秒': 'second', '民族': 'ethnic',
    '明白': 'understand', '拿': 'take',
    '哪': 'which', '奶奶': 'grandma',
    '耐': 'patient', '南': 'south',
    '难': 'hard', '难过': 'sad',
    '难受': 'uncomfortable', '年级': 'grade',
    '年轻': 'young', '鸟': 'bird',
    '努力': 'effort', '排队': 'queue',
    '爬山': 'hike', '盘子': 'plate',
    '胖': 'fat', '跑': 'run',
    '陪': 'accompany', '批评': 'criticize',
    '皮肤': 'skin', '脾气': 'temper',
    '篇': 'article', '骗': 'cheat',
    '乒乓球': 'ping pong', '平时': 'usually',
    '破': 'broken', '葡萄': 'grape',
    '普遍': 'universal', '骑': 'ride',
    '其实': 'actually', '其他': 'other',
    '其中': 'among', '气候': 'climate',
    '千': 'thousand', '签证': 'visa',
    '敲': 'knock', '桥': 'bridge',
    '巧克力': 'chocolate', '亲戚': 'relative',
    '轻': 'light', '清楚': 'clear',
    '情况': 'situation', '请假': 'leave',
    '穷': 'poor', '区别': 'difference',
    '取': 'take', '全部': 'all',
    '缺少': 'lack', '却': 'however',
    '确实': 'indeed', '群': 'group',
    '然后': 'then', '热闹': 'lively',
    '任何': 'any', '扔': 'throw',
    '仍然': 'still', '容易': 'easy',
    '如果': 'if', '伞': 'umbrella',
    '上网': 'online', '生气': 'angry',
    '声音': 'voice', '省': 'province',
    '剩': 'remain', '失败': 'fail',
    '师傅': 'master', '十分': 'very',
    '实际': 'actual', '适合': 'suitable',
    '适应': 'adapt', '收': 'receive',
    '舒服': 'comfortable', '熟悉': 'familiar',
    '数量': 'quantity', '数字': 'number',
    '刷子': 'brush', '帅': 'handsome',
    '双': 'pair', '水平': 'level',
    '瞬间': 'moment', '说法': 'statement',
    '说明': 'explain', '硕士': 'master degree',
    '死': 'die', '速度': 'speed',
    '酸': 'sour', '随身': 'with oneself',
    '随': 'follow', '损失': 'loss',
    '所': 'place', '锁': 'lock',
    '台阶': 'steps', '谈': 'talk',
    '弹': 'play (instrument)', '汤': 'soup',
    '趟': 'trip', '讨论': 'discuss',
    '讨厌': 'hate', '套': 'set',
    '特别': 'special', '提': 'carry',
    '提供': 'provide', '提前': 'in advance',
    '提醒': 'remind', '填': 'fill',
    '条件': 'condition', '停': 'stop',
    '挺': 'quite', '通过': 'through',
    '通知': 'notify', '同情': 'sympathize',
    '头': 'head', '头发': 'hair',
    '投资': 'invest', '突然': 'sudden',
    '图书馆': 'library', '腿': 'leg',
    '完成': 'complete', '碗': 'bowl',
    '万': 'ten thousand', '往往': 'often',
    '危险': 'dangerous', '味道': 'taste',
    '温度': 'temperature', '文章': 'article',
    '污染': 'pollution', '无': 'no',
    '无聊': 'boring', '无论': 'no matter',
    '误会': 'misunderstand', '吸引': 'attract',
    '熟悉': 'familiar', '西红柿': 'tomato',
    '咸': 'salty', '现金': 'cash',
    '限制': 'limit', '相': 'each other',
    '相反': 'opposite', '相同': 'same',
    '详细': 'detailed', '响': 'ring',
    '橡皮': 'eraser', '消息': 'news',
    '效果': 'effect', '笑话': 'joke',
    '心情': 'mood', '新鲜': 'fresh',
    '信心': 'confidence', '行李': 'luggage',
    '幸福': 'happiness', '性别': 'gender',
    '性格': 'personality', '幸亏': 'luckily',
    '修理': 'repair', '许多': 'many',
    '学期': 'semester', '压力': 'pressure',
    '牙齿': 'tooth', '亚洲': 'Asia',
    '严格': 'strict', '严重': 'serious',
    '研究': 'research', '研究生': 'grad student',
    '盐': 'salt', '眼睛': 'eye',
    '演出': 'performance', '演员': 'actor',
    '阳光': 'sunshine', '养成': 'develop',
    '样子': 'appearance', '钥匙': 'key',
    '也许': 'perhaps', '叶子': 'leaf',
    '页': 'page', '一切': 'everything',
    '以': 'by/with', '以前': 'before',
    '以为': 'thought', '艺术': 'art',
    '意见': 'opinion', '因此': 'therefore',
    '印象': 'impression', '赢': 'win',
    '应聘': 'apply for job', '永远': 'forever',
    '优点': 'advantage', '由': 'by/from',
    '由于': 'due to', '友好': 'friendly',
    '有趣': 'interesting', '于是': 'thereupon',
    '与': 'and/with', '语法': 'grammar',
    '语言': 'language', '预习': 'preview',
    '原来': 'original', '愿意': 'willing',
    '约': 'about', '阅读': 'reading',
    '允许': 'allow', '杂志': 'magazine',
    '在': 'at', '赞成': 'approve',
    '暂时': 'temporary', '脏': 'dirty',
    '责任': 'responsibility', '增加': 'increase',
    '占': 'occupy', '招聘': 'recruit',
    '真正': 'real', '整理': 'organize',
    '正常': 'normal', '正好': 'exactly',
    '正确': 'correct', '正式': 'formal',
    '政府': 'government', '政治': 'politics',
    '支持': 'support', '知道': 'know',
    '直接': 'direct', '值得': 'worth',
    '职业': 'profession', '植物': 'plant',
    '指标': 'indicator', '至少': 'at least',
    '质量': 'quality', '重': 'heavy',
    '重点': 'key point', '周围': 'around',
    '主意': 'idea', '祝福': 'bless',
    '著名': 'famous', '专门': 'specialized',
    '专业': 'major', '转': 'turn',
    '赚': 'earn', '准确': 'accurate',
    '仔细': 'careful', '自然': 'nature',
    '总结': 'summarize', '租': 'rent',
    '最好': 'had better', '最近': 'recently',
    '尊重': 'respect', '左右': 'about',
}


# Load vocabulary data
VOCAB_DIR = BASE / '词汇数据'
vocab = {}
for lv in [1, 2, 3, 4, 5, 6]:
    fpath = VOCAB_DIR / f'hsk_vocab_{lv}.json'
    if fpath.exists():
        with open(fpath) as f:
            vocab[lv] = json.load(f)

# For 7-9, load separately
fpath79 = VOCAB_DIR / 'hsk_vocab_7-9.json'
if fpath79.exists():
    with open(fpath79) as f:
        vocab['7-9'] = json.load(f)

TRANSLATION_CACHE_PATH = VOCAB_DIR / 'hsk_translation_cache.json'
ENABLE_ONLINE_TRANSLATION = os.getenv('HSK_ENABLE_ONLINE_TRANSLATION', '0') == '1'
TRANSLATION_BATCH_SIZE = int(os.getenv('HSK_TRANSLATION_BATCH_SIZE', '40'))
WORD_SUFFIX_RE = re.compile(r'\d+$')
PINYIN_FRAGMENT_RE = re.compile(r"^[A-Za-züÜāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ'’·\- ]+$")

if TRANSLATION_CACHE_PATH.exists():
    with open(TRANSLATION_CACHE_PATH, encoding='utf-8') as f:
        TRANSLATION_CACHE = json.load(f)
else:
    TRANSLATION_CACHE = {}


def clean_vocab_word(word):
    """Remove disambiguation suffixes like 和1 while keeping the simplified form."""
    return WORD_SUFFIX_RE.sub('', str(word).strip())


def looks_like_pinyin_fragment(value):
    """Heuristic: detect malformed POS fields that are actually pinyin fragments."""
    value = str(value).strip()
    return bool(value) and bool(PINYIN_FRAGMENT_RE.fullmatch(value))


def normalize_vocab_entry(entry):
    """Normalize vocab display fields for appendix/export tables."""
    word = clean_vocab_word(entry.get('word', ''))
    pinyin = str(entry.get('pinyin', '')).strip()
    pos = str(entry.get('pos', '')).strip()

    # Some source rows incorrectly spill a second pinyin syllable into the POS field.
    if pos and looks_like_pinyin_fragment(pos) and not any(token in pos for token in POS_MAP):
        pinyin = f"{pinyin}{pos}"
        pos = ''

    return {
        'word': word,
        'pinyin': pinyin,
        'pos': pos,
    }


def english_meaning_for(word):
    """Look up an English gloss from local overrides and the persisted cache."""
    clean = clean_vocab_word(word)
    for key in (word, clean):
        if key in COMMON_TRANSLATIONS and COMMON_TRANSLATIONS[key]:
            return COMMON_TRANSLATIONS[key]
        cached = TRANSLATION_CACHE.get(key, '')
        if cached:
            return cached
    return ''


def save_translation_cache():
    """Persist newly discovered translations so later runs stay local-first."""
    with open(TRANSLATION_CACHE_PATH, 'w', encoding='utf-8') as f:
        json.dump(TRANSLATION_CACHE, f, ensure_ascii=False, indent=2, sort_keys=True)


def chunked(items, size):
    """Yield fixed-size chunks."""
    for i in range(0, len(items), size):
        yield items[i:i + size]


def translate_batch(words):
    """Translate a batch of Chinese words to English using a lightweight online fallback."""
    query = '\n'.join(words)
    url = (
        'https://translate.googleapis.com/translate_a/single'
        '?client=gtx&sl=zh-CN&tl=en&dt=t&q=' + urllib.parse.quote(query)
    )
    with urllib.request.urlopen(url, timeout=20) as response:
        data = json.loads(response.read().decode('utf-8'))
    translated = ''.join(part[0] for part in data[0]).split('\n')
    if len(translated) != len(words):
        raise ValueError('Translation batch size mismatch')
    return [item.strip() for item in translated]


def fill_missing_translations(words):
    """Populate the translation cache for words missing from the local glossary."""
    pending = []
    seen = set()

    for entry in words:
        word = clean_vocab_word(entry.get('word', ''))
        if not word or english_meaning_for(word) or word in seen:
            continue
        seen.add(word)
        pending.append(word)

    if not pending or not ENABLE_ONLINE_TRANSLATION:
        return

    print(f"  Filling {len(pending)} missing glossary translations with online fallback...")
    updated = False

    for batch in chunked(pending, TRANSLATION_BATCH_SIZE):
        try:
            translations = translate_batch(batch)
        except Exception:
            translations = []
            for word in batch:
                try:
                    translations.extend(translate_batch([word]))
                except Exception:
                    translations.append('')

        for word, translation in zip(batch, translations):
            translation = translation.strip()
            if translation:
                TRANSLATION_CACHE[word] = translation
                updated = True

    if updated:
        save_translation_cache()

# Exam structures
EXAM_STRUCTURE = {
    1: {
        'listening': {'total': 20, 'parts': [5, 5, 5, 5], 'duration': '~12 min'},
        'reading': {'total': 20, 'parts': [5, 5, 5, 5], 'duration': '20 min'},
        'writing': None,
        'total_q': 40, 'total_time': '~40 min'
    },
    2: {
        'listening': {'total': 25, 'parts': [5, 10, 10], 'duration': '~17 min'},
        'reading': {'total': 25, 'parts': [5, 5, 10, 5], 'duration': '25 min'},
        'writing': {'total': 10, 'parts': [5, 5], 'duration': '10 min'},
        'total_q': 60, 'total_time': '~60 min'
    },
    3: {
        'listening': {'total': 30, 'parts': [10, 10, 10], 'duration': '~23 min'},
        'reading': {'total': 30, 'parts': [10, 10, 10], 'duration': '30 min'},
        'writing': {'total': 10, 'parts': [5, 5], 'duration': '20 min'},
        'total_q': 70, 'total_time': '~83 min'
    },
    4: {
        'listening': {'total': 32, 'parts': [14, 18], 'duration': '~20 min'},
        'reading': {'total': 32, 'parts': [10, 15, 7], 'duration': '30 min'},
        'writing': {'total': 6, 'parts': [5, 1], 'duration': '25 min'},
        'total_q': 70, 'total_time': '~85 min'
    },
    5: {
        'listening': {'total': 35, 'parts': [19, 16], 'duration': '~25 min'},
        'reading': {'total': 35, 'parts': [10, 10, 15], 'duration': '35 min'},
        'writing': {'total': 2, 'parts': [1, 1], 'duration': '40 min'},
        'total_q': 72, 'total_time': '~110 min'
    },
    6: {
        'listening': {'total': 40, 'parts': [8, 20, 12], 'duration': '~30 min'},
        'reading': {'total': 40, 'parts': [10, 10, 20], 'duration': '40 min'},
        'writing': {'total': 2, 'parts': [1, 1], 'duration': '45 min'},
        'total_q': 82, 'total_time': '~125 min'
    },
}

LEVEL_NAMES = {
    1: ('初等·入门篇', 'Beginner · Starting Out'),
    2: ('初等·基础篇', 'Beginner · Foundation'),
    3: ('初等·进阶篇', 'Beginner · Advancing'),
    4: ('中等·突破篇', 'Intermediate · Breakthrough'),
    5: ('中等·精进篇', 'Intermediate · Refinement'),
    6: ('高等·卓越篇', 'Advanced · Excellence'),
    '7-9': ('高等·大师篇', 'Advanced · Mastery'),
}

VOCAB_TOPICS = {
    1: [
        ('Numbers & Time', '数字与时间', '一 二 三 四 五 六 七 八 九 十 百 点 分 半 年 月 日 星期 今天 明天 昨天 年 分钟'),
        ('People & Pronouns', '人物与称谓', '我 你 他 她 我们 你们 他们 爸爸 妈妈 哥哥 姐姐 弟弟 妹妹 老师 同学 朋友 医生 人 谁'),
        ('Daily Actions', '日常动作', '吃 喝 看 听 说 走 来 去 坐 站 睡 醒 买 卖 做 打电话 学习 工作 休息 打开 关上 到 回'),
        ('Common Objects', '常见物品', '书 手机 水 茶 杯子 书包 笔 钱 衣服 鞋子 雨伞 钥匙 电脑 电视 米饭 面条 菜 水果 苹果 包子'),
        ('Locations', '地点与方位', '学校 医院 超市 家 商店 餐厅 银行 车站 公园 电影院 上 下 里 外 前 后 左 右 中间 旁边'),
        ('Adjectives', '形容词与描述', '大 小 多 少 好 坏 热 冷 高 矮 长 短 快 慢 新 旧 忙 累 开心 好看 好吃 高兴'),
        ('Grammar Core', '核心语法', '是 有 在 想 能 会 不 吗 呢 很 非常 太 了 的 这 那 什么 几 多少 哪里 怎么 为什么'),
    ],
    2: [
        ('Weather & Seasons', '天气与季节', '天气 下雨 下雪 刮风 冷 热 春天 夏天 秋天 冬天 晴天 阴天 温度 度'),
        ('Shopping & Prices', '购物与价格', '买 卖 贵 便宜 打折 多少钱 块 元 角 分 打折 特价 超市 商店 收银台'),
        ('Transportation', '交通出行', '公交车 出租车 地铁 飞机 火车 自行车 走路 开车 坐 到 站 机场 火车站 票'),
        ('Hobbies', '兴趣爱好', '运动 跳舞 唱歌 踢足球 打篮球 跑步 游泳 旅游 玩 游戏 电影 电视 上网'),
        ('Work & Study', '工作与学习', '上班 下班 办公室 开会 考试 成绩 毕业 作业 问题 答案 容易 难 准备'),
        ('Health & Body', '健康与身体', '身体 头 眼睛 手 脚 感冒 发烧 吃药 看病 医院 疼 病 舒服 休息 健康'),
    ],
    3: [
        ('Social Interactions', '社交与人际', '欢迎 欢迎 道歉 感谢 告别 邀请 约会 见面 认识 了解 熟悉 关心 帮助 介绍'),
        ('Education & Campus', '教育与校园', '课程 作业 毕业 专业 成绩 奖学金 考试 学期 教室 图书馆 宿舍 校园 论文'),
        ('Work & Career', '工作与职业', '公司 经理 面试 工资 加班 辞职 辞职 合同 办公室 同事 老板 升职 请假 出差'),
        ('Travel & Culture', '旅游与文化', '景点 历史 风景 拍照 纪念品 导游 地图 护照 签证 酒店 航班 旅行 出发 到达'),
        ('Food Culture', '饮食文化', '菜单 点菜 口味 特色 筷子 宴席 辣 甜 酸 咸 新鲜 菜单 厨师 餐厅 服务员'),
        ('Living & Environment', '居住与环境', '租房 邻居 社区 环境 搬家 装修 小区 街道 附近 安静 干净 方便 距离'),
        ('Emotions & Psychology', '情感与心理', '高兴 难过 担心 生气 惊讶 满意 感动 紧张 放松 舒服 紧张 害怕 勇敢'),
    ],
    4: [
        ('Society & Economy', '社会与经济', '经济 发展 政策 市场 投资 竞争 消费 生产 需求 供应 贸易 合作 创新'),
        ('Tech & Internet', '科技与互联网', '网络 软件 数据 人工智能 扫码 网购 下载 安装 更新 密码 屏幕 点击 搜索'),
        ('Culture & Tradition', '文化与传统', '书法 京剧 武术 节日 习俗 传承 遗产 古典 现代 融合 影响 特色 代表性'),
        ('Law & Citizenship', '法律与公民', '法律 权利 义务 合同 投诉 维权 规定 制度 遵守 违法 罚款 责任 保护'),
        ('Media & News', '媒体与新闻', '新闻 报道 采访 评论 社交媒体 记者 发布 消息 热点 关注 舆论 传播'),
        ('Environment & Health', '环境与健康', '环保 污染 可持续发展 养生 医疗 健康 卫生 锻炼 减肥 预防 治疗'),
    ],
    5: [
        ('Academic & Education', '学术与教育', '论文 研究 实验 理论 分析 数据 结论 假设 方法 成果 学术 教授 学位'),
        ('Business & Economy', '商务与经济', '贸易 利润 合同 谈判 品牌 营销 策略 竞争 投资 风险 回报 股份 上市'),
        ('Literature & Art', '文学与艺术', '散文 小说 诗歌 鉴赏 意境 风格 创作 表现 灵感 审美 传统 创新'),
        ('Philosophy & Thought', '哲学与思想', '观点 矛盾 逻辑 推理 价值 信仰 思考 判断 批判 宽容 自由 平等'),
        ('Nature & Science', '自然与科学', '实验 现象 规律 气候 生态 物种 进化 适应 环境 资源 能量 变化'),
    ],
    6: [
        ('Advanced Academic', '高级学术词汇', '概率 趋势 论证 争议 范式 框架 模型 变量 参数 推导 归纳 演绎'),
        ('Advanced Business', '高级商务词汇', '战略 并购 估值 合规 风险 杠杆 对冲 套利 多元化 重组 整合'),
        ('Cultural Deep', '文化深层词汇', '含蓄 典故 隐喻 象征 底蕴 渊源 沉淀 传承 交融 碰撞 渗透'),
        ('Classical Expressions', '文言与书面表达', '之 乎 者 也 其 而 以 于 乃 则 虽 然 故 且 若 即'),
    ],
}

def vocab_for_level(lv, count=50):
    """Get first N vocabulary items for a level."""
    words = vocab.get(lv, [])
    if not words:
        return []
    return words[:count]

def write_file(path, content):
    """Write content to file, creating directories as needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

def gen_vocab_table(words):
    """Generate a vocabulary table in markdown with English POS and translations."""
    normalized = [normalize_vocab_entry(w) for w in words]
    fill_missing_translations(normalized)

    lines = ['| Word (简体) | Pinyin | Part of Speech | English Meaning |']
    lines.append('|-------------|--------|----------------|-----------------|')
    for w in normalized:
        word = w['word']
        pinyin = w['pinyin']
        pos_en = translate_pos(w.get('pos', ''))
        english = english_meaning_for(word)
        lines.append(f"| {word} | {pinyin} | {pos_en} | {english} |")
    return '\n'.join(lines)


def gen_vocab_appendix(words, chunk_size=80):
    """Split large vocab appendices into readable table sections."""
    sections = []
    for start in range(0, len(words), chunk_size):
        end = min(start + chunk_size, len(words))
        sections.append(
            f"### Entries {start + 1}-{end}\n\n{gen_vocab_table(words[start:end])}"
        )
    return '\n\n'.join(sections)

def gen_four_layer(word, pinyin, literal, english):
    """Generate a four-layer translation block."""
    return f"""```
Chinese: {word}
Pinyin: {pinyin}
Literal: {literal}
English: "{english}"
```"""

def gen_four_layer_block():
    """Generate a reusable four-layer explanation block."""
    return """The **Four-Layer Translation System** used throughout this book:

```
Chinese: 你    好     吗？
Pinyin:  nǐ    hǎo    ma?
Literal: you   good   [question]?
English: "How are you?"
```

This lets you see exactly how Chinese thinks — not just what it says."""


# ============================================================
# HSK 1 CONTENT
# ============================================================

def generate_hsk1():
    base = BASE / 'HSK备考/hsk1-prep'

    # Exam overview
    write_file(base / 'part0-exam-overview/01-hsk-intro.md', """# HSK 1 备考完全指南
## 初等·入门篇 — Level 1 Complete Prep Guide

> **2026年最新版 · 基于HSK 3.0官方考试大纲**

Published: 2026 | Author: Tony Sheng | Series: Z Turns Chinese

The definitive preparation guide for the new HSK Level 1 exam (HSK 3.0 framework).
Covers all 300 vocabulary words, grammar points, listening & reading strategies,
and 3 full mock exams. Designed for English speakers preparing for the July 2026 exam.

Z Turns Chinese — HSK 1 Prep Guide
""")

    # Part 1: Pinyin
    write_file(base / 'part1-pinyin/01-initials-finals.md', """# Part 1: 拼音与声调基础

## The Chinese Sound System

Chinese has only **~400 syllable combinations** (English has 15,000+). Master these, and you can pronounce ANY Chinese word.

### Initials (声母) — 21 Total

| # | Initial | Sound Like | Example |
|---|---------|-----------|---------|
| 1 | b | b in "boy" (unaspirated) | 八 bā — eight |
| 2 | p | p in "pay" (aspirated) | 跑 pǎo — run |
| 3 | m | m in "me" | 妈妈 māma — mom |
| 4 | f | f in "fun" | 飞机 fēijī — airplane |
| 5 | d | d in "dog" (unaspirated) | 大 dà — big |
| 6 | t | t in "top" (aspirated) | 他 tā — he |
| 7 | n | n in "no" | 你 nǐ — you |
| 8 | l | l in "love" | 来 lái — come |
| 9 | g | g in "go" (unaspirated) | 高 gāo — tall |
| 10 | k | k in "kite" (aspirated) | 开 kāi — open |
| 11 | h | h in "hot" | 好 hǎo — good |
| 12 | j | like "jee" in "jeep" (soft) | 家 jiā — home |
| 13 | q | like "chee" in "cheese" | 七 qī — seven |
| 14 | x | like "sh" but smile wider | 学 xué — study |
| 15 | zh | "j" with tongue curled back | 知道 zhīdào — know |
| 16 | ch | "ch" with tongue curled back | 吃 chī — eat |
| 17 | sh | "sh" with tongue curled back | 是 shì — is |
| 18 | r | like "r" but with friction | 人 rén — person |
| 19 | z | "dz" in "kids" | 在 zài — at |
| 20 | c | "ts" in "cats" | 菜 cài — dish |
| 21 | s | s in "see" | 三 sān — three |

### Finals (韵母) — 36 Total

| # | Final | Sound Like | Example |
|---|-------|-----------|---------|
| 1 | a | "ah" | 大 dà |
| 2 | o | "or" | 我 wǒ |
| 3 | e | "uh" | 饿 è |
| 4 | i | "ee" | 一 yī |
| 5 | u | "oo" | 五 wǔ |
| 6 | ü | like French "u" | 女 nǚ |
| 7 | ai | "eye" | 爱 ài |
| 8 | ei | "hey" | 对 duì |
| 9 | ao | "ow" | 好 hǎo |
| 10 | ou | "oh" | 走 zǒu |

## Key Takeaways

- 21 initials + 36 finals = ~400 syllables total
- The key difference from English is aspiration: b vs p, d vs t, g vs k
- Practice each initial-final combination with all 4 tones
""")

    write_file(base / 'part1-pinyin/02-tones.md', """# The Four Tones — Chinese Is a Musical Language

## Why Tones Matter

In Chinese, **tones change meaning**. The same syllable "ma" with different tones means completely different things:

| Tone | Mark | ma = | Example |
|------|------|------|---------|
| 1st (阴平) | mā | mom (妈) | 妈妈 māma |
| 2nd (阳平) | má | hemp (麻) | 麻烦 máfan |
| 3rd (上声) | mǎ | horse (马) | 马上 mǎshàng |
| 4th (去声) | mà | scold (骂) | 骂人 màrén |
| Neutral (轻声) | ma | question particle | 好吗 hǎo ma |

## Tone Descriptions

```
Chinese: 一声平，二声扬，三声拐弯，四声降
Pinyin: yì shēng píng, èr shēng yáng, sān shēng guǎiwān, sì shēng jiàng
Literal: 1st tone flat, 2nd tone rise, 3rd tone dip-then-rise, 4th tone fall
English: "1st is flat, 2nd rises up, 3rd goes down then up, 4th falls down."
```

## Visual Guide

```
Tone 1: ───── (flat, high)    mā — mom
Tone 2:   ╱   (rising)        má — hemp
Tone 3:  ╲╱  (dip-then-rise)  mǎ — horse
Tone 4:   ╲   (falling)       mà — scold
```

## Practice Sentences

```
Chinese: 妈 妈 骂 马 吗？
Pinyin: Māma mà mǎ ma?
Literal: mom scold horse [question]?
English: "Does mom scold the horse?"
```
This sentence uses all 4 tones + neutral on "ma"!

## Key Takeaways

- Tone 1: flat and high (sing a sustained note)
- Tone 2: rising (like asking "Really?")
- Tone 3: dips then rises (like saying "Well...")
- Tone 4: sharp fall (like saying "No!")
- Neutral: light and short
""")

    write_file(base / 'part1-pinyin/03-pinyin-rules.md', """# Pinyin Rules — What You Need to Know

## Essential Spelling Rules

### Rule 1: i → y at start of word
| Original | Becomes | Example |
|----------|---------|---------|
| ian → yan | | 眼 yǎn — eye |
| in → yin | | 因为 yīnwèi — because |
| ing → ying | | 电影 diànyǐng — movie |

### Rule 2: u → w at start of word
| Original | Becomes | Example |
|----------|---------|---------|
| uan → wan | | 完 wán — finish |
| u → wu | | 五 wǔ — five |

### Rule 3: ü loses dots after j, q, x
| Written | Pronounced | Example |
|---------|-----------|---------|
| ju | jü | 句子 jùzi — sentence |
| qu | qü | 去 qù — go |
| xu | xü | 学 xué — study |

**But keeps dots after l and n:**
- 女 nǚ — woman
- 绿 lǜ — green

### Rule 4: ü → yu at start of word
| Original | Becomes | Example |
|----------|---------|---------|
| üe → yue | | 月 yuè — month |
| üan → yuan | | 元 yuán — yuan |

## Tone Mark Placement

Tone marks always go on the **main vowel** of the syllable, in this priority order:

1. **a** gets the mark first: mā, bá, dǎ
2. If no a: **o** or **e**: mō, lè
3. If both i and u: mark the **second** one: liú, duì

## Key Takeaways

- i/u become y/w at the start of syllables
- ü loses dots after j/q/x but keeps them after l/n
- Tone marks follow a→o/e→i/u priority
""")

    write_file(base / 'part1-pinyin/04-tone-changes.md', """# Tone Changes — When Tones Shift

## Third Tone Sandhi

When **two 3rd tones** are next to each other, the first becomes 2nd:

| Original | Actually Say | Meaning |
|----------|-------------|---------|
| nǐ hǎo → ní hǎo | ní hǎo | hello |
| hěn hǎo → hén hǎo | hén hǎo | very good |

## "一" (yī) Tone Changes

The word "一" (one) changes tone based on what follows:

| Before... | "一" becomes | Example |
|-----------|-------------|---------|
| 1st/2nd/3rd tone | 4th tone (yì) | 一天 yì tiān |
| 4th tone | 2nd tone (yí) | 一样 yí yàng |
| Alone | 1st tone (yī) | 一 yī |

## "不" (bù) Tone Changes

The word "不" (not) changes before 4th tone:

| Before... | "不" becomes | Example |
|-----------|-------------|---------|
| 4th tone | 2nd tone (bú) | 不是 bú shì |
| Other tones | Stays 4th (bù) | 不好 bù hǎo |
| Alone | 4th tone (bù) | 不 bù |

## Key Takeaways

- 3rd + 3rd → 2nd + 3rd (most important rule!)
- 一 changes to 4th or 2nd depending on context
- 不 changes to 2nd only before 4th tone
- These changes happen naturally — don't overthink them
""")

    write_file(base / 'part1-pinyin/05-pinyin-practice.md', """# Pinyin Practice — Drills

## Drill 1: Tone Identification

Listen to each word and identify the tone (1-4):

| # | Word | Your Tone | Check |
|---|------|-----------|-------|
| 1 | māma | ? | 1-0 |
| 2 | nǐ hǎo | ? | 3-3 |
| 3 | chī fàn | ? | 1-4 |
| 4 | hē shuǐ | ? | 1-3 |
| 5 | dà xué | ? | 4-2 |

## Drill 2: Minimal Pairs

Distinguish between similar words that differ only in tone:

```
Chinese: 买 和 卖
Pinyin: mǎi hé mài
Literal: buy and sell
English: "mǎi (3rd) = buy, mài (4th) = sell"
```

```
Chinese: 买 菜
Pinyin: mǎi cài
Literal: buy dish/vegetables
English: "buy groceries"
```

```
Chinese: 卖 菜
Pinyin: mài cài
Literal: sell dish/vegetables
English: "sell vegetables"
```

## Drill 3: Read Aloud

Practice reading these sentences aloud:

```
Chinese: 你好！我叫小明。
Pinyin: Nǐ hǎo! Wǒ jiào Xiǎo Míng.
Literal: you good! I called small bright.
English: "Hello! My name is Xiao Ming."
```

```
Chinese: 今天天气很好。
Pinyin: Jīntiān tiānqì hěn hǎo.
Literal: today weather very good.
English: "The weather is very good today."
```

## Key Takeaways

- Practice tones daily — they're the foundation of all Chinese communication
- Record yourself and compare to native audio
- Use hand gestures to reinforce tone shapes
- Don't skip tone practice — it will come back to hurt you later
""")

    # Part 2: Vocabulary & Grammar
    vocab1 = vocab_for_level(1, 80)

    for i, (topic_zh, topic_en, word_list) in enumerate(VOCAB_TOPICS[1]):
        fname = f'{i+1:02d}-{topic_en.lower().replace(" ", "-")}.md'
        content = f"""# {topic_en} — {topic_zh}

## Core Vocabulary

{gen_vocab_table(vocab1[i*10:(i+1)*10] if i*10 < len(vocab1) else [])}

## Key Expressions

"""
        write_file(base / f'part2-vocabulary-grammar/{fname}', content)

    # Core grammar
    write_file(base / 'part2-vocabulary-grammar/07-basic-grammar.md', """# Basic Grammar — HSK 1 Essentials

## SVO Word Order (Same as English!)

Chinese follows **Subject-Verb-Object** order, just like English:

```
Chinese: 我 吃 苹果。
Pinyin: Wǒ chī píngguǒ.
Literal: I eat apple.
English: "I eat apples."
```

```
Chinese: 他 喝 茶。
Pinyin: Tā hē chá.
Literal: He drink tea.
English: "He drinks tea."
```

## 是 (shì) — To Be

Used to connect two nouns (A = B):

```
Chinese: 我 是 学生。
Pinyin: Wǒ shì xuéshēng.
Literal: I am student.
English: "I am a student."
```

```
Chinese: 他 是 老师。
Pinyin: Tā shì lǎoshī.
Literal: He is teacher.
English: "He is a teacher."
```

**Negative:** 不是 (bú shì)

```
Chinese: 我 不是 医生。
Pinyin: Wǒ bú shì yīshēng.
Literal: I am-not doctor.
English: "I am not a doctor."
```

## 有 (yǒu) — To Have

```
Chinese: 我 有 一个 问题。
Pinyin: Wǒ yǒu yí gè wèntí.
Literal: I have one classifier question.
English: "I have a question."
```

**Negative:** 没有 (méiyǒu)

```
Chinese: 他 没有 钱。
Pinyin: Tā méiyǒu qián.
Literal: He not-have money.
English: "He doesn't have money."
```

## 在 (zài) — To Be At/In

```
Chinese: 我 在 学校。
Pinyin: Wǒ zài xuéxiào.
Literal: I am-at school.
English: "I am at school."
```

## 吗 (ma) — Question Particle

Add 吗 to the end of a statement to make it a yes/no question:

```
Chinese: 你 是 学生 吗？
Pinyin: Nǐ shì xuéshēng ma?
Literal: you are student [question]?
English: "Are you a student?"
```

```
Chinese: 你 吃 饭 吗？
Pinyin: Nǐ chī fàn ma?
Literal: you eat rice [question]?
English: "Do you eat?"
```

## 的 (de) — Possession

```
Chinese: 我 的 书
Pinyin: wǒ de shū
Literal: my [possessive] book
English: "my book"
```

```
Chinese: 他 的 老师
Pinyin: tā de lǎoshī
Literal: his [possessive] teacher
English: "his teacher"
```

## Numbers + Classifiers

| Number | Pinyin |
|--------|--------|
| 一 | yī |
| 二/两 | èr / liǎng |
| 三 | sān |
| 四 | sì |
| 五 | wǔ |
| 六 | liù |
| 七 | qī |
| 八 | bā |
| 九 | jiǔ |
| 十 | shí |

**Classifier 个 (ge):** Used for most general objects:

```
Chinese: 一 个人
Pinyin: yí gè rén
Literal: one classifier person
English: "one person"
```

## Question Words

| Chinese | Pinyin | English |
|---------|--------|---------|
| 什么 | shénme | what |
| 谁 | shéi | who |
| 哪里 | nǎlǐ | where |
| 怎么 | zěnme | how |
| 几 | jǐ | how many (small numbers) |
| 多少 | duōshao | how much/many |
| 为什么 | wèishénme | why |

```
Chinese: 你 叫 什么 名字？
Pinyin: Nǐ jiào shénme míngzi?
Literal: you called what name?
English: "What is your name?"
```

## Key Takeaways

- Chinese word order = SVO (same as English)
- 是 = A equals B; 有 = possess; 在 = location
- 吗 turns any statement into a question
- 的 = possession ('s / of)
- Use 个 as the default classifier
""")

    # Part 3: Listening
    write_file(base / 'part3-listening/01-task1-picture.md', """# Listening Task 1 — Picture Selection (Questions 1-5)

## Task Format
You hear a single word or short phrase. Choose the matching picture from 3 options (A, B, C).

## Strategy
1. **Preview all 3 pictures** before the audio starts
2. **Listen for the KEY word** — usually the only content word in the audio
3. **Eliminate obviously wrong answers** first
4. **Choose immediately** — don't wait

## Practice Items

**Item 1:** You hear: "苹果" (píngguǒ — apple)
- Picture A: A banana
- Picture B: An orange
- Picture C: An apple ← **Correct**

**Item 2:** You hear: "老师" (lǎoshī — teacher)
- Picture A: A doctor
- Picture B: A teacher ← **Correct**
- Picture C: A student

## Key Takeaways

- Preview pictures first
- Listen for the key content word
- Answer immediately and move on
""")

    write_file(base / 'part3-listening/02-task2-keywords.md', """# Listening Task 2 — Sentence to Word (Questions 6-10)

## Task Format
You hear a short sentence. Choose the word that best relates to it from 3 options (each with pinyin shown).

## Strategy
1. **Read all 3 options quickly** before audio
2. **Catch the KEYWORD** in the sentence
3. **Match** the keyword to one of the options

## Practice Items

You hear: "今天天气怎么样？" (jīntiān tiānqì zěnmeyàng? — How's the weather today?)

Options:
- A 在学习 (zài xuéxí — studying)
- B 很好听 (hěn hǎotīng — sounds good)
- C 非常热 (fēicháng rè — very hot) ← **Correct** (relates to weather)

## Key Takeaways

- The question word tells you the topic: 天气 = weather, 多少钱 = price
- Match the topic to the correct option
""")

    write_file(base / 'part3-listening/03-task3-dialogue.md', """# Listening Task 3 — Dialogue to Picture (Questions 11-15)

## Task Format
You hear a short dialogue (2 people). Choose the matching picture from 6 options (A-F).

## Strategy
1. **Scan all 6 pictures in 3 seconds**
2. **Listen for WHO and WHAT**
3. **Match the scene** — not individual words, the overall situation

## Practice Items

You hear:
- 女：你好！(Nǚ: Nǐ hǎo! — Woman: Hello!)
- 男：你好，很高兴认识你！(Nán: Nǐ hǎo, hěn gāoxìng rènshi nǐ! — Man: Hello, nice to meet you!)

This is a "meeting someone new" scene.

## Key Takeaways

- Focus on the SITUATION, not individual words
- 6 options means quick elimination is essential
""")

    write_file(base / 'part3-listening/04-task4-short-text.md', """# Listening Task 4 — Short Passage Q&A (Questions 16-20)

## Task Format
You hear a short passage (1-2 sentences), then a question. Choose from 3 options.

## Strategy
1. **Read the question and options FIRST** (printed on the paper)
2. **Listen for the answer** while hearing the passage
3. **Match directly**

## Practice Items

You hear: "下午我去超市，我想买一些水果。"
(xiàwǔ wǒ qù chāoshì, wǒ xiǎng mǎi yìxiē shuǐguǒ.)
"This afternoon I go to supermarket, I want to buy some fruits."

Question: "说话人下午去哪里？" (shuōhuàrén xiàwǔ qù nǎlǐ? — Where does the speaker go this afternoon?)

Options:
- A 超市 (chāoshì — supermarket) ← **Correct**
- B 医院 (yīyuàn — hospital)
- C 学校 (xuéxiào — school)

## Key Takeaways

- Always read the question before the audio starts
- The answer is usually stated directly
- Common question patterns: 去哪里 (where), 做什么 (what doing), 什么 (what)
""")

    write_file(base / 'part3-listening/05-listening-mock.md', """# Listening Mock Practice — Full Set

## Practice Listening Test (20 questions)

### Part 1 (Questions 1-5)
1. You hear: 妈妈 → Choose: A banana, B mom, C book
2. You hear: 吃 → Choose: A eating, B sleeping, C reading
3. You hear: 学校 → Choose: A hospital, B school, C supermarket
4. You hear: 大 → Choose: A small, B big, C medium
5. You hear: 水 → Choose: A tea, B water, C juice

### Part 2 (Questions 6-10)
6. You hear: "你好吗？" → A fine, B eating, C going
7. You hear: "几点了？" → A time, B money, C name
8. You hear: "我要一杯茶" → A tea, B rice, C book
9. You hear: "他很高" → A tall, B short, C fat
10. You hear: "今天很冷" → A hot, B cold, C warm

### Part 3 (Questions 11-15)
11. Dialogue: "请问，去火车站怎么走？" → Directions scene
12. Dialogue: "这个多少钱？" → Shopping scene
13. Dialogue: "你吃药了吗？" → Health scene
14. Dialogue: "我们去吃午饭吧。" → Restaurant scene
15. Dialogue: "明天见！" → Saying goodbye scene

### Part 4 (Questions 16-20)
16. Passage: "我每天早上七点起床，吃早饭，然后去上班。" → Question: 他几点起床？
17. Passage: "我的爸爸是医生，妈妈是老师。" → Question: 妈妈做什么？
18. Passage: "这个星期天我去上海玩。" → Question: 去哪里？
19. Passage: "她会说英语和中文。" → Question: 她会几种语言？
20. Passage: "外面在下雨，你带伞了吗？" → Question: 天气怎么样？

## Answer Key
1-B, 2-A, 3-B, 4-B, 5-B, 6-A, 7-A, 8-A, 9-A, 10-B, 11-directions, 12-shopping, 13-health, 14-restaurant, 15-goodbye, 16-七点, 17-老师, 18-上海, 19-两种, 20-下雨
""")

    # Part 4: Reading
    write_file(base / 'part4-reading/01-task1-sentence-picture.md', """# Reading Task 1 — Sentence to Picture (Questions 21-25)

## Task Format
Read a sentence with pinyin. Choose the matching picture from 6 options (A-F).

## Strategy
1. **Scan all 6 pictures** first (5 seconds)
2. **Read the sentence** — identify the key content words
3. **Eliminate** pictures that don't match
4. **Choose** the best match

## Practice

Sentence: "我很喜欢这本书。" (Wǒ hěn xǐhuan zhè běn shū.)
Key words: 喜欢 (like), 书 (book) → Find the picture about liking/reading a book.

Sentence: "外面在下雨。" (Wàimiàn zài xiàyǔ.)
Key words: 外面 (outside), 下雨 (raining) → Find the picture showing rain.

## Key Takeaways

- Identify the KEY content word (usually a noun or verb)
- Eliminate obviously wrong pictures first
- 6 options = scan quickly
""")

    write_file(base / 'part4-reading/02-task2-sentence-response.md', """# Reading Task 2 — Choose Response (Questions 26-30)

## Task Format
Read a sentence. Choose the appropriate response from 6 options (A-F).

## Strategy
1. **Identify the TYPE** of sentence: question, statement, greeting
2. **Think about natural conversation flow**
3. **Match** the most logical response

## Practice

Statement: "你喝水吗？" (Nǐ hē shuǐ ma? — Do you want water?)
Response: "好的，谢谢！" (Hǎo de, xièxie! — OK, thanks!) ← Correct

Statement: "你叫什么名字？" (Nǐ jiào shénme míngzi?)
Response: "我叫小明。" (Wǒ jiào Xiǎo Míng.) ← Correct

## Key Takeaways

- Questions → answers
- Greetings → return greeting
- Invitations → accept/decline response
""")

    write_file(base / 'part4-reading/03-task3-fill-blank.md', """# Reading Task 3 — Fill in the Blank (Questions 31-35)

## Task Format
A sentence with a blank. Choose from 6 word options (A-F).

## Strategy
1. **Read the FULL sentence first**
2. **Identify what type of word** is missing (verb? noun? preposition?)
3. **Eliminate** words that don't fit grammatically
4. **Choose** from remaining options

## Practice

"你（ ）什么名字？" → Missing: verb for "called" → 叫 (jiào)

"今天天气很（ ）。" → Missing: adjective → 好/热/冷

"我（ ）学生。" → Missing: 是 (shì — to be)

## Key Takeaways

- Grammar patterns help: 是 + noun, 很 + adjective, 在 + place
- Elimination is your best friend
""")

    write_file(base / 'part4-reading/04-task4-comprehension.md', """# Reading Task 4 — Reading Comprehension (Questions 36-40)

## Task Format
Read a short passage (1-3 sentences). Answer a question.

## Strategy
1. **Read the QUESTION first** (know what to look for)
2. **Scan the passage** for keywords related to the question
3. **Find the answer** — it's usually directly stated

## Practice

Passage: "请问现在几点了？" (Qǐngwèn xiànzài jǐ diǎn le?)
Question: "说话人想知道什么？" (What does the speaker want to know?)

Options:
- A 时间 (shíjiān — time) ← Correct
- B 名字 (míngzi — name)
- C 房间号 (fángjiān hào — room number)

## Key Takeaways

- Read the question FIRST
- 请问 = excuse me, 想知道 = want to know
- Look for time words (几点), place words (哪里), person words (谁)
""")

    write_file(base / 'part4-reading/05-reading-mock.md', """# Reading Mock Practice — Full Set

## Practice Reading Test (20 questions)

### Part 1 (21-25): Sentence to Picture
21. 我吃饭。 → eating scene
22. 她在打电话。 → phone scene
23. 今天很热。 → hot weather scene
24. 这是我的家。 → family/home scene
25. 我们去公园。 → park scene

### Part 2 (26-30): Choose Response
26. "你好！" → "你好！"
27. "你吃饭了吗？" → "吃了，你呢？"
28. "谢谢！" → "不客气！"
29. "再见！" → "明天见！"
30. "你忙吗？" → "很忙。"

### Part 3 (31-35): Fill in the Blank
31. 我（ ）老师。→ 是
32. 你（ ）中国菜吗？→ 喜欢
33. 今天（ ）很好。→ 天气
34. 他（ ）学校。→ 在
35. 这（ ）多少钱？→ 本

### Part 4 (36-40): Comprehension
36. Passage about weather → Question about temperature
37. Passage about family → Question about number of people
38. Passage about daily routine → Question about time
39. Passage about shopping → Question about price
40. Passage about travel → Question about destination

## Answer Key
31-是, 32-喜欢, 33-天气, 34-在, 35-本 (classifier for books)
""")

    # Part 5: Exam Tips
    write_file(base / 'part5-exam-tips/01-top-10-points.md', """# Top 10 High-Frequency Exam Points — HSK 1

## 1. 是 (shì) — The "equals" verb
Tested in 3-5 questions. Know: 是 + noun, 不是 + noun

## 2. 有 (yǒu) — Possession
Tested in 2-3 questions. Know: 有 + object, 没有 + object

## 3. 在 (zài) — Location
Tested in 2-3 questions. Know: 在 + place

## 4. Numbers + Time
Tested in 2-3 questions. Know how to say time: 三点半 (3:30)

## 5. Question Words
Tested in 2-3 questions. 什么/谁/哪里/怎么/几/多少

## 6. 的 (de) — Possession
Tested in 1-2 questions. 我的书, 他的老师

## 7. 吗 (ma) — Questions
Tested in 1-2 questions. 你好吗？你是学生吗？

## 8. Measure Words
Tested in 1-2 questions. 一个, 这本书

## 9. 很 (hěn) — "Very"
Tested in 1-2 questions. 很好, 很大

## 10. Common Daily Phrases
Tested throughout. 吃饭, 喝水, 去学校, 回家
""")

    write_file(base / 'part5-exam-tips/02-common-traps.md', """# Common Traps & Test-Maker Tricks

## Trap 1: Similar-Sounding Words
Test makers often use words that sound similar:
- 水 (shuǐ — water) vs 睡 (shuì — sleep)
- 买 (mǎi — buy) vs 卖 (mài — sell)

**Defense:** Pay attention to tones!

## Trap 2: Negation Confusion
- 不 (bù) vs 没有 (méiyǒu): 不 for present/future, 没有 for past/experience
- At HSK 1: just know 不 = not, 没有 = don't have

## Trap 3: Picture Similarity
Two pictures might look similar (apple vs orange).
**Defense:** Listen/read carefully for the specific word.

## Trap 4: Time Words Confusion
今天 (today) vs 明天 (tomorrow) vs 昨天 (yesterday)
**Defense:** Read carefully, circle time words.

## Key Takeaways

- Tone differences create traps
- Time words are commonly confused
- Always double-check before moving on
""")

    write_file(base / 'part5-exam-tips/03-confusing-words.md', """# Confusing Words — Quick Discrimination Guide

## 是 vs 有 vs 在

| Word | Meaning | Pattern | Example |
|------|---------|---------|---------|
| 是 | to be (equals) | 是 + noun | 我是学生 |
| 有 | to have | 有 + object | 我有书 |
| 在 | to be at | 在 + place | 我在家 |

## 几 vs 多少

| Word | Usage | Example |
|------|-------|---------|
| 几 | Small numbers (1-10), with classifier | 几个人？ |
| 多少 | Any number, no classifier needed | 多少钱？ |

## 怎么 vs 为什么

| Word | Meaning | Example |
|------|---------|---------|
| 怎么 | How (method) | 怎么走？ |
| 为什么 | Why (reason) | 为什么？ |

## 和 vs 跟

| Word | Usage |
|------|-------|
| 和 | and (connects nouns) | 我和他 |
| 跟 | with (preposition) | 我跟他去 |
""")

    write_file(base / 'part5-exam-tips/04-time-management.md', """# Time Management Strategy

## Listening: ~12 minutes (20 questions)
- **Don't control timing** — audio plays at fixed speed
- **Preview during gaps**: Use time between questions to scan options
- **Mark immediately**: Never wait — you'll forget

## Reading: 20 minutes (20 questions)
- **1 minute per question** average
- **Part 1 (21-25):** 3 minutes — picture matching is fast
- **Part 2 (26-30):** 4 minutes — think about conversation flow
- **Part 3 (31-35):** 5 minutes — grammar-based, take your time
- **Part 4 (36-40):** 6 minutes — read carefully
- **Review:** 2 minutes — check answer sheet

## Golden Rules
1. Never spend more than 90 seconds on one question
2. If stuck, mark a guess and move on
3. Use the review time to check answer sheet alignment
4. Listening: the pace is set — focus on each question, don't dwell
""")

    # Part 6: Mock Exams
    for exam_num in range(1, 4):
        write_file(base / f'part6-mock-exams/mock-exam-{exam_num}.md', f"""# Full Mock Exam {exam_num} — HSK Level 1

## Instructions
- Total: 40 questions
- Listening: 20 questions (~12 minutes)
- Reading: 20 questions (20 minutes)
- No writing module at Level 1

---

## Listening Section (20 questions)

### Part 1 (Questions 1-5): Picture Selection
*You will hear a word. Choose the matching picture.*

1. 包子 (bāozi — steamed bun)
2. 医院 (yīyuàn — hospital)
3. 看书 (kànshū — reading)
4. 热 (rè — hot)
5. 飞机 (fēijī — airplane)

### Part 2 (Questions 6-10): Sentence to Word
*You will hear a sentence. Choose the related word.*

6. "我饿了。" → A 饭 B 书 C 床
7. "今天很冷。" → A 热 B 冷 C 下雨
8. "我要买票。" → A 车站 B 医院 C 学校
9. "他在学习。" → A 玩 B 学习 C 睡觉
10. "外面在下雨。" → A 晴天 B 下雨 C 下雪

### Part 3 (Questions 11-15): Dialogue to Picture
*You will hear a dialogue. Choose the matching picture.*

11. "你要吃什么？" "我想吃米饭。" → Restaurant
12. "请问，医院在哪里？" "在那边。" → Asking directions
13. "你好，我是新同学。" "欢迎！" → Meeting new person
14. "这件衣服多少钱？" "一百块。" → Shopping
15. "再见！" "明天见！" → Saying goodbye

### Part 4 (Questions 16-20): Short Passage Q&A
*You will hear a passage. Answer the question.*

16. "我每天早上六点起床。" → 他几点起床？
17. "我爸爸是医生。" → 他爸爸做什么？
18. "这个周末我去北京。" → 去哪里？
19. "她会说两种语言。" → 几种语言？
20. "外面在下雪，很冷。" → 天气怎么样？

---

## Reading Section (20 questions)

### Part 1 (Questions 21-25): Sentence to Picture

21. 我在吃饭。
22. 她在睡觉。
23. 今天很热。
24. 这是我的书。
25. 我们去学校。

### Part 2 (Questions 26-30): Choose Response

26. "你好！"
27. "你吃饭了吗？"
28. "谢谢！"
29. "再见！"
30. "你忙吗？"

### Part 3 (Questions 31-35): Fill in the Blank

31. 我（ ）学生。
32. 你（ ）水吗？
33. 今天（ ）很好。
34. 他（ ）家。
35. 这（ ）书是我的。

### Part 4 (Questions 36-40): Comprehension

36. 请问现在几点了？ → 说话人想知道什么？
37. 我妈妈是老师，爸爸是医生。 → 妈妈做什么？
38. 今天我去超市买东西。 → 去哪里？
39. 他会说英语。 → 他会什么语言？
40. 外面在下雨，你带伞了吗？ → 天气怎么样？

---

## Answer Key (Mock Exam {exam_num})

**Listening:** 1-包子, 2-医院, 3-看书, 4-热, 5-飞机
6-A, 7-B, 8-A, 9-B, 10-B
11-餐厅, 12-问路, 13-欢迎, 14-购物, 15-再见
16-六点, 17-医生, 18-北京, 19-两种, 20-下雪

**Reading:** 21-吃饭, 22-睡觉, 23-热, 24-书, 25-学校
26-你好, 27-吃了, 28-不客气, 29-明天见, 30-很忙
31-是, 32-喝, 33-天气, 34-在, 35-本
36-时间, 37-老师, 38-超市, 39-英语, 40-下雨
""")

    # Appendices
    vocab_all = vocab.get(1, [])
    vocab_table = gen_vocab_appendix(vocab_all)
    write_file(base / 'appendices/A-vocabulary-list.md', f"""# Appendix A: HSK 1 Complete Vocabulary List (300 words)

## Full Vocabulary Reference

{vocab_table}

**Note:** `Word (简体)` uses normalized simplified Chinese, and `English Meaning` is filled from the local glossary plus cached online fallback for uncovered items.
""")

    write_file(base / 'appendices/B-character-list.md', """# Appendix B: HSK 1 Character List

## Must-Read Characters (认读字)

| Character | Pinyin | Meaning |
|-----------|--------|---------|
| 一 | yī | one |
| 二 | èr | two |
| 三 | sān | three |
| 四 | sì | four |
| 五 | wǔ | five |
| 六 | liù | six |
| 七 | qī | seven |
| 八 | bā | eight |
| 九 | jiǔ | nine |
| 十 | shí | ten |
| 百 | bǎi | hundred |
| 人 | rén | person |
| 大 | dà | big |
| 小 | xiǎo | small |
| 中 | zhōng | middle |
| 上 | shàng | up/above |
| 下 | xià | down/below |
| 天 | tiān | sky/day |
| 水 | shuǐ | water |
| 火 | huǒ | fire |
""")

    write_file(base / 'appendices/C-grammar-reference.md', """# Appendix C: Grammar Quick Reference

## Core Grammar Patterns

| Pattern | Example | Meaning |
|---------|---------|---------|
| A 是 B | 我是学生 | A is B |
| A 有 B | 我有书 | A has B |
| A 在 B | 我在家 | A is at B |
| A 不 B | 我不忙 | A is not B |
| A 很 B | 我很好 | A is very B |
| A 吗？ | 你好吗？ | A? (question) |
| A 的 B | 我的书 | A's B |
| 一 + classifier + noun | 一个人 | one person |

## Question Patterns

| Question | Pattern |
|----------|---------|
| What? | 什么 + noun? / 是什么？ |
| Who? | 谁？ |
| Where? | 在哪里？ / 去哪里？ |
| When? | 什么时候？ / 几点？ |
| How? | 怎么 + verb? |
| Why? | 为什么？ |
| How many? | 几 + classifier? / 多少？ |
""")

    write_file(base / 'appendices/D-exam-points.md', """# Appendix D: High-Frequency Exam Points

## Top 15 Most-Tested Items

1. 是 (shì) — 3-5 questions per exam
2. 有 (yǒu) — 2-3 questions
3. 在 (zài) — 2-3 questions
4. Numbers & time — 2-3 questions
5. Question words — 2-3 questions
6. 的 (de) — 1-2 questions
7. 吗 (ma) — 1-2 questions
8. 很 (hěn) — 1-2 questions
9. Classifiers — 1-2 questions
10. 不/没 — 1-2 questions
11. 去/来 — 1 question
12. 想/要 — 1 question
13. 会/能 — 1 question
14. 和 — 1 question
15. 这/那 — 1 question
""")

    write_file(base / 'appendices/E-answer-sheet-guide.md', """# Appendix E: Answer Sheet Guide

## How to Mark Your Answers

1. Use **2B pencil** only
2. **Fill the circle completely** — don't just make a dot
3. **Erase completely** if changing an answer
4. **Check question numbers** match answer row numbers

## Common Mistakes

- Marking two answers for one question
- Skipping a question number (answers misaligned)
- Erasing partially (machine can't read)
- Forgetting to mark the answer sheet entirely

## Pre-Exam Checklist

- [ ] ID card / passport
- [ ] 2B pencil (2 spare)
- [ ] Eraser
- [ ] Exam confirmation
- [ ] Arrive 30 minutes early
""")

    print(f"HSK 1: Generated {len(list(base.rglob('*.md')))} files")


# ============================================================
# HSK 2-6 and 7-9 — Similar structure
# ============================================================

def generate_hsk_structure(level):
    """Generate structure files for HSK levels 2-6."""
    structure = EXAM_STRUCTURE[level]
    name_zh, name_en = LEVEL_NAMES[level]
    base = BASE / f'HSK备考/hsk{level}-prep'

    # Exam overview
    write_file(base / 'part0-exam-overview/01-hsk-intro.md', f"""# HSK {level} 备考完全指南
## {name_zh} — Level {level} Complete Prep Guide

> **2026年最新版 · 基于HSK 3.0官方考试大纲**

Published: 2026 | Author: Tony Sheng | Series: Z Turns Chinese

The definitive preparation guide for HSK Level {level} ({name_en}).
Based on the official HSK 3.0 syllabus released November 2025, implemented July 2026.
""")

    # Build listening breakdown table
    listening_rows = ""
    for i, n in enumerate(structure['listening']['parts']):
        task = get_listening_task(level, i)
        listening_rows += f"| Part {i+1} | {n} | {task} |\n"

    write_file(base / 'part0-exam-overview/02-exam-structure.md', f"""# HSK {level} Exam Structure

## Overview

| Section | Questions | Duration |
|---------|-----------|----------|
| Listening (听力) | {structure['listening']['total']} | {structure['listening']['duration']} |
| Reading (阅读) | {structure['reading']['total']} | {structure['reading']['duration']} |
{'| Writing (写作) | ' + str(structure['writing']['total']) + ' | ' + str(structure['writing']['duration']) + ' |' if structure.get('writing') else ''}
| **Total** | **{structure['total_q']}** | **{structure['total_time']}** |

## Listening Breakdown

| Part | Questions | Task Type |
|------|-----------|-----------|
{listening_rows}
""")

    # Vocabulary by topic
    topics = VOCAB_TOPICS.get(level, [])
    for i, (topic_en, topic_zh, word_hint) in enumerate(topics):
        fname = f'{i+1:02d}-{topic_en.lower().replace(" ", "-")}.md'
        words = vocab_for_level(level, 50)
        content = f"""# {topic_en} — {topic_zh}

## Core Vocabulary

{gen_vocab_table(words[:20])}

## Key Points

Focus on these {topic_zh} terms. They appear frequently in listening and reading sections.
"""
        write_file(base / f'part1-vocabulary-grammar/{fname}', content)

    # Grammar for each level
    grammar_content = get_grammar_content(level)
    write_file(base / f'part1-vocabulary-grammar/{len(topics)+1:02d}-grammar.md', grammar_content)

    # Listening sections
    for i in range(len(structure['listening']['parts'])):
        task_name = get_listening_task(level, i)
        write_file(base / f'part2-listening/0{i+1:02d}-{task_name.lower().replace(" ", "-")}.md', f"""# Listening Task {i+1} — {task_name}

## Task Description

Practice for {task_name} questions in the HSK {level} exam.

## Strategy

1. Preview options before audio starts
2. Listen for keywords
3. Answer immediately
4. Move on — don't dwell on missed questions
""")

    # Reading sections
    for i in range(len(structure['reading']['parts'])):
        task_name = get_reading_task(level, i)
        write_file(base / f'part3-reading/0{i+1:02d}-{task_name.lower().replace(" ", "-")}.md', f"""# Reading Task {i+1} — {task_name}

## Task Description

Practice for {task_name} questions.

## Strategy

1. Read questions first
2. Scan for keywords
3. Eliminate wrong answers
4. Verify your choice
""")

    # Writing sections (if applicable)
    if structure.get('writing'):
        for i in range(len(structure['writing']['parts'])):
            task_name = get_writing_task(level, i)
            write_file(base / f'part4-writing/0{i+1:02d}-{task_name.lower().replace(" ", "-")}.md', f"""# Writing Task {i+1} — {task_name}

## Task Description

Practice for {task_name}.

## Strategy

1. Read instructions carefully
2. Plan before writing
3. Check grammar and characters
4. Review your work
""")

    # Exam tips
    write_file(base / 'part5-exam-tips/01-top-points.md', f"""# Top Exam Points — HSK {level}

## Most Frequently Tested Grammar Points

Focus on mastering these patterns — they appear in almost every exam.
""")

    write_file(base / 'part5-exam-tips/02-common-traps.md', f"""# Common Traps — HSK {level}

## Test-Maker Tricks to Watch For

1. Similar-sounding words
2. Negation confusion
3. Time word mix-ups
4. Picture similarity
""")

    write_file(base / 'part5-exam-tips/03-time-management.md', f"""# Time Management — HSK {level}

## Total Time: {structure['total_time']}

### Reading Time Allocation
- Budget ~1 minute per question
- Save 2-3 minutes for review
""")

    # Mock exams
    for exam_num in range(1, 4):
        mock_content = f"""# Full Mock Exam {exam_num} — HSK Level {level}

## Instructions
- Total: {structure['total_q']} questions
- Listening: {structure['listening']['total']} questions
- Reading: {structure['reading']['total']} questions
{f'- Writing: {structure["writing"]["total"]} questions' if structure.get('writing') else ''}

---

## Listening Section ({structure['listening']['total']} questions)

### Part 1
Practice listening questions here.

### Part 2
Practice listening questions here.

---

## Reading Section ({structure['reading']['total']} questions)

### Part 1
Practice reading questions here.

### Part 2
Practice reading questions here.

---

## Answer Key

Answers and explanations for Mock Exam {exam_num}.
"""
        write_file(base / f'part6-mock-exams/mock-exam-{exam_num}.md', mock_content)

    # Appendices
    vocab_all = vocab.get(level, [])
    write_file(base / 'appendices/A-vocabulary-list.md', f"""# Appendix A: HSK {level} Vocabulary

## Full Vocabulary Reference

{gen_vocab_appendix(vocab_all)}

**Note:** Complete vocabulary list contains {len(vocab_all)} words. `Word (简体)` is cleaned to simplified display form, and `English Meaning` uses the local glossary plus cached online fallback when enabled.
""")

    write_file(base / 'appendices/B-grammar-reference.md', f"""# Appendix B: Grammar Quick Reference

## HSK {level} Grammar Patterns

Key grammar patterns tested at this level.
""")

    print(f"HSK {level}: Generated {len(list(base.rglob('*.md')))} files")

def get_listening_task(level, part_idx):
    tasks = {
        1: ['Picture Selection', 'Sentence to Word', 'Dialogue to Picture', 'Short Passage Q&A'],
        2: ['Picture Sentence', 'Dialogue Picture', 'Dialogue Q&A'],
        3: ['True/False Dialogue', 'Dialogue Choice', 'Passage Choice'],
        4: ['Dialogue Choice', 'Passage Choice'],
        5: ['Dialogue Choice', 'Passage News Choice'],
        6: ['Partial Dialogue', 'Full Dialogue', 'Speech Passage'],
    }
    return tasks.get(level, ['Task'])[part_idx] if part_idx < len(tasks.get(level, [''])) else 'Practice'

def get_reading_task(level, part_idx):
    tasks = {
        1: ['Sentence Picture', 'Choose Response', 'Fill Blank', 'Comprehension'],
        2: ['Sentence Picture', 'Fill Blank', 'Sentence Order', 'Comprehension'],
        3: ['Fill Blank', 'Sentence Fill', 'Comprehension'],
        4: ['Fill Blank', 'Sentence Fill', 'Comprehension'],
        5: ['Fill Blank', 'Sentence Fill', 'Long Comprehension'],
        6: ['Fill Blank', 'Sentence Order', 'Academic Reading'],
    }
    return tasks.get(level, ['Task'])[part_idx] if part_idx < len(tasks.get(level, [''])) else 'Practice'

def get_writing_task(level, part_idx):
    tasks = {
        2: ['Picture Sentence', 'Character Fill'],
        3: ['Sentence Order', 'Picture Sentence'],
        4: ['Sentence Order', 'Picture Essay'],
        5: ['Listen and Write', 'Picture Essay'],
        6: ['Summary Writing', 'Essay Writing'],
    }
    return tasks.get(level, ['Task'])[part_idx] if part_idx < len(tasks.get(level, [''])) else 'Practice'

def get_grammar_content(level):
    grammar_contents = {
        2: """# HSK 2 Core Grammar

## 了 (le) — Change of State / Completion

**Usage 1:** Completed action
```
Chinese: 我吃 了 饭。
Pinyin: Wǒ chī le fàn.
Literal: I eat [completed] rice.
English: "I ate food."
```

**Usage 2:** Change of state
```
Chinese: 下雨 了。
Pinyin: Xiàyǔ le.
Literal: rain [change].
English: "It's raining now."
```

## 比 (bǐ) — Comparison
```
Chinese: 他 比 我 高。
Pinyin: Tā bǐ wǒ gāo.
Literal: He compare me tall.
English: "He is taller than me."
```

## 虽然...但是 (suīrán...dànshì) — Although...but
```
Chinese: 虽然 下雨，但是 我 还是 去 了。
Pinyin: Suīrán xiàyǔ, dànshì wǒ háishì qù le.
Literal: Although rain, but I still go [completed].
English: "Although it was raining, I still went."
```

## 正在...呢 (zhèngzài...ne) — Currently doing
```
Chinese: 他 正在 学习 呢。
Pinyin: Tā zhèngzài xuéxí ne.
Literal: He currently studying [progressive].
English: "He is studying right now."
```
""",
        3: """# HSK 3 Core Grammar

## Complement System (补语)

### Result Complement
```
Chinese: 我吃 完 了 饭。
Pinyin: Wǒ chī wán le fàn.
Literal: I eat finish [completed] rice.
English: "I finished eating."
```

### Direction Complement
```
Chinese: 他 走 进来 了。
Pinyin: Tā zǒu jìnlái le.
Literal: He walk enter-come [completed].
English: "He walked in."
```

### Potential Complement
```
Chinese: 我 吃 不 完。
Pinyin: Wǒ chī bu wán.
Literal: I eat not-can finish.
English: "I can't finish eating."
```

## Passive: 被 (bèi)
```
Chinese: 杯子 被 打 破 了。
Pinyin: Bēizi bèi dǎ pò le.
Literal: Cup by hit break [completed].
English: "The cup was broken."
```

## Complex Sentences: 不但...而且
```
Chinese: 他 不但 聪明，而且 很 努力。
Pinyin: Tā búdàn cōngmíng, érqiě hěn nǔlì.
Literal: He not-only smart, but-also very hardworking.
English: "He is not only smart but also very hardworking."
```
""",
        4: """# HSK 4 Core Grammar

## 把 (bǎ) Sentences — Object Disposal
```
Chinese: 请 把 书 给 我。
Pinyin: Qǐng bǎ shū gěi wǒ.
Literal: Please take book give me.
English: "Please give me the book."
```

**Structure:** Subject + 把 + Object + Verb + Result

## 被 (bèi) Sentences — Passive
```
Chinese: 书 被 他 拿走 了。
Pinyin: Shū bèi tā ná zǒu le.
Literal: Book by he take away [completed].
English: "The book was taken away by him."
```

## 兼语句 (Pivotal Sentences)
```
Chinese: 老师 让 我们 做 作业。
Pinyin: Lǎoshī ràng wǒmen zuò zuòyè.
Literal: Teacher let us do homework.
English: "The teacher asked us to do homework."
```

## Emphasis: 是...的
```
Chinese: 我 是 昨天 来 的。
Pinyin: Wǒ shì zuótiān lái de.
Literal: I [emphatic] yesterday come [marker].
English: "It was yesterday that I came."
```
""",
        5: """# HSK 5 Core Grammar

## Formal Written Structures

### 鉴于 (jiànyú) — In view of
```
Chinese: 鉴于 以上 原因，我们 决定 推迟 会议。
Pinyin: Jiànyú yǐshàng yuányīn, wǒmen juédìng tuīchí huìyì.
Literal: In-view-of above reasons, we decide postpone meeting.
English: "In view of the above reasons, we decided to postpone the meeting."
```

### 与其...不如 (yǔqí...bùrú) — Rather than...it would be better
```
Chinese: 与其 抱怨，不如 行动。
Pinyin: Yǔqí bàoyuàn, bùrú xíngdòng.
Literal: Rather-than complain, better act.
English: "Rather than complain, it would be better to act."
```

### 无论...都 (wúlùn...dōu) — No matter...all
```
Chinese: 无论 什么 困难，我们 都 能 解决。
Pinyin: Wúlùn shénme kùnnán, wǒmen dōu néng jiějué.
Literal: No-matter what difficulty, we all can solve.
English: "No matter what difficulties, we can solve them all."
```
""",
        6: """# HSK 6 Core Grammar

## Advanced Discourse Connectors

### 诚然...然而 (chéngrán...rán'ér) — Admittedly...however
```
Chinese: 诚然 困难 很多，然而 并非 不可 克服。
Pinyin: Chéngrán kùnnán hěn duō, rán'ér bìng fēi bùkě kèfú.
Literal: Admittedly difficulties very many, however certainly not cannot overcome.
English: "Admittedly there are many difficulties, however they are not insurmountable."
```

### Nested Structures
```
Chinese: 虽然 他 说 的 那番 话，听起来 似乎 有 道理，然而 仔细 分析，却 经 不 起 推敲。
Pinyin: Suīrán tā shuō de nàfān huà, tīng qǐlái sìhu yǒu dàolǐ, rán'ér zǐxǐ fēnxī, què jīng bu qǐ tuīqiāo.
Literal: Although he said [possessive] those words, listen up seemingly have reason, however carefully analyze, yet withstand not careful consideration.
English: "Although what he said sounds reasonable, upon careful analysis, it does not withstand scrutiny."
```
"""
    }
    return grammar_contents.get(level, "# Grammar Content\n\nContent for this level.")


def generate_hsk79():
    """Generate HSK 7-9 prep guide content."""
    base = BASE / 'HSK备考/hsk79-prep'

    # Cover
    write_file(base / 'part0-exam-overview/01-hsk79-intro.md', """# HSK 7-9 备考完全指南
## 高等·大师篇 — Levels 7-9 Complete Prep Guide

> **2026年最新版 · 基于HSK 3.0官方考试大纲 · 一卷三试**

Published: 2026 | Author: Tony Sheng | Series: Z Turns Chinese

The definitive preparation guide for the new HSK 7-9 advanced exam.
Features the innovative "One Exam, Three Levels" (一卷三试) system with five skill areas:
Listening, Reading, Writing, Translation, and Speaking.
""")

    write_file(base / 'part0-exam-overview/02-five-skills.md', """# Five Skills — The Complete Exam

## What Changed?

Old HSK tested: Listening, Reading, Writing (3 skills)
New HSK 7-9 tests: **Listening, Reading, Writing, Translation, Speaking** (5 skills)

## Exam Structure

| Module | Duration | Task Types |
|--------|----------|-----------|
| Listening | ~30 min | Lectures, news, debates |
| Reading | ~45 min | Papers, literature, editorials |
| Writing | ~40 min | Academic, literary, practical |
| Translation | ~25 min | CN→EN, EN→CN |
| Speaking | ~15 min | Reading aloud, topic presentation, debate |

## Grading: "One Exam, Three Levels" (一卷三试)

All candidates take the SAME exam. Your score determines your level:

| Score Range | Level Achieved |
|-------------|---------------|
| 180-219 | Level 7 |
| 220-259 | Level 8 |
| 260-300 | Level 9 |

Total score: 300 points (each module contributes proportionally)
""")

    # Vocabulary/Grammar
    vocab_79 = vocab.get('7-9', [])[:50]
    write_file(base / 'part1-vocabulary-grammar/01-advanced-vocab-by-theme.md', f"""# Advanced Vocabulary — By Theme

## Sample Vocabulary (first 50 of ~5,600 new words)

{gen_vocab_table(vocab_79)}

## Theme Categories

1. **Academic** (学术) — research, methodology, hypothesis, conclusion
2. **Business** (商务) — strategy, merger, valuation, compliance
3. **Cultural** (文化) — allusion, metaphor, heritage, integration
4. **Technical** (技术) — algorithm, quantum, neural network
5. **Social** (社会) — governance, welfare, equity, sustainability
""")

    write_file(base / 'part1-vocabulary-grammar/02-professional-domains.md', """# Professional Domain Vocabulary

## Legal (法律)
| Chinese | Pinyin | English |
|---------|--------|---------|
| 诉讼 | sùsòng | litigation |
| 仲裁 | zhòngcái | arbitration |
| 合规 | héguī | compliance |
| 管辖 | guǎnxiá | jurisdiction |

## Medical (医学)
| Chinese | Pinyin | English |
|---------|--------|---------|
| 诊断 | zhěnduàn | diagnosis |
| 处方 | chǔfāng | prescription |
| 症状 | zhèngzhuàng | symptom |
| 治疗 | zhìliáo | treatment |

## Engineering (工程)
| Chinese | Pinyin | English |
|---------|--------|---------|
| 结构 | jiégòu | structure |
| 参数 | cānshù | parameter |
| 算法 | suànfǎ | algorithm |
| 优化 | yōuhuà | optimization |
""")

    write_file(base / 'part1-vocabulary-grammar/03-idioms-proverbs.md', """# Idioms, Proverbs & Fixed Expressions

## High-Frequency Chengyu (成语)

| Chengyu | Pinyin | Literal | Meaning |
|---------|--------|---------|---------|
| 一举两得 | yì jǔ liǎng dé | One action, two gains | Kill two birds with one stone |
| 画蛇添足 | huà shé tiān zú | Draw snake, add feet | Ruin by adding superfluous |
| 井底之蛙 | jǐng dǐ zhī wā | Well-bottom frog | Narrow-minded person |
| 守株待兔 | shǒu zhū dài tù | Guard stump, wait rabbit | Wait for luck instead of effort |
| 对牛弹琴 | duì niú tán qín | Play lute to cow | Talk to someone who can't understand |
| 亡羊补牢 | wáng yáng bǔ láo | Lose sheep, fix pen | Better late than never |
| 刻舟求剑 | kè zhōu qiú jiàn | Mark boat, seek sword | Rigid approach to changing situation |
| 掩耳盗铃 | yǎn ěr dào líng | Cover ears, steal bell | Self-deception |

## Common Proverbs (谚语)

| Chinese | Pinyin | English |
|---------|--------|---------|
| 活到老，学到老 | huó dào lǎo, xué dào lǎo | Live to old, learn to old — lifelong learning |
| 一寸光阴一寸金 | yí cùn guāngyīn yí cùn jīn | An inch of time, an inch of gold |
| 滴水穿石 | dī shuǐ chuān shí | Dripping water pierces stone — persistence pays off |
""")

    # Translation module
    write_file(base / 'part5-translation/01-cn-to-en.md', """# Translation Task 1 — Chinese to English

## Task Description
Translate Chinese passages into English. Tests your ability to:
- Understand complex Chinese structures
- Produce natural English equivalents
- Handle cultural and technical vocabulary

## Strategy
1. **Read the full passage first** — understand context
2. **Identify key structures** — relative clauses, conditionals, passive
3. **Translate meaning, not word-for-word**
4. **Check for natural English** — subject-verb agreement, articles, tense

## Practice

**Source:** "随着经济的发展，中国人的消费方式发生了很大变化。"
**Translation:** "With the development of the economy, Chinese people's consumption patterns have changed significantly."

**Source:** "中国自古以来就重视教育，认为教育是改变命运的重要途径。"
**Translation:** "Since ancient times, China has valued education, believing it to be an important pathway to change one's destiny."
""")

    write_file(base / 'part5-translation/02-en-to-cn.md', """# Translation Task 2 — English to Chinese

## Task Description
Translate English passages into Chinese. Tests your ability to:
- Understand complex English structures
- Produce natural Chinese equivalents
- Handle technical and academic vocabulary

## Strategy
1. **Understand the full meaning first**
2. **Restructure for Chinese** — SVO, topic-comment, time-place order
3. **Choose appropriate register** — formal for academic, natural for general
4. **Check Chinese fluency** — read it aloud to test

## Practice

**Source:** "The rapid advancement of artificial intelligence has raised important ethical questions about the future of work."
**Translation:** "人工智能的快速发展引发了关于未来工作的重要伦理问题。"

**Source:** "Climate change is one of the greatest challenges facing humanity in the 21st century."
**Translation:** "气候变化是21世纪人类面临的最大挑战之一。"
""")

    # Speaking module
    write_file(base / 'part6-speaking/01-reading-aloud-retelling.md', """# Speaking Task 1 — Reading Aloud & Retelling

## Task Description
1. Read a Chinese passage aloud (tests pronunciation, fluency, intonation)
2. Retell the main points in your own words

## Scoring Criteria
- Pronunciation accuracy (声母、韵母、声调)
- Fluency (speed, pauses, rhythm)
- Intonation (sentence stress, tone changes)
- Comprehension (accuracy of retelling)

## Strategy
1. **Read silently first** — understand before speaking
2. **Pace yourself** — not too fast, not too slow
3. **Clear articulation** — each syllable should be distinct
4. **Retell structure:** Main point → Supporting detail → Conclusion
""")

    write_file(base / 'part6-speaking/02-topic-presentation.md', """# Speaking Task 2 — Topic Presentation (3 minutes)

## Task Description
Given a topic, prepare and deliver a 3-minute presentation in Chinese.

## Common Topics
1. 人工智能对社会的影响 (AI's impact on society)
2. 中国传统文化的现代价值 (Modern value of traditional Chinese culture)
3. 全球化背景下的文化交流 (Cultural exchange in the context of globalization)
4. 环境保护与经济发展的平衡 (Balance between environmental protection and economic development)
5. 教育公平问题 (Educational equity issues)

## Strategy
1. **Structure:** Introduction → Point 1 → Point 2 → Conclusion
2. **Use connectors:** 首先, 其次, 再次, 最后, 综上所述
3. **Vary sentence types:** 陈述句, 疑问句, 感叹句
4. **Stay on topic** — 3 minutes goes fast

## Sample Opening
"各位考官好，今天我要讨论的话题是...我将从以下几个方面来展开..."
("Dear examiners, today I will discuss... I will expand from the following aspects...")
""")

    # Exam tips
    write_file(base / 'part7-exam-tips/01-translation-scoring.md', """# Translation Scoring & Strategy

## Scoring Rubric

| Score Range | Criteria |
|-------------|----------|
| 90-100% | Accurate, fluent, appropriate register |
| 70-89% | Mostly accurate, minor errors |
| 50-69% | Key meaning conveyed, some errors |
| Below 50% | Significant misunderstanding or poor expression |

## Key Strategies
1. Don't leave blanks — partial translation gets partial credit
2. Use context clues for unknown words
3. Keep sentences shorter in translation — reduces error risk
4. Double-check proper nouns (names, places, technical terms)
""")

    write_file(base / 'part7-exam-tips/02-speaking-scoring.md', """# Speaking Scoring & Strategy

## Scoring Rubric

| Dimension | Weight | What Examiners Look For |
|-----------|--------|------------------------|
| Pronunciation | 25% | Accurate initials, finals, tones |
| Fluency | 25% | Natural pace, appropriate pauses |
| Vocabulary | 20% | Appropriate word choice, range |
| Grammar | 15% | Correct structures, variety |
| Content | 15% | Relevance, depth, organization |

## Key Strategies
1. Speak clearly — examiners can't score what they can't hear
2. Use formal register — this is an exam, not casual conversation
3. Structure your response — intro → body → conclusion
4. Practice with a timer — 3 minutes is shorter than you think
""")

    write_file(base / 'part7-exam-tips/03-contemporary-china.md', """# Contemporary China Knowledge (必考背景)

## Must-Know Background Topics

### Economy
- GDP growth, dual circulation, common prosperity
- Belt and Road Initiative (一带一路)
- Digital economy, e-commerce, fintech

### Society
- Urbanization, hukou system, migrant workers
- Education reform, gaokao, double reduction policy
- Aging population, three-child policy

### Technology
- AI development (Baidu, Alibaba, Tencent)
- Space program (Tiangong, Chang'e, Mars)
- 5G, quantum computing, high-speed rail

### Culture
- Cultural confidence (文化自信)
- Intangible cultural heritage
- Soft power, cultural export

### Environment
- Carbon peak (2030), carbon neutrality (2060)
- Green development, ecological civilization
- Yangtze River protection, Yellow River strategy
""")

    # Mock exams
    for exam_num in range(1, 4):
        write_file(base / f'part8-mock-exams/mock-exam-{exam_num}.md', f"""# Full Mock Exam {exam_num} — HSK Levels 7-9

## Instructions
- **One exam, three levels** — your score determines 7/8/9
- Five modules: Listening, Reading, Writing, Translation, Speaking
- Total duration: ~180 minutes

---

## Module 1: Listening
- Academic lecture comprehension
- News and commentary
- Formal dialogue analysis

## Module 2: Reading
- Academic paper excerpts
- Literary passages
- Editorial analysis

## Module 3: Writing
- Academic summary (论文摘要)
- Opinion essay (议论文)

## Module 4: Translation
- Chinese to English passage
- English to Chinese passage

## Module 5: Speaking
- Read passage aloud
- 3-minute topic presentation
- Response to examiner questions

---

## Scoring Guide
- 180-219: Level 7
- 220-259: Level 8
- 260-300: Level 9
""")

    # Appendices
    vocab_all = vocab.get('7-9', [])
    if vocab_all:
        write_file(base / 'appendices/A-new-vocabulary.md', f"""# Appendix A: HSK 7-9 New Vocabulary

## Full Vocabulary Reference

{gen_vocab_appendix(vocab_all)}

**Note:** `Word (简体)` uses normalized simplified Chinese, and `English Meaning` is filled from the local glossary plus cached online fallback for uncovered items.
""")
    else:
        write_file(base / 'appendices/A-new-vocabulary.md', """# Appendix A: HSK 7-9 New Vocabulary (Sample)

## Academic & Professional Vocabulary

| Chinese | Pinyin | English | Domain |
|---------|--------|---------|--------|
| 范式 | fànshì | paradigm | Academic |
| 博弈 | bóyì | game theory | Academic |
| 赋能 | fùnéng | empower | Business |
| 迭代 | diédài | iterate | Tech |
| 耦合 | ǒuhé | coupling | Engineering |
| 溯源 | sùyuán | trace origin | Academic |
| 协同 | xiétóng | synergy | Business |

**Note:** The repository currently does not contain a full `hsk_vocab_7-9.json`, so this appendix stays as a curated sample until the source list is added.
""")

    write_file(base / 'appendices/C-idiom-handbook.md', """# Appendix C: Essential Idioms (300 Samples)

## Most Tested Chengyu for HSK 7-9

| # | Chengyu | Pinyin | Meaning |
|---|---------|--------|---------|
| 1 | 画蛇添足 | huà shé tiān zú | Superfluous action |
| 2 | 对牛弹琴 | duì niú tán qín | Waste effort |
| 3 | 亡羊补牢 | wáng yáng bǔ láo | Better late than never |
| 4 | 一举两得 | yì jǔ liǎng dé | Two birds one stone |
| 5 | 井底之蛙 | jǐng dǐ zhī wā | Narrow-minded |
| 6 | 杯水车薪 | bēi shuǐ chē xīn | Inadequate effort |
| 7 | 守株待兔 | shǒu zhū dài tù | Wait for luck |
| 8 | 掩耳盗铃 | yǎn ěr dào líng | Self-deception |
""")

    write_file(base / 'appendices/E-speaking-topics.md', """# Appendix E: 50 Speaking Topics

## High-Frequency Speaking Topics

1. 人工智能与未来生活 (AI and future life)
2. 中国传统文化的价值 (Value of traditional Chinese culture)
3. 全球化与文化多样性 (Globalization and cultural diversity)
4. 环境保护与可持续发展 (Environmental protection and sustainability)
5. 教育公平与素质教育 (Educational equity and quality education)
6. 城乡差距与乡村振兴 (Urban-rural gap and rural revitalization)
7. 老龄化社会的挑战 (Challenges of aging society)
8. 数字经济与就业变革 (Digital economy and employment change)
9. 跨文化交际中的误解 (Misunderstandings in cross-cultural communication)
10. 中国饮食文化的传播 (Spread of Chinese food culture)
11. 中国高铁对区域经济的影响 (High-speed rail's impact on regional economy)
12. 社交媒体的利与弊 (Pros and cons of social media)
13. 中医药的现代化 (Modernization of traditional Chinese medicine)
14. 中国航天事业的发展 (Development of China's space program)
15. 乡村振兴中的电商角色 (E-commerce's role in rural revitalization)
16-50: Additional topics in the full version
""")

    print(f"HSK 7-9: Generated {len(list(base.rglob('*.md')))} files")


# ============================================================
# MAIN
# ============================================================

print("=== HSK Prep Content Generator ===")
print(f"Loaded vocabulary: {sum(len(v) for v in vocab.values())} words across {len(vocab)} levels")

generate_hsk1()
for lv in [2, 3, 4, 5, 6]:
    generate_hsk_structure(lv)
generate_hsk79()

print("\n=== Generation Complete ===")
print("All 7 HSK prep guides created with markdown content.")
print("Run: python3 generate_hsk_pdf.py to generate PDFs.")
