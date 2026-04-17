在大语言模型（如 Claude 3.5 Sonnet 或 GPT-4o）的应用中，Prompt 不是简单的几句话，而是**软件工程中的“编译指令”**。为了确保系统能稳定、连续地输出符合“四行对照”、“HSK分级”和“真实中国”要求的高质量结构化数据（以便无缝对接 Typst 生成 PDF），我们需要采用**结构化与模块化的 Prompt 链设计 (Chain of Prompts)**。

以下是 LingoFlow 核心引擎的 Prompt 架构技术文档。

---

# LingoFlow Prompt 架构设计文档 v3.0

## 1. 提示词系统整体架构 (Prompt System Architecture)

为了保证极高的输出稳定性，我们不采用单一的庞大提示词，而是使用 **XML 标签结构化** 的系统级 Prompt。这种架构对顶级 LLM 的指令遵循（Instruction Following）效果最好。

完整的 Prompt 包含以下五个核心模块：
1.  **`<Role>` (角色设定)**：定义 AI 的身份、语气和核心教育理念（如你的字对字直译法）。
2.  **`<Context>` (动态上下文)**：通过代码动态注入 MCP 抓取的笔记、当前 HSK 级别、历史词汇表。
3.  **`<Constraints>` (绝对约束)**：强制执行数据脱敏、词汇超纲限制、输出格式限制。
4.  **`<Task>` (具体任务)**：课文重构、生词提取、真实中国练习生成。
5.  **`<Output_Format>` (输出规范)**：定义严格的 JSON Schema，确保后端能直接解析并喂给排版引擎。

---

## 2. 核心 System Prompt 模板 (The Master Prompt)

在实际的 Python/Node.js 后端中，这个模板会配合变量动态生成。以下是核心 Prompt 的完整设计：

```xml
<Role>
你是一位顶级的国际中文教育专家（Tony的数字分身）。你擅长为零基础或初级外国企业高管（如世界银行、埃克森美孚的高管）编写极具实用性的中文教材。
你的核心教学法是“母语逻辑映射（Literal Translation）”，通过中式英语直译帮助学生解构中文语序。你不仅教授语言，更注重融入2026年真实的中国现代生活场景。
</Role>

<Constraints>
1. 【隐私脱敏】绝对禁止在输出中包含输入文本里的真实人名、公司名、家庭住址等PII信息。统一替换为化名（如：David, Mary, 某公司）。
2. 【词汇控制】严格遵循 HSK 3.0 大纲。非目标级别的词汇必须降级替换，或作为“文化扩展词”单独列出。
3. 【字对字直译】每个中文字/词必须精确对应一个英文单词或短语，保持中文的原始语序。
4. 【输出格式】必须严格输出为指定的 JSON 格式，不要包含任何额外的 Markdown 代码块外的解释文字。
</Constraints>

<Context>
- 目标受众：外企高管，零基础/初级
- 当前教学目标等级：HSK {target_hsk_level}
- 本系列已学历史词汇（需间隔重复，尽量在对话中自然复用）：{historical_vocab_list}
- MCP 提取的今日上课原始笔记/录音文本：
{mcp_raw_notes}
</Context>

<Task>
请基于 <Context> 中的原始笔记，提取核心教学话题，重构为一篇高质量的中文教学课时（Lesson）。
包含以下三个部分：
1. 场景对话 (Dialogue)：一段符合真实商业/生活场景的对话（6-8个回合）。
2. 核心生词 (Vocabulary)：提取不超过 15 个生词。
3. 真实中国练习 (Real China Practice)：结合“{target_scenario}”（如：微信支付/滴滴打车）生成 3 道情景互动选择题。
</Task>

<Output_Format>
必须输出为合法的 JSON 格式，Schema 如下：
{
  "lesson_title": "英文课程标题",
  "topic_zh": "中文主题",
  "dialogue": [
    {
      "speaker": "角色名",
      "zh": "中文字符",
      "pinyin": "拼音(带声调)",
      "literal_en": "字对字直译(严格按照中文语序)",
      "natural_en": "地道的英文翻译"
    }
  ],
  "vocabulary": [
    {
      "word": "中文",
      "pinyin": "拼音",
      "pos": "词性",
      "meaning": "英文释义",
      "hsk_level": "HSK等级"
    }
  ],
  "real_china_exercises": [
    {
      "context": "英文情境描述 (e.g., You are in a Didi...)",
      "question": "英文问题",
      "options": [
        {"id": "A", "zh": "中文选项", "pinyin": "拼音", "literal_en": "直译"}
      ],
      "correct_answer": "A/B/C",
      "explanation": "英文解析，解释为什么这个选项在真实中国场景中最地道"
    }
  ]
}
</Output_Format>
```

---

## 3. 数学与逻辑控制模型 (Logic Control Variables)

为了实现你要求的“按HSK级别进行递进”和“新旧知识衔接”，我们必须在将数据喂给 Prompt 之前，在后端执行严格的数学与逻辑控制。

定义词汇控制公式：
$$ V_{\text{lesson}} = \text{本节课使用的所有独特词汇集合} $$
$$ V_{\text{HSK\_target}} = \text{当前HSK级别的标准词库} $$
$$ V_{\text{history}} = \text{该学员/系列以往学过的词汇数据库} $$

我们的系统在每次生成时，必须满足以下逻辑约束：
$$ V_{\text{lesson}} \subseteq (V_{\text{HSK\_target}} \cup V_{\text{history}} \cup V_{\text{new\_cultural}}) $$
并且，每节课的新生词数量必须受到严格限制（防止认知过载）：
$$ |V_{\text{lesson}} \setminus V_{\text{history}}| \le 15 $$

**执行逻辑分析：**
在后端 Python 代码中，当 LLM 返回 JSON 后，系统需要加一道**拦截校验（Validation Layer）**：
1. 提取 JSON 中 `dialogue` 所有的中文字词。
2. 与 PostgreSQL 数据库中的 HSK 3.0 大纲和用户的 $V_{\text{history}}$ 进行比对。
3. 如果发现大模型“幻觉”使用了高级别且未标注的复杂词汇（例如在 HSK 1 的课文中使用了“相提并论”），系统触发 **Auto-Correction Prompt**（自动纠错提示词），让 LLM 重新修改该句子。

---

## 4. 关键难点：字对字直译 (Literal Translation) 的精准度优化

**现状与痛点：**
大模型默认的翻译逻辑是“信达雅”，它会本能地把“你叫什么名字”翻译成“What is your name”。要强迫它输出“You call what name”是非常反直觉的，容易出现映射错位。

**解决方案与建议 (Few-Shot Prompting)：**
在 System Prompt 中，除了规则约束，必须加入**Few-Shot（少样本）示例**，手把手教它怎么切分。建议在 `<Constraints>` 模块后追加一个 `<Examples>` 标签：

```xml
<Examples>
  <Example 1>
    输入中文: "我明天去北京出差。"
    标准输出:
    zh: "我 明天 去 北京 出差。"
    pinyin: "Wǒ míngtiān qù Běijīng chūchāi."
    literal_en: "I tomorrow go Beijing business trip."
    natural_en: "I am going on a business trip to Beijing tomorrow."
  </Example 1>
  <Example 2>
    输入中文: "微信扫码支付。"
    标准输出:
    zh: "微信 扫 码 支付。"
    pinyin: "Wēixìn sǎo mǎ zhīfù."
    literal_en: "WeChat scan code pay."
    natural_en: "Pay by scanning the WeChat QR code."
  </Example 2>
</Examples>
```

---

## 5. 输出到 Typst 的数据流转 (Pipeline to Typst)

当大模型稳定输出上述 JSON 后，下一步是排版。由于你主打精品 PDF，强烈建议在系统中集成 Typst。

**数据流转路径：**
1. AI 生成结构化 JSON。
2. 后端使用 Python 的 Jinja2 模板引擎，将 JSON 数据注入到 `.typ` (Typst源文件) 中。
3. 调用 Typst CLI 编译：`typst compile lesson_04.typ lesson_04.pdf`

**Typst 模板代码概念展示 (直译排版的高效实现)：**
Typst 可以非常优雅地处理多行对齐问题。

```typst
#let literal_block(zh, py, lit, nat) = [
  #block(
    fill: luma(240),
    inset: 10pt,
    radius: 4pt,
    [
      #text(size: 16pt, weight: "bold", zh) \
      #text(size: 10pt, fill: rgb("555555"), py) \
      #text(size: 11pt, fill: rgb("0055cc"), lit) \
      #line(length: 100%, stroke: 0.5pt + silver)
      #text(size: 12pt, style: "italic", nat)
    ]
  )
]

// 之后可以直接通过 JSON 循环调用这个组件生成对话
```

## 6. 下一步行动讨论 (Action Items)

通过这套核心 Prompt 架构和数学控制逻辑，LingoFlow 的“大脑”就已经成型了。

接下来，我们需要确认实施层面的细节：
1. **测试意愿**：你是否愿意使用现成的一段“Get笔记”录音文本，我们直接手动模拟跑一次这个 Prompt，看看 Claude 3.5 Sonnet 生成的 JSON 质量是否达到你的教学标准？（你可以把一小段笔记贴在这里，我来运行演示）。
2. **场景库构建**：对于“真实中国练习”，我们需要预先定义几十个场景标签（如：外卖、网约车、高铁、饭局敬酒等）。你目前有哪些最常给高管讲的真实痛点场景？我们可以先列一个 Top 10 列表。
