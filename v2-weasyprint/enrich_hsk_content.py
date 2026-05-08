#!/usr/bin/env python3
"""Enrich HSK 2-79 prep guides with detailed content matching HSK 1 quality."""

import json, os
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # v2-weasyprint root

# Load vocabulary
vocab = {}
for lv in [1, 2, 3, 4, 5, 6]:
    fpath = BASE / f'hsk_vocab_{lv}.json'
    if fpath.exists():
        with open(fpath) as f:
            vocab[lv] = json.load(f)

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

def fl(chinese, pinyin, literal, english):
    return f"""```
Chinese: {chinese}
Pinyin: {pinyin}
Literal: {literal}
English: "{english}"
```"""

def gen_vocab_table(words):
    lines = ['| 词语 | 拼音 | 词性 | English Meaning |']
    lines.append('|------|------|------|----------------|')
    for w in words[:30]:
        lines.append(f"| {w['word']} | {w['pinyin']} | {w['pos']} | |")
    return '\n'.join(lines)


# ============================================================
# HSK 2 ENRICHMENT
# ============================================================
base = BASE / 'hsk2-prep'

# Exam overview - detailed
write_file(base / 'part0-exam-overview/03-prep-plan.md', """# HSK 2 Prep Plan — 8-Week Standard Schedule

## Weekly Breakdown

| Week | Focus | New Words | Activities |
|------|-------|-----------|------------|
| 1 | Weather & Shopping | 50 | Learn 天气/购物 vocabulary, practice 了 |
| 2 | Transportation & Hobbies | 50 | Learn 交通/爱好, practice 比 sentences |
| 3 | Work/Study & Health | 50 | Learn 工作/健康, practice 虽然...但是 |
| 4 | Review + Listening practice | — | Full listening practice, mock sections |
| 5 | Grammar deep-dive | 50 | All 了 usages, comparisons |
| 6 | Reading + Writing practice | 50 | Sentence construction, character writing |
| 7 | Full mock exams | — | 3 timed mock exams |
| 8 | Weak point review | — | Targeted review, final prep |

## Daily Practice (45 minutes)

**15 min Vocabulary:** Review 20 flashcards + learn 10 new
**15 min Listening:** Audio practice with official-style questions
**15 min Reading/Writing:** Sentence exercises, character practice

## Key Grammar for HSK 2

1. **了 (le)** — Completion/change of state (biggest grammar point)
2. **比 (bǐ)** — Comparison sentences: A 比 B + adj
3. **虽然...但是** — Although...but
4. **正在...呢** — Currently doing
5. **又...又** — Both...and
6. **一边...一边** — While doing...also doing

## Key Takeaways

- HSK 2 introduces 书写 (writing) — new module!
- 了 is the #1 grammar point to master
- 500 total words (300 from HSK 1 + 200 new)
- 60 questions total, ~60 minutes
""")

# Enrich vocabulary with four-layer examples
write_file(base / 'part1-vocabulary-grammar/01-weather-seasons.md', f"""# Weather & Seasons — 天气与季节

## Core Vocabulary

{gen_vocab_table(vocab.get(2, [])[:30])}

## Key Expressions

### Describing Weather

{fl('今天天气很好。', 'Jīntiān tiānqì hěn hǎo.', 'today weather very good.', 'The weather is very good today.')}

{fl('外面在下雨。', 'Wàimiàn zài xiàyǔ.', 'outside at rain.', 'It is raining outside.')}

{fl('今天很冷，刮风了。', 'Jīntiān hěn lěng, guāfēng le.', 'today very cold, blow-wind [change].', 'It is very cold today, and the wind is blowing.')}

### Temperature

{fl('今天多少度？', 'Jīntiān duōshao dù?', 'today how-many degree?', 'What is the temperature today?')}

{fl('零下五度。', 'Líng xià wǔ dù.', 'zero below five degree.', 'Minus five degrees.')}

### Seasons

{fl('我最喜欢春天。', 'Wǒ zuì xǐhuan chūntiān.', 'I most like spring.', 'I like spring the most.')}

{fl('夏天太热了。', 'Xiàtiān tài rè le.', 'summer too hot [change].', 'Summer is too hot.')}

## Practice

Match each weather description to the correct season:
1. 下雪了 (snowing) → 冬天 (winter)
2. 很热 (very hot) → 夏天 (summer)
3. 刮风 (windy) → 秋天 (autumn)
4. 暖和 (warm) → 春天 (spring)
""")

write_file(base / 'part1-vocabulary-grammar/02-shopping-prices.md', f"""# Shopping & Prices — 购物与价格

## Key Expressions

{fl('这个多少钱？', 'Zhège duōshao qián?', 'this how-much money?', 'How much is this?')}

{fl('太贵了，便宜一点吧。', 'Tài guì le, piányi yìdiǎn ba.', 'too expensive [change], cheap a-little [suggestion].', 'Too expensive, make it a bit cheaper please.')}

{fl('我要买这个。', 'Wǒ yào mǎi zhège.', 'I want buy this.', 'I want to buy this.')}

{fl('打折吗？', 'Dǎzhé ma?', 'discount [question]?', 'Is there a discount?')}

## Shopping Dialogue

{fl('A: 请问，这件衣服多少钱？', 'A: Qǐngwèn, zhè jiàn yīfu duōshao qián?', 'A: excuse-me, this classifier clothes how-much money?', 'A: Excuse me, how much is this piece of clothing?')}

{fl('B: 一百五十块。', 'B: Yì bǎi wǔshí kuài.', 'B: one hundred fifty yuan.', 'B: 150 yuan.')}

{fl('A: 太贵了，能不能便宜一点？', 'A: Tài guì le, néng bu néng piányi yìdiǎn?', 'A: too expensive [change], can-not-can cheap a-little?', 'A: Too expensive, can you make it a bit cheaper?')}

{fl('B: 好吧，一百块。', 'B: Hǎo ba, yì bǎi kuài.', 'B: OK [suggestion], one hundred yuan.', 'B: OK, 100 yuan.')}
""")

write_file(base / 'part1-vocabulary-grammar/07-new-grammar.md', f"""# HSK 2 New Grammar Points

## 1. 了 (le) — The Big One

### Usage A: Completed Action
{fl('我吃 了 早饭。', 'Wǒ chī le zǎofàn.', 'I eat [completed] breakfast.', 'I ate breakfast.')}

### Usage B: Change of State
{fl('下雨 了。', 'Xiàyǔ le.', 'rain [change].', 'It has started raining.')}

### Usage C: With 太...了 (too...)
{fl('这个 太 贵 了！', 'Zhège tài guì le!', 'this too expensive [change]!', 'This is too expensive!')}

### Usage D: With 已经 (already)
{fl('他 已经 走 了。', 'Tā yǐjīng zǒu le.', 'He already leave [completed].', 'He has already left.')}

### Usage E: 了...了 (change + completion)
{fl('他 来 了 三 天 了。', 'Tā lái le sān tiān le.', 'He come [completed] three day [ongoing].', 'He has been here for three days.')}

### Usage F: 要...了 (about to)
{fl('要 下雨 了。', 'Yào xiàyǔ le.', 'about-to rain [change].', 'It is about to rain.')}

## 2. 比 (bǐ) — Comparison

{fl('他 比 我 高。', 'Tā bǐ wǒ gāo.', 'He compare me tall.', 'He is taller than me.')}

{fl('今天 比 昨天 冷。', 'Jīntiān bǐ zuótiān lěng.', 'today compare yesterday cold.', 'Today is colder than yesterday.')}

{fl('这个 比 那个 好。', 'Zhège bǐ nàge hǎo.', 'this compare that good.', 'This one is better than that one.')}

## 3. 虽然...但是 (Although...but)

{fl('虽然 下雨，但是 我 还是 去 了。', 'Suīrán xiàyǔ, dànshì wǒ háishì qù le.', 'Although rain, but I still go [completed].', 'Although it was raining, I still went.')}

## 4. 正在...呢 (Currently doing)

{fl('他 正在 学习 呢。', 'Tā zhèngzài xuéxí ne.', 'He currently studying [progressive].', 'He is studying right now.')}

## Key Takeaways

- 了 has SIX distinct usages at HSK 2 — master all of them
- 比 sentences: subject + 比 + object + adjective
- 虽然 and 但是 go together (unlike English, Chinese uses both)
- 正在...呢 = in the middle of doing something
""")

# Enrich HSK 2 listening section
write_file(base / 'part2-listening/04-listening-mock.md', f"""# Listening Mock Practice — HSK 2 Full Set

## Practice Listening Test (25 questions)

### Part 1 (Questions 1-5): Picture Sentence
1. You hear: "我喜欢踢足球。" → sports scene
2. You hear: "她买了一件新衣服。" → shopping scene
3. You hear: "今天真冷啊。" → cold weather scene
4. You hear: "请给我一杯水。" → drinking water scene
5. You hear: "他在打电话。" → phone scene

### Part 2 (Questions 6-15): Dialogue to Picture
6. M: "你喜欢什么运动？" W: "我最喜欢游泳。" → swimming
7. M: "你吃药了吗？" W: "还没有。" → medicine
8. M: "这个多少钱？" W: "八十块。" → shopping
9. M: "明天去公园好吗？" W: "好的。" → park
10. M: "你身体怎么样？" W: "很好，谢谢。" → health check

### Part 3 (Questions 16-25): Dialogue Q&A
16. M: "你每天几点起床？" W: "七点。" → Question: 她几点起床？
17. M: "你周末做什么？" W: "我去看电影。" → Question: 他周末做什么？
18. W: "你要喝茶还是喝咖啡？" M: "喝茶吧。" → Question: 男的喝什么？
19. M: "你的工作是什么？" W: "我是医生。" → Question: 女的是做什么的？
20. W: "这个周末我们去爬山吧。" M: "好的。" → Question: 他们周末做什么？

## Answer Key
16-七点, 17-看电影, 18-茶, 19-医生, 20-爬山
""")

# Enrich HSK 2 writing section
write_file(base / 'part4-writing/01-task1-picture-sentence.md', f"""# Writing Task 1 — Picture to Sentence (Questions 51-55)

## Task Format
Look at 5 pictures (A-E) and a word bank (F). Write a sentence for each picture using the given words.

## Strategy
1. **Look at the picture** — understand the scene
2. **Identify the action** — what is happening?
3. **Use simple SVO structure** — Subject + Verb + Object
4. **Add time/place if relevant**

## Examples

**Picture:** A person eating rice at a table.
{fl('他在吃饭。', 'Tā zài chī fàn.', 'He at eat rice.', 'He is eating.')}

**Picture:** A person going to school.
{fl('她去上学。', 'Tā qù shàngxué.', 'She go attend-school.', 'She is going to school.')}

**Picture:** Rain falling outside a window.
{fl('外面下雨了。', 'Wàimiàn xiàyǔ le.', 'Outside rain [change].', 'It is raining outside.')}

## Practice Prompts
1. Picture of someone drinking water → 喝水
2. Picture of someone at a hospital → 看病
3. Picture of someone shopping → 买东西
4. Picture of someone studying → 学习
5. Picture of a sunny day → 晴天
""")

print("HSK 2 enrichment complete")


# ============================================================
# HSK 3 ENRICHMENT
# ============================================================
base = BASE / 'hsk3-prep'

write_file(base / 'part1-vocabulary-grammar/08-core-grammar.md', f"""# HSK 3 Core Grammar — The Complement System

## Result Complement (结果补语)

{fl('我吃 完 了 饭。', 'Wǒ chī wán le fàn.', 'I eat finish [completed] rice.', 'I finished eating.')}

{fl('他听 懂 了 老师 的 话。', 'Tā tīng dǒng le lǎoshī de huà.', 'He listen understand [completed] teacher [possessive] words.', 'He understood what the teacher said.')}

Common result complements:
- 完 (finish): 做完 (finish doing), 看完 (finish reading)
- 懂 (understand): 听懂 (understand by listening)
- 见 (see): 看见 (see), 听见 (hear)
- 到 (arrive/reach): 找到 (find), 拿到 (get)

## Direction Complement (趋向补语)

{fl('他 走 进来 了。', 'Tā zǒu jìnlái le.', 'He walk enter-come [completed].', 'He walked in.')}

{fl('请 拿 出来。', 'Qǐng ná chūlái.', 'Please take out-come.', 'Please take it out.')}

## Potential Complement (可能补语)

{fl('我 看 不 清 这个字。', 'Wǒ kàn bu qīng zhège zì.', 'I look not-clear this classifier character.', 'I can\'t see this character clearly.')}

{fl('他 吃 得 完 吗？', 'Tā chī de wán ma?', 'He eat can-finish [question]?', 'Can he finish eating?')}

## Passive: 被 (bèi)

{fl('杯子 被 打 破 了。', 'Bēizi bèi dǎ pò le.', 'Cup by hit break [completed].', 'The cup was broken.')}

## Complex Sentences

### 因为...所以 (because...therefore)
{fl('因为 下雨，所以 我 不 去 了。', 'Yīnwèi xiàyǔ, suǒyǐ wǒ bú qù le.', 'Because rain, therefore I not go [completed].', 'Because it is raining, I am not going.')}

### 不但...而且 (not only...but also)
{fl('他 不但 聪明，而且 很 努力。', 'Tā búdàn cōngmíng, érqiě hěn nǔlì.', 'He not-only smart, but-also very hardworking.', 'He is not only smart but also very hardworking.')}

### 如果...就 (if...then)
{fl('如果 下雨，我 就 不 去 了。', 'Rúguǒ xiàyǔ, wǒ jiù bú qù le.', 'If rain, I then not go [completed].', 'If it rains, I won\'t go.')}
""")

print("HSK 3 enrichment complete")


# ============================================================
# HSK 4 ENRICHMENT
# ============================================================
base = BASE / 'hsk4-prep'

write_file(base / 'part1-vocabulary-grammar/07-core-grammar.md', f"""# HSK 4 Core Grammar

## 把 (bǎ) Sentences — Object Disposal

Structure: Subject + 把 + Object + Verb + Result/Direction

{fl('请 把 书 给 我。', 'Qǐng bǎ shū gěi wǒ.', 'Please take book give me.', 'Please give me the book.')}

{fl('他 把 房间 打扫 干净 了。', 'Tā bǎ fángjiān dǎsǎo gānjìng le.', 'He take room clean clean [completed].', 'He cleaned the room.')}

{fl('你 把 这个 消息 告诉 他 了 吗？', 'Nǐ bǎ zhège xiāoxi gàosu tā le ma?', 'You take this news tell him [completed] [question]?', 'Did you tell him this news?')}

## 被 (bèi) Sentences — Passive

{fl('书 被 他 拿走 了。', 'Shū bèi tā ná zǒu le.', 'Book by he take away [completed].', 'The book was taken away by him.')}

{fl('窗户 被 风吹 开 了。', 'Chuānghu bèi fēng chuī kāi le.', 'Window by wind blow open [completed].', 'The window was blown open by the wind.')}

## 兼语句 (Pivotal Sentences)

{fl('老师 让 我们 做 作业。', 'Lǎoshī ràng wǒmen zuò zuòyè.', 'Teacher let us do homework.', 'The teacher asked us to do homework.')}

{fl('他 请 我 吃 饭。', 'Tā qǐng wǒ chī fàn.', 'He invite me eat rice.', 'He invited me to eat.')}

## Emphasis: 是...的

{fl('我 是 昨天 来 的。', 'Wǒ shì zuótiān lái de.', 'I [emphatic] yesterday come [marker].', 'It was yesterday that I came.')}

{fl('他 是 坐 飞机 去 的。', 'Tā shì zuò fēijī qù de.', 'He [emphatic] sit airplane go [marker].', 'He went by airplane.')}
""")

print("HSK 4 enrichment complete")


# ============================================================
# HSK 5 ENRICHMENT
# ============================================================
base = BASE / 'hsk5-prep'

write_file(base / 'part1-vocabulary-grammar/07-core-grammar.md', f"""# HSK 5 Core Grammar — Advanced Structures

## Formal Written Structures

### 鉴于 (jiànyú) — In view of
{fl('鉴于 以上 原因，我们 决定 推迟 会议。', 'Jiànyú yǐshàng yuányīn, wǒmen juédìng tuīchí huìyì.', 'In-view-of above reasons, we decide postpone meeting.', 'In view of the above reasons, we decided to postpone the meeting.')}

### 与其...不如 (rather than...it would be better)
{fl('与其 抱怨，不如 行动。', 'Yǔqí bàoyuàn, bùrú xíngdòng.', 'Rather-than complain, better act.', 'Rather than complain, it would be better to act.')}

### 无论...都 (no matter...all)
{fl('无论 什么 困难，我们 都 能 解决。', 'Wúlùn shénme kùnnán, wǒmen dōu néng jiějué.', 'No-matter what difficulty, we all can solve.', 'No matter what difficulties, we can solve them all.')}

### 不仅...反而 (not only...on the contrary)
{fl('他 不仅 没生气，反而 笑 了 起来。', "Tā bùjǐn méi shēngqì, fǎn'ér xiào le qǐlái.", 'He not-only not angry, on-the-contrary laugh [completed] up.', 'Not only was he not angry, on the contrary he started laughing.')}
""")

print("HSK 5 enrichment complete")


# ============================================================
# HSK 6 ENRICHMENT
# ============================================================
base = BASE / 'hsk6-prep'

write_file(base / 'part1-vocabulary-grammar/05-advanced-grammar.md', f"""# HSK 6 Advanced Grammar — Discourse & Rhetoric

## Advanced Discourse Connectors

### 诚然...然而 (admittedly...however)
{fl('诚然 困难 很多，然而 并非 不可 克服。', "Chéngrán kùnnán hěn duō, rán'ér bìng fēi bùkě kèfú.", 'Admittedly difficulties very many, however certainly not cannot overcome.', 'Admittedly there are many difficulties, however they are not insurmountable.')}

### 固然...但是 (admittedly...but)
{fl('这个 方案 固然 有 优点，但是 也 存在 问题。', "Zhège fāng'àn gùrán yǒu yōudiǎn, dànshì yě cúnzài wèntí.", 'This plan admittedly have advantages, but also exist problems.', 'This plan admittedly has advantages, but also has problems.')}

## Nested Structures

{fl('虽然 他 说 的 那番 话，听起来 似乎 有 道理，然而 仔细 分析，却 经 不 起 推敲。', "Suīrán tā shuō de nàfān huà, tīng qǐlái sìhu yǒu dàolǐ, rán'ér zǐxǐ fēnxī, què jīng bu qǐ tuīqiāo.", 'Although he said [possessive] those words, listen up seemingly have reason, however carefully analyze, yet withstand not careful consideration.', 'Although what he said sounds reasonable, upon careful analysis, it does not withstand scrutiny.')}
""")

print("HSK 6 enrichment complete")


# ============================================================
# HSK 7-9 ENRICHMENT
# ============================================================
base = BASE / 'hsk79-prep'

# One exam three levels detail
write_file(base / 'part0-exam-overview/05-one-exam-three-levels.md', """# One Exam, Three Levels (一卷三试) — Detailed Guide

## How It Works

All candidates take the **same exam paper**. Your total score determines which level you achieve:

| Score Range | Level | CEFR Equivalent |
|-------------|-------|-----------------|
| 180-219 | 七级 | C1 |
| 220-259 | 八级 | C1+ |
| 260-300 | 九级 | C2 |

## Why This System?

- **Flexibility**: One registration, three possible outcomes
- **Accuracy**: Your actual level is determined by performance, not self-selection
- **Motivation**: Candidates aim higher knowing they can still achieve a lower level

## Module Weighting

| Module | Weight | Key Skills Tested |
|--------|--------|-------------------|
| Listening | 20% | Academic comprehension, inference |
| Reading | 25% | Critical analysis, literary appreciation |
| Writing | 25% | Academic writing, argumentation |
| Translation | 15% | Cross-lingual competence, cultural awareness |
| Speaking | 15% | Oral fluency, structured expression |

## Level-Specific Expectations

### Level 7 (180-219)
- Understand main ideas in academic contexts
- Write clear essays on familiar topics
- Translate straightforward passages
- Speak with reasonable fluency

### Level 8 (220-259)
- Analyze complex texts and arguments
- Write well-structured academic papers
- Translate nuanced passages accurately
- Speak with confidence on diverse topics

### Level 9 (260-300)
- Engage critically with advanced scholarship
- Write publishable-quality academic Chinese
- Translate literary and technical texts
- Deliver sophisticated oral presentations
""")

# More translation practice
write_file(base / 'part5-translation/03-translation-practice.md', f"""# Translation Practice — Mixed Exercises

## CN → EN Practice

{fl('近年来，随着互联网技术的飞速发展，中国的电子商务行业取得了长足的进步。', 'Jìnniánlái, suízhe hùliánwǎng jìshù de fēisù fāzhǎn, Zhōngguó de diànzǐ shāngwù hángyè qǔdé le chángzú de jìnbù.', 'In-recent-years, along-with internet technology [possess] rapid development, China [possess] e-commerce industry achieved significant progress.', 'In recent years, with the rapid development of Internet technology, China\'s e-commerce industry has made remarkable progress.')}

{fl('中国政府高度重视环境保护，提出了一系列绿色发展理念和政策措施。', "Zhōngguó zhèngfǔ gāodù zhòngshì huánjìng bǎohù, tíchū le yíxìliè lǜsè fāzhǎn lǐniàn hé zhèngcè cuòshī.", 'China government highly-value environmental protection, proposed [completed] series green development concept and policy measures.', 'The Chinese government attaches great importance to environmental protection and has proposed a series of green development concepts and policy measures.')}

## EN → CN Practice

**Source:** "The integration of traditional Chinese medicine with modern medical technology represents a unique approach to healthcare innovation."

**Translation:** "中医药与现代医疗技术的结合代表了医疗保健创新的独特方法。"

**Source:** "Belt and Road Initiative has promoted economic cooperation and cultural exchange among participating countries."

**Translation:** "一带一路倡议促进了参与国之间的经济合作和文化交流。"
""")

print("HSK 7-9 enrichment complete")

print("\n=== All Enrichments Complete ===")
