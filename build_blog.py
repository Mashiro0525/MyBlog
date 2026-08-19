# -*- coding: utf-8 -*-
"""生成「五彩湾 UE 开发知识库」博客式静态站点（纯静态预渲染版 · 学霸笔记风）。

设计原则（不依赖 JavaScript 即可浏览）：
  1. 所有内容（6 主题 → 24 子主题 → 364 卡片）直接写成 HTML <details> 折叠树。
  2. 答案按步骤分段：数字步骤(1. 标题) → 步骤块(序号徽标+标题+正文)，
     行首角色标签(操作/观察/原因/结论/检查项/排查/验证/注意…) → 彩色小标签；
     无步骤的答案按空行分段。
  3. 关键词荧光：生成时把术语/节点/报错码(code:51/220001)/坐标(EPSG:4539)等
     包进 <mark class="kw">（按主题统一荧光色），报错码用 <mark class="err"> 红色提亮。
  4. 四套可切换配色（学霸荧光默认/薄荷清新/黄昏暖读/深空夜读）：CSS 变量 + radio-hack，
     纯 CSS 切换，无需 JS。

输入: pkm_cards_v2/{主题}/{子主题}.md （单文件多卡片：## N. 标题 + **问题：**/**答案：**）
输出: pkm_blog/index.html （单文件，双击即开，无外部依赖）
"""

import html
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'pkm_cards_v2')
OUT = os.path.join(BASE, 'pkm_blog')

# 原始对话数据源（卡片定位上下文用）
CONV_JSON = os.path.join(BASE, 'conversation_01KS260F0A23NMC7A3ZXGXDY4W_2026-08-17T02-51-15.json')
CONV_MD = os.path.join(BASE, 'conversation.md')
CTX_WINDOW = 3   # 对话上下文：定位消息前后各展开 N 条（JS 增强）

TOPIC_META = {
    '蓝图交互': '蓝图逻辑与交互：属性查询、射线点击、UI 控件、场景漫游、动画天气、专题图层',
    'GIS坐标': 'GIS 与坐标：三维数据导入、GeoServer 图层、WFS/HTTP 查询、坐标转换',
    'Cpp工程': 'UE C++ 工程：AirSim 源码编译、常规编译报错、C++ 类设计',
    'AirSim无人机': 'AirSim 无人机：插件安装部署、崩溃排查、飞行操控',
    'Echarts媒体': '图表与媒体：ECharts 图表、WebBrowser 集成、视频与 GIF',
    '项目配置': '项目配置：工程备份迁移、运行环境',
}
# 主题顺序固定 -> 主题色类 t0..t5
TOPIC_ORDER = list(TOPIC_META.keys())

SUB_ICON = {
    '属性查询系统': '🗂️', '射线检测与点击': '🎯', 'UI与控件': '🎨', '场景漫游': '🚶',
    '动画与天气': '🌤️', '鸟瞰专题图层': '🛰️', 'GameMode与关卡': '🎮',
    '蓝图与C++协作': '🔗', '视频播放': '🎬',
    '三维数据导入': '📦', 'GeoServer图层': '🗺️', 'HTTP与WFS查询': '🌐', '坐标转换': '🧭',
    'AirSim源码编译': '🔧', '常规编译报错': '⚠️', 'C++类设计': '🧩',
    '插件安装部署': '📥', '崩溃与报错排查': '💥', '操控与使用': '🕹️',
    'ECharts图表制作': '📊', 'WebBrowser集成': '🌍', '视频与GIF': '🎞️',
    '备份与迁移': '💾', '环境与运行': '⚙️',
}

# ---------------- 关键词荧光（静态写入，生成阶段完成） ----------------

# 报错码/坐标等"模式型"关键词 -> 红色荧光 <mark class="err">
KW_PATTERNS_ERR = [
    re.compile(r'EPSG\s*[:：]?\s*\d+', re.I),
    re.compile(r'code\s*[:：]\s*\d+', re.I),
    re.compile(r'0x[0-9A-Fa-f]{3,}'),
    re.compile(r'\b(?:error|warning)\s*(?:C|LNK|MSB)?\s*\d{3,}', re.I),
]

# 词表型关键词 -> 主题荧光 <mark class="kw">（按主题单色）
KW_GLOBAL = [
    'Unreal Engine', 'UE5', '静态网格体', '射线检测', '碰撞通道', '数据表',
    'Row Name', 'Draw Debug Type', 'Line Trace', 'Print String', 'Add to Viewport',
    'BeginPlay', 'Create Widget', 'Forward Vector', 'Get World Location',
    'Input Action', 'Auto Receive Input', 'Visibility', 'BlockAll', 'NoCollision',
    'Collision Presets', 'Trace Responses', 'Z-Order', 'GameMode', 'Pawn',
    'Character', 'Widget', 'Component', 'Actor', 'Details', 'Collision',
    'WGS84', 'CGCS2000', 'GeoServer', 'WFS', 'WMS', 'WMTS', 'GeoJSON',
    'Shapefile', 'DEM', 'OSGB', 'FPS',
]

KW_TOPIC = {
    '蓝图交互': [
        'Get Data Table Row', 'Row Found', 'Line Trace By Channel', 'For Duration',
        'One Frame', 'Component Tags', 'Actor Tags', 'Left Mouse Button',
        'Cast To', 'Event Tick', 'Event BeginPlay', 'User Widget', 'Canvas Panel',
        'Overlay', 'Viewport', 'Screen Space', 'Hit Result', 'Impact Point',
        'Get Hit Result', 'Data Table', 'Branches',
    ],
    'GIS坐标': [
        '经纬度', '投影坐标', '地理坐标系', '投影坐标系', '火星坐标', 'GCJ-02',
        'WGS-84', 'Web Mercator', '球心坐标', '平面坐标', '坐标系', '瓦片', '图层',
    ],
    'Cpp工程': [
        'CMake', 'Visual Studio', 'MSVC', 'Build.bat', 'C++', '头文件', '编译',
        '链接', '链接器', 'Include', 'Lib', 'DLL', '静态库', '动态库', '定义宏',
    ],
    'AirSim无人机': [
        'settings.json', 'SimMode', 'MavLink', 'RPC', 'HomeGeoPoint',
        'OriginGeopoint', '起飞', '降落', '悬停', '遥控', '手动模式', 'API',
    ],
    'Echarts媒体': [
        'ECharts', 'option', 'series', 'xAxis', 'yAxis', 'tooltip', 'legend',
        'WebBrowser', 'HTML5', 'Canvas', 'SVG', 'GIF', 'MP4', '自动播放', '循环',
    ],
    '项目配置': [
        '.uproject', '.ini', 'DefaultEngine.ini', 'DefaultGame.ini', '环境变量',
        '启动参数', '备份', '迁移', 'Git', '引擎版本', '插件目录',
    ],
}


def kw_mark(text, topic):
    """在纯文本上把关键词替换为占位符。返回 (带占位符文本, kw列表, err列表)。"""
    kbuf, ebuf = [], []

    def _mk(buf, ph):
        def _r(m):
            buf.append(m.group(0))
            return ph.format(len(buf) - 1)
        return _r

    for pat in KW_PATTERNS_ERR:
        text = pat.sub(_mk(ebuf, '\x00E{}\x00'), text)
    terms = list(KW_GLOBAL) + list(KW_TOPIC.get(topic, []))
    for t in sorted(set(terms), key=len, reverse=True):
        if not t:
            continue
        if re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:/+\-]*', t):
            # 全 ASCII 词加边界，避免 Pawn 误命中 Spawn 等子串；中文后缀(FPS模式)不受影响
            pat = r'(?<![A-Za-z0-9_])' + re.escape(t) + r'(?![A-Za-z0-9_])'
        else:
            pat = re.escape(t)
        text = re.sub(pat, _mk(kbuf, '\x00K{}\x00'), text, flags=re.IGNORECASE)
    return text, kbuf, ebuf


def kw_restore(h, kbuf, ebuf):
    def _r(m):
        return '<mark class="err">' + html.escape(ebuf[int(m.group(1))]) + '</mark>'
    h = re.sub(r'\x00E(\d+)\x00', _r, h)

    def _r2(m):
        return '<mark class="kw">' + html.escape(kbuf[int(m.group(1))]) + '</mark>'
    return re.sub(r'\x00K(\d+)\x00', _r2, h)


# ---------------- 标签导航（右侧栏，纯 CSS :has 筛选 + JS 渐进增强） ----------------

# 聚合型报错标签：不一一列举每个报错码，而是按"类别"聚合，方便快速定位同类问题
ERR_TAGS = [
    ('err-epsg', 'EPSG:*'),
    ('err-code', 'code:*'),
    ('err-hex', '0x*'),
    ('err-msg', 'error/warning C*'),
]
ERR_PATTERNS = [
    ('err-epsg', re.compile(r'EPSG\s*[:：]?\s*\d+', re.I)),
    ('err-code', re.compile(r'code\s*[:：]\s*\d+', re.I)),
    ('err-hex', re.compile(r'0x[0-9A-Fa-f]{3,}')),
    ('err-msg', re.compile(r'\b(?:error|warning)\s*(?:C|LNK|MSB)?\s*\d{3,}', re.I)),
]

# 报错模式标签固定在最前，其余标签在界面按组排列
GLOBAL_TAG_N = 15      # 全局热门标签个数
TOPIC_TAG_N = 6        # 每主题标签个数

# 标签"文本贡献占比"：问题命中的标签权重高（优先），答案命中的标签权重低（兜底）。
# 调整 Q_WEIGHT / A_WEIGHT 即调整两者占比，仅影响标签排序与计数，不影响筛选覆盖。
Q_WEIGHT = 3           # 问题命中权重（默认 3）
A_WEIGHT = 1           # 答案命中权重（默认 1）


def slugify(s):
    """把关键词转成可作 CSS 类/属性值的 slug（保留中文，空白与符号转连字符）。"""
    s = s.lower().strip()
    s = re.sub(r'[\s_/\\+.:]+', '-', s)
    s = re.sub(r'[^a-z0-9\u4e00-\u9fff-]', '', s)
    return s.strip('-')


def compute_tags(q, a_text, topic):
    """统计一张卡片命中的标签，按来源分两组。

    问题命中（q_slugs）权重高，答案兜底（a_slugs）权重低；
    答案中已由问题命中的词不再重复计入 a_slugs（避免重复计数）。
    返回 (q_slugs, a_slugs)，各为有序去重 slug 列表。
    """
    def _hit(text):
        text = text.lower()
        found = set()
        for slug, pat in ERR_PATTERNS:
            if pat.search(text):
                found.add(slug)
        for t in sorted(set(KW_GLOBAL) | set(KW_TOPIC.get(topic, [])), key=len, reverse=True):
            if not t:
                continue
            if re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:/+\-]*', t):
                # 全 ASCII 词加边界，避免 Pawn 误命中 Spawn 等子串
                pat = r'(?<![A-Za-z0-9_])' + re.escape(t) + r'(?![A-Za-z0-9_])'
            else:
                pat = re.escape(t)
            if re.search(pat, text, re.I):
                found.add(slugify(t))
        return found

    q_slugs = _hit(q)
    a_slugs = _hit(a_text) - q_slugs
    return sorted(q_slugs), sorted(a_slugs)


def build_tag_index(data):
    """统计每个标签的加权得分与真实命中卡片数，并按组返回。

    得分 = 问题命中 × Q_WEIGHT + 答案命中 × A_WEIGHT，用于组内排序（问题优先）。
    真实命中卡片数用于 chip 徽标显示。同词跨组时只归入先出现的组。
    """
    score = {}   # slug -> 加权得分
    real = {}    # slug -> 命中卡片数
    for t, meta in data.items():
        for sn, su in meta['subs'].items():
            for c in su['cards']:
                for tg in c.get('q_tags', []):
                    score[tg] = score.get(tg, 0) + Q_WEIGHT
                    real[tg] = real.get(tg, 0) + 1
                for tg in c.get('a_tags', []):
                    score[tg] = score.get(tg, 0) + A_WEIGHT
                    real[tg] = real.get(tg, 0) + 1

    name_of = {slugify(t): t for t in KW_GLOBAL}
    for ts in KW_TOPIC.values():
        for t in ts:
            name_of.setdefault(slugify(t), t)
    for slug, name in ERR_TAGS:
        name_of[slug] = name

    groups = []          # list of (group_name, [(slug, name, score, real_count)])
    seen = set()

    def _entry(slug):
        if slug in seen:
            return None
        seen.add(slug)
        return (slug, name_of.get(slug, slug), score.get(slug, 0), real.get(slug, 0))

    errs = [e for e in (_entry(s) for s, _ in ERR_TAGS) if e and e[3] > 0]
    if errs:
        groups.append(('报错定位', errs))

    gbl = [e for e in (_entry(slugify(t)) for t in KW_GLOBAL) if e and e[3] > 0]
    gbl.sort(key=lambda e: e[2], reverse=True)
    if gbl:
        groups.append(('热门标签', gbl[:GLOBAL_TAG_N]))

    for topic in TOPIC_ORDER:
        ts = [e for e in (_entry(slugify(t)) for t in KW_TOPIC.get(topic, [])) if e and e[3] > 0]
        ts.sort(key=lambda e: e[2], reverse=True)
        if ts:
            groups.append((topic, ts[:TOPIC_TAG_N]))

    return groups


# ---------------- 对话档案（dialogue.html：卡片 → 原始对话上下文） ----------------

_PUNCT = '，。！？、；：“”‘’（）《》【】,.!?;:"\'()<>[]{}'


def norm_text(s):
    """归一化文本：小写 + 去空白 + 去标点，用于卡片问题与对话消息的模糊匹配。"""
    s = s.lower()
    for ch in _PUNCT:
        s = s.replace(ch, '')
    return re.sub(r'\s+', '', s)


def load_conversations():
    """解析两个对话数据源，返回 (msgs, user_index)。

    msgs: [(seq, msg_id, role, content)]，按时间序（主对话 JSON 在前，次对话 md 在后）。
    user_index: {归一化问题文本: 消息id}（同文去重保留第一个），供卡片定位。
    次对话 md 无消息 id，按 `s2-序号` 合成（与主对话 id 不冲突）。
    """
    msgs = []
    user_idx = {}
    seq = 0

    if os.path.exists(CONV_JSON):
        with open(CONV_JSON, encoding='utf-8') as f:
            conv = json.load(f)
        for m in conv:
            role = m.get('role')
            content = (m.get('content') or '').strip()
            if role not in ('user', 'assistant') or not content:
                continue
            seq += 1
            msgs.append((seq, m['id'], role, content))
            if role == 'user':
                user_idx.setdefault(norm_text(content), m['id'])

    if os.path.exists(CONV_MD):
        text = open(CONV_MD, encoding='utf-8').read()
        blocks = re.split(r'^##\s+\d+\.\s+', text, flags=re.M)
        for i, b in enumerate(blocks[1:], 1):
            lines = b.splitlines()
            role_cn = lines[0].strip() if lines else ''
            body = '\n'.join(lines[1:]).strip()
            if not body:
                continue
            mid = 's2-' + str(i)
            role = 'user' if role_cn == '用户' else 'assistant'
            seq += 1
            msgs.append((seq, mid, role, body))
            if role == 'user':
                user_idx.setdefault(norm_text(body), mid)

    return msgs, user_idx


def match_card_to_msg(q, user_idx):
    """卡片问题 → 对话消息 id。归一化前缀 30 字子串匹配（双源，取时间序首个命中）。"""
    nq = norm_text(q)
    if not nq:
        return None
    key = nq[:30]
    for un, mid in user_idx.items():
        if key in un:
            return mid
    return None


def build_dialogue_msgs(msgs):
    """把全部消息渲染为对话档案页内容（details 折叠列表，id=msg-<id>）。"""
    parts = []
    for seq, mid, role, content in msgs:
        if role == 'user':
            body = ''.join('<p>' + html.escape(x) + '</p>' for x in content.split('\n') if x.strip())
        else:
            body = content   # 助手消息已是 HTML
        summary_text = strip_md(content)[:44]
        role_cn = '用户' if role == 'user' else '助手'
        parts.append('<details class="dmsg" id="msg-' + mid + '" open>'
                     + '<summary><span class="drole drole-' + role + '">' + role_cn
                     + '</span><span class="dseq">#' + str(seq) + '</span>'
                     + '<span class="dtext">' + html.escape(summary_text) + '</span></summary>'
                     + '<div class="dbd">' + body + '</div></details>')
    return '\n'.join(parts)


def inline_rich(s, topic):
    """行内渲染：关键词荧光 + `code` + **strong**（在纯文本上标记，转义后还原）。"""
    t2, kbuf, ebuf = kw_mark(s, topic)
    h = html.escape(t2)
    h = re.sub(r'`([^`]+)`', r'<code>\1</code>', h)
    h = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', h)
    return kw_restore(h, kbuf, ebuf)


# ---------------- 答案按步骤分段 ----------------

ROLE_RE = re.compile(r'^(操作|观察|原因|结论|检查项|排查|验证|注意|正确公式|专家提示|结果|说明|小技巧|提示)[：:]\s*(.+)$')

STEP_NUM = re.compile(r'^(\d+)\.\s+(.+)$')
STEP_CN = re.compile(r'^(第[一二三四五六七八九十百\d]+[步环节]|步骤\s*\d+)\s*[：:]\s*(.+)$')
STEP_METHOD = re.compile(r'^(方法|方案)\s*([AB甲乙丙丁])\s*[：:]\s*(.+)$')
STEP_NODE = re.compile(r'^节点\s*(\d+)\s*[：:]\s*(.+)$')
STEP_ALPHA = re.compile(r'^([A-Z])\.\s+(.+)$')


def render_blocks(text, topic):
    """渲染一个块内的行：代码块 / 角色标签行 / 列表 / 标题 / 引用 / 段落。"""
    lines = text.split('\n')
    out, i = [], 0
    in_code, code_buf, li_buf = False, [], []

    def flush_li():
        nonlocal li_buf
        if li_buf:
            out.append('<ul>' + ''.join(li_buf) + '</ul>')
            li_buf = []

    while i < len(lines):
        ln = lines[i]
        if ln.strip().startswith('```'):
            if in_code:
                c = '\n'.join(code_buf)
                c2, kk, ee = kw_mark(c, topic)
                out.append('<pre><code>' + kw_restore(html.escape(c2), kk, ee) + '</code></pre>')
                code_buf, in_code = [], False
            else:
                in_code = True
            i += 1
            continue
        if in_code:
            code_buf.append(ln)
            i += 1
            continue
        s = ln.strip()
        if not s:
            flush_li()
            i += 1
            continue
        if re.match(r'^[-*]\s+', s):
            li_buf.append('<li>' + inline_rich(re.sub(r'^[-*]\s+', '', s), topic) + '</li>')
            i += 1
            continue
        flush_li()
        rm = ROLE_RE.match(s)
        if rm:
            role, rest = rm.group(1), rm.group(2)
            out.append('<p class="rp"><span class="rlb r-' + role + '">' + role
                       + '</span><span class="rpt">' + inline_rich(rest, topic) + '</span></p>')
            i += 1
            continue
        hm = re.match(r'^(#{1,4})\s+(.*)$', s)
        if hm:
            lvl = len(hm.group(1))
            out.append('<h' + str(lvl) + '>' + inline_rich(hm.group(2), topic) + '</h' + str(lvl) + '>')
            i += 1
            continue
        if re.match(r'^>\s?', s):
            out.append('<blockquote>' + inline_rich(re.sub(r'^>\s?', '', s), topic) + '</blockquote>')
            i += 1
            continue
        out.append('<p>' + inline_rich(s, topic) + '</p>')
        i += 1
    if in_code and code_buf:
        c = '\n'.join(code_buf)
        c2, kk, ee = kw_mark(c, topic)
        out.append('<pre><code>' + kw_restore(html.escape(c2), kk, ee) + '</code></pre>')
    flush_li()
    return '\n'.join(out)


def render_answer(a, topic):
    """把答案按步骤分段渲染。无步骤时按空行分段。"""
    lines = a.split('\n')
    cands = {'num': [], 'cn': [], 'node': [], 'method': [], 'alpha': []}
    for i, ln in enumerate(lines):
        s = ln.strip()
        m = STEP_NUM.match(s)
        if m:
            cands['num'].append((i, m.group(1), m.group(2)))
            continue
        m = STEP_CN.match(s)
        if m:
            cands['cn'].append((i, m.group(1), m.group(2)))
            continue
        m = STEP_NODE.match(s)
        if m:
            cands['node'].append((i, m.group(1), m.group(2)))
            continue
        m = STEP_METHOD.match(s)
        if m:
            cands['method'].append((i, m.group(1) + m.group(2), m.group(3)))
            continue
        m = STEP_ALPHA.match(s)
        if m:
            cands['alpha'].append((i, m.group(1), m.group(2)))

    if cands['num']:
        idxs = cands['num']
    elif cands['cn']:
        idxs = cands['cn']
    elif cands['node']:
        idxs = cands['node']
    elif cands['method']:
        idxs = cands['method']
    elif len(cands['alpha']) >= 2:
        idxs = cands['alpha']
    else:
        return render_blocks(a, topic)

    pos = [p for p, _, _ in idxs]
    out = []
    pre = '\n'.join(lines[:pos[0]]).strip()
    if pre:
        out.append('<div class="ans-pre">' + render_blocks(pre, topic) + '</div>')
    for k, (i, no, tt) in enumerate(idxs):
        end = pos[k + 1] if k + 1 < len(pos) else len(lines)
        body = '\n'.join(lines[i + 1:end]).strip()
        out.append('<div class="step"><div class="step-hd"><span class="step-no">'
                   + no + '</span><span class="step-tt">' + inline_rich(tt, topic)
                   + '</span></div>')
        if body:
            out.append('<div class="step-bd">' + render_blocks(body, topic) + '</div>')
        out.append('</div>')
    return '\n'.join(out)


def strip_md(text):
    t = re.sub(r'```.*?```', ' ', text, flags=re.S)
    t = re.sub(r'[#>*`\-]', ' ', t)
    t = re.sub(r'\*\*?', '', t)
    return re.sub(r'\s+', ' ', t).strip()


def parse_sub_md(path, topic):
    with open(path, encoding='utf-8') as f:
        text = f.read()
    cards = []
    blocks = re.split(r'^##\s+(\d+)\.\s+(.+)$', text, flags=re.M)
    i = 1
    while i < len(blocks) - 1:
        idx = int(blocks[i])
        title = blocks[i + 1].strip()
        body = blocks[i + 2] if i + 2 < len(blocks) else ''
        qm = re.search(r'\*\*问题：\*\*(.*?)(?=\*\*答案：\*\*|\Z)', body, re.S)
        am = re.search(r'\*\*答案：\*\*(.*)', body, re.S)
        q = qm.group(1).strip() if qm else title
        a = am.group(1).strip() if am else ''
        if not a:
            a = '（原始对话未返回有效回答，此卡片暂无内容。可参考同主题其他卡片，或重新向 AI 咨询补全。）'
        q_tags, a_tags = compute_tags(q, strip_md(a), topic)
        cards.append({'id': idx, 'q': q,
                      'a_html': render_answer(a, topic),
                      'a_text': strip_md(a),
                      'q_tags': q_tags,
                      'a_tags': a_tags,
                      'tags': sorted(set(q_tags) | set(a_tags))})
        i += 3
    return cards


def build_data():
    data = {}
    for topic in TOPIC_ORDER:
        tdir = os.path.join(SRC, topic)
        if not os.path.isdir(tdir):
            continue
        subs = {}
        for name in sorted(os.listdir(tdir)):
            if not name.endswith('.md'):
                continue
            sub = name[:-3]
            cards = parse_sub_md(os.path.join(tdir, name), topic)
            if not cards:
                continue
            subs[sub] = {'icon': SUB_ICON.get(sub, '📄'), 'cards': cards}
        if subs:
            data[topic] = {'desc': TOPIC_META.get(topic, ''), 'subs': subs}
    return data


# ---------------- 静态 HTML 片段 ----------------

def card_html(c, topic):
    text = html.escape((c['q'] + ' ' + c.get('a_text', '')).lower())
    tags = c.get('tags', [])
    tagattr = ' data-tags="' + ' '.join(tags) + '"' if tags else ''
    q_html = inline_rich(c['q'], topic)
    if c.get('msg_id'):
        ctx = ('<a class="ctxlink" href="dialogue.html#msg-' + c['msg_id']
               + '" title="查看该卡片对应的原始对话及前后文">💬 对话上下文</a>')
    else:
        ctx = '<span class="ctxmiss" title="该卡片未在已收录对话中找到对应记录">对话未收录</span>'
    return ('<details class="card"' + tagattr + ' data-text="' + text + '">'
            '<summary><span class="qid">#' + str(c['id']) + '</span>'
            '<span class="qtext">' + q_html + '</span><span class="tog">▾</span></summary>'
            '<div class="ans">' + c['a_html'] + ctx + '</div></details>')


def sub_html(icon, name, cards, topic):
    inner = ''.join(card_html(c, topic) for c in cards)
    return ('<details class="sub"><summary><span class="ic">' + icon + '</span>'
            + html.escape(name) + '<span class="scount">' + str(len(cards)) + '</span></summary>'
            + inner + '</details>')


def topic_html(t, meta, tcls):
    subs = meta['subs']
    total = sum(len(s['cards']) for s in subs.values())
    inner = ''.join(sub_html(su['icon'], sn, su['cards'], t) for sn, su in subs.items())
    return ('<details class="topic ' + tcls + '" open><summary><span class="ic">📁</span>'
            + html.escape(t) + '<span class="scount">' + str(total) + '</span></summary>'
            + '<p class="tdesc">' + html.escape(meta['desc']) + '</p>'
            + inner + '</details>')


def tag_css(groups):
    """为每个标签生成 4 条纯 CSS 筛选规则（:has 联动，无 JS 也可用）。"""
    lines = []
    for _, entries in groups:
        for slug, *_ in entries:
            sel = 'body:has(#tagf-' + slug + ':checked)'
            lines.append(sel + ' details.card:not([data-tags~="' + slug + '"]){display:none}')
            lines.append(sel + ' details.sub:not(:has([data-tags~="' + slug + '"])){display:none}')
            lines.append(sel + ' details.topic:not(:has([data-tags~="' + slug + '"])){display:none}')
            lines.append(sel + ' details.card[data-tags~="' + slug + '"]{outline:2px solid var(--accent);outline-offset:-1px}')
            lines.append(sel + ' label[for="tagf-' + slug + '"]{border-color:var(--accent);color:var(--accent);background:var(--mark);font-weight:700}')
    return '\n'.join(lines)


def tagbar_html(groups, total):
    """生成右侧标签导航栏 HTML（radio 单选 + 分组 chips）。“全部”独立置于分组之前。"""
    radios = ['<input type="radio" name="tagf" id="tagf-all" checked>']
    all_label = ('<label for="tagf-all" class="tag-chip chip-all">全部'
                 + '<span class="tcnt">' + str(total) + '</span></label>')
    group_html = ['<div id="tagAll"><div class="chips">' + all_label + '</div></div>']
    for gname, entries in groups:
        labels = []
        for slug, name, sc, cnt in entries:
            radios.append('<input type="radio" name="tagf" id="tagf-' + slug + '">')
            labels.append('<label for="tagf-' + slug + '" class="tag-chip">' + html.escape(name)
                          + '<span class="tcnt">' + str(cnt) + '</span></label>')
        group_html.append('<details class="tgrp" open><summary>' + html.escape(gname) + '</summary>'
                          + '<div class="chips">' + ''.join(labels) + '</div></details>')
    return ('<aside id="tagbar">'
            + '<div id="tbar-head"><h3>🏷 标签导航</h3><p>点击关键词筛选卡片 · 单选</p></div>'
            + '<div id="tagStat">全部 ' + str(total) + ' 张卡片</div>'
            + '<div class="tag-radios">' + ''.join(radios) + '</div>'
            + ''.join(group_html)
            + '<div id="tbar-tip">标签来自问题（权重 '
            + str(Q_WEIGHT) + '）与答案（权重 ' + str(A_WEIGHT)
            + '）词表命中，按得分排序（问题优先）。点标签后：仅显示含该关键词的卡片，命中卡片描边高亮；空的主题/子主题自动隐藏。点「全部」恢复。</div>'
            + '</aside>')


INDEX_HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>五彩湾 UE 开发知识库 · 速查手册</title>
<style>
/* ============ 主题变量（4 套配色，radio-hack 切换，纯 CSS） ============ */
/* 默认：学霸荧光（暖米白便签） */
:root{
  --bg:#faf6ec; --panel:#fffdf7; --panel2:#f6efdc; --card:#fffbea;
  --border:#e6dcc2; --text:#3d3526; --muted:#7c7156; --dim:#a89a7c;
  --accent:#e08a1e; --accent2:#2e9e6b;
  --codebg:#f7f1df; --codefg:#b3531d;
  --mark:#ffdf5e; --markfg:#4a3a00;
  --markerr:#ffc1c1; --markerrfg:#8f1f1f;
  --t0:#2f6fd0; --t1:#1f8a5f; --t2:#7a4fd0; --t3:#c07f1a; --t4:#c94f88; --t5:#1f8f96;
}
/* 薄荷清新（浅绿） */
#th1:checked ~ #app{
  --bg:#eef6ef; --panel:#f7fcf8; --panel2:#e4f1e7; --card:#f2faf4;
  --border:#cfe3d4; --text:#2f4236; --muted:#5f7a6a; --dim:#8aa395;
  --accent:#2e9e6b; --accent2:#3a7bd5;
  --codebg:#e8f3ec; --codefg:#1f6b43;
  --mark:#9fe8c8; --markfg:#104a30;
  --markerr:#ffd0c9; --markerrfg:#9a2b1c;
  --t0:#2f6fd0; --t1:#1f8a5f; --t2:#7a4fd0; --t3:#c07f1a; --t4:#c94f88; --t5:#1f8f96;
}
/* 黄昏暖读（暖橙） */
#th2:checked ~ #app{
  --bg:#f8f1e7; --panel:#fdf9f1; --panel2:#f3e6d2; --card:#fbf4e7;
  --border:#e8d5b8; --text:#4a3a28; --muted:#8a7052; --dim:#b09a7c;
  --accent:#d97a2b; --accent2:#8a5cc0;
  --codebg:#f6eee0; --codefg:#a05a1a;
  --mark:#ffc478; --markfg:#5c3608;
  --markerr:#ffd0c0; --markerrfg:#9a331c;
  --t0:#2f6fd0; --t1:#1f8a5f; --t2:#7a4fd0; --t3:#c07f1a; --t4:#c94f88; --t5:#1f8f96;
}
/* 深空夜读（深色） */
#th3:checked ~ #app{
  --bg:#0e1116; --panel:#151a23; --panel2:#1b2230; --card:#1d2433;
  --border:#2a3346; --text:#e8ecf4; --muted:#9aa4b8; --dim:#6b7688;
  --accent:#4da3ff; --accent2:#3ddc97;
  --codebg:#0a0d13; --codefg:#7fd4ff;
  --mark:#4da3ff55; --markfg:#dbeafe;
  --markerr:#5a2a2a; --markerrfg:#ff9c9c;
  --t0:#4da3ff; --t1:#3ddc97; --t2:#a97bff; --t3:#ffb04d; --t4:#ff7ab8; --t5:#4adbe6;
}
.theme-radio{display:none}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font:14px/1.65 "Segoe UI","Microsoft YaHei",system-ui,sans-serif}
#app{display:flex;height:100vh;overflow:hidden}
/* ===== 侧栏 ===== */
#sidebar{width:292px;min-width:292px;background:var(--panel);border-right:1px solid var(--border);
  display:flex;flex-direction:column;overflow:hidden}
#shead{padding:15px 16px 8px;border-bottom:1px solid var(--border)}
#shead h1{font-size:15px;color:var(--accent)}
#shead p{font-size:11px;color:var(--dim);margin-top:3px}
/* 主题切换器 */
.themes{display:flex;flex-wrap:wrap;gap:6px;padding:12px 12px 4px}
.theme-lbl{flex:1 1 44%;text-align:center;padding:6px 4px;border:1px solid var(--border);
  border-radius:8px;background:var(--panel2);color:var(--muted);cursor:pointer;
  font-size:11.5px;user-select:none;transition:all .15s}
.theme-lbl:hover{border-color:var(--accent)}
#th0:checked ~ #app label[for="th0"],#th1:checked ~ #app label[for="th1"],
#th2:checked ~ #app label[for="th2"],#th3:checked ~ #app label[for="th3"]{
  border-color:var(--accent);color:var(--accent);font-weight:700;background:var(--mark)}
.theme-radio:focus ~ #app label{border-color:var(--accent)}
#search{margin:10px 12px;padding:9px 12px;border-radius:8px;border:1px solid var(--border);
  background:var(--panel2);color:var(--text);outline:none;font-size:13px}
#search:focus{border-color:var(--accent)}
#tools{display:flex;gap:8px;padding:0 12px 10px}
#tools button{flex:1;padding:7px 0;border-radius:7px;border:1px solid var(--border);
  background:var(--panel2);color:var(--text);font-size:12px;cursor:pointer}
#tools button:hover{border-color:var(--accent)}
#sidebarTip{padding:12px 14px;color:var(--dim);font-size:11px;line-height:1.6;border-top:1px solid var(--border);margin:0 12px}
/* ===== 主区域 ===== */
#main{flex:1;display:flex;flex-direction:column;overflow:hidden}
#mhead{padding:16px 24px 12px;border-bottom:1px solid var(--border);background:var(--panel)}
#mhead h2{font-size:18px}
#mhead p{font-size:12.5px;color:var(--muted);margin-top:4px}
#content{flex:1;overflow-y:auto;padding:18px 26px 70px;max-width:1080px}
/* ===== 折叠树 ===== */
details.topic{border:1px solid var(--border);border-left:5px solid var(--t0);border-radius:12px;margin-bottom:14px;background:var(--card);overflow:hidden}
details.topic.t1{border-left-color:var(--t1)}
details.topic.t2{border-left-color:var(--t2)}
details.topic.t3{border-left-color:var(--t3)}
details.topic.t4{border-left-color:var(--t4)}
details.topic.t5{border-left-color:var(--t5)}
details.topic>summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:10px;
  padding:14px 18px;font-size:16px;font-weight:700;user-select:none}
details.topic>summary::-webkit-details-marker{display:none}
details.topic>summary .ic{font-size:20px}
details.topic>summary .scount{margin-left:auto;font-size:12px;color:var(--dim);
  background:var(--panel2);border:1px solid var(--border);border-radius:10px;padding:2px 10px}
details.topic[open]>summary{border-bottom:1px solid var(--border)}
.tdesc{color:var(--muted);font-size:13px;padding:10px 18px 4px}
details.sub{margin:10px 14px;border:1px solid var(--border);border-radius:10px;background:var(--panel)}
details.sub>summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:9px;
  padding:11px 15px;font-size:14px;user-select:none}
details.sub>summary::-webkit-details-marker{display:none}
details.sub>summary .ic{font-size:17px}
details.sub>summary .scount{margin-left:auto;font-size:11px;color:var(--dim)}
details.topic>summary:hover,details.sub>summary:hover{background:var(--panel2)}
details.card{margin:8px 14px;border:1px solid var(--border);border-radius:8px;background:var(--bg);overflow:hidden}
details.card[hidden]{display:none}
details.card>summary{list-style:none;cursor:pointer;display:flex;align-items:flex-start;gap:10px;
  padding:11px 14px;user-select:none}
details.card>summary::-webkit-details-marker{display:none}
details.card>summary .qid{font-size:11px;color:var(--accent);font-family:Consolas,monospace;padding-top:2px;min-width:34px}
details.card>summary .qtext{flex:1;font-weight:600;font-size:13.5px;line-height:1.5}
details.card>summary .tog{color:var(--dim);transition:transform .15s}
details.card[open]>summary .tog{transform:rotate(180deg)}
details.card[open]>summary{border-bottom:1px solid var(--border);background:var(--panel)}
.ans{padding:10px 18px 14px 58px;background:var(--panel);font-size:13.5px}
.ans p{margin:7px 0}
.ans h1,.ans h2,.ans h3,.ans h4{margin:12px 0 6px;font-size:14px;color:var(--accent2)}
.ans ul,.ans ol{margin:6px 0 6px 22px}
.ans li{margin:3px 0}
.ans code{background:var(--codebg);border:1px solid var(--border);border-radius:4px;padding:1px 5px;
  font-size:12px;color:var(--codefg);font-family:Consolas,monospace}
.ans pre{background:var(--codebg);border:1px solid var(--border);border-radius:8px;padding:12px;overflow-x:auto;margin:8px 0}
.ans pre code{background:none;border:none;padding:0;color:var(--codefg);font-size:12px;line-height:1.5}
.ans blockquote{border-left:3px solid var(--accent);padding:4px 12px;margin:8px 0;color:var(--muted);
  background:var(--panel2);border-radius:0 6px 6px 0}
.ctxlink{display:inline-block;margin-top:10px;font-size:12px;color:var(--accent2);
  border:1px solid var(--border);border-radius:7px;padding:3px 11px;background:var(--panel2);
  text-decoration:none;user-select:none;transition:all .15s}
.ctxlink:hover{border-color:var(--accent);color:var(--accent)}
.ctxmiss{display:inline-block;margin-top:10px;font-size:12px;color:var(--dim);
  border:1px dashed var(--border);border-radius:7px;padding:3px 11px;background:var(--panel2)}
/* ===== 关键词荧光 ===== */
mark{background:var(--mark);color:var(--markfg);border-radius:3px;padding:0 2px}
mark.err{background:var(--markerr);color:var(--markerrfg);font-weight:600}
mark.kw{background:var(--mark);color:var(--markfg);font-weight:600}
/* ===== 步骤分段（学霸笔记风） ===== */
.ans-pre{color:var(--muted);border-bottom:1px dashed var(--border);padding-bottom:8px;margin-bottom:10px}
.ans-pre p{margin:6px 0}
.step{position:relative;margin:10px 0;border:1px solid var(--border);border-radius:10px;
  background:var(--card);overflow:hidden}
.step-hd{display:flex;align-items:center;gap:9px;padding:8px 12px;background:var(--panel2);
  border-bottom:1px dashed var(--border)}
.step-no{width:21px;height:21px;border-radius:50%;background:var(--accent);color:#fff;
  font-size:11.5px;font-weight:700;display:inline-flex;align-items:center;justify-content:center;flex:none}
.step-tt{font-weight:700;font-size:13.5px;line-height:1.45}
.step-bd{padding:8px 12px 10px}
.step-bd p{margin:6px 0}
/* 角色标签 */
.rp{margin:5px 0;display:flex;gap:7px;align-items:flex-start}
.rlb{flex:none;display:inline-block;font-size:11px;font-weight:700;line-height:1.5;
  padding:0 8px;border-radius:9px;margin-top:1px;white-space:nowrap}
.rpt{flex:1}
.r-操作{background:#2563eb22;color:#1d4ed8}
.r-观察,.r-验证{background:#05966922;color:#047857}
.r-原因{background:#d9770622;color:#b45309}
.r-结论{background:#7c3aed22;color:#6d28d9}
.r-注意,.r-排查{background:#dc262622;color:#b91c1c}
.r-检查项{background:#2563eb22;color:#1d4ed8}
.r-结果{background:#0d948822;color:#0f766e}
.r-提示,.r-说明{background:#64748b22;color:#475569}
.r-专家提示,.r-小技巧{background:#b4530922;color:#92400e}
.r-正确公式{background:#db277722;color:#be185d}
.noscript{background:#3a2a2a;color:#ffb4b4;border:1px solid #5a3a3a;padding:10px 16px;font-size:12.5px;margin:0}
::-webkit-scrollbar{width:9px;height:9px}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:5px}
::-webkit-scrollbar-track{background:transparent}
/* ===== 右侧标签导航栏 ===== */
#tagbar{width:236px;min-width:236px;background:var(--panel);border-left:1px solid var(--border);
  overflow-y:auto;padding:0 0 20px}
#tbar-head{padding:14px 16px 6px;border-bottom:1px solid var(--border)}
#tbar-head h3{font-size:14px;color:var(--accent)}
#tbar-head p{font-size:11px;color:var(--dim);margin-top:2px}
#tagStat{padding:8px 16px;font-size:12px;color:var(--muted);border-bottom:1px dashed var(--border)}
.tag-radios{display:none}
#tagAll{padding:9px 12px 2px}
.tgrp{margin:10px 12px 0;border:1px solid var(--border);border-radius:9px;background:var(--panel2);overflow:hidden}
.tgrp>summary{list-style:none;cursor:pointer;font-size:12.5px;font-weight:700;padding:8px 12px;
  color:var(--muted);user-select:none;display:flex;align-items:center;gap:6px}
.tgrp>summary::-webkit-details-marker{display:none}
.tgrp>summary::before{content:"▸";color:var(--dim);transition:transform .15s}
.tgrp[open]>summary::before{transform:rotate(90deg)}
.tgrp[open]>summary{border-bottom:1px solid var(--border)}
.chips{display:flex;flex-wrap:wrap;gap:5px;padding:9px 10px}
.tag-chip{display:inline-flex;align-items:center;gap:4px;font-size:11px;line-height:1.4;
  padding:3px 8px;border:1px solid var(--border);border-radius:11px;background:var(--panel);
  color:var(--muted);cursor:pointer;user-select:none;transition:all .15s}
.tag-chip:hover{border-color:var(--accent);color:var(--accent)}
.tag-chip .tcnt{font-size:10px;color:var(--dim);background:var(--panel2);border-radius:8px;padding:0 5px}
.tag-chip.chip-all{background:var(--panel2)}
#tbar-tip{padding:10px 14px;color:var(--dim);font-size:10.5px;line-height:1.6;margin:12px 12px 0;
  border-top:1px solid var(--border)}
@media(max-width:1180px){#tagbar{display:none}}
/* ===== 标签筛选规则（生成期注入，纯 CSS :has 联动，无 JS 可用） ===== */
__TAGCSS__
</style>
</head>
<body>
<input type="radio" name="th" id="th0" class="theme-radio" checked>
<input type="radio" name="th" id="th1" class="theme-radio">
<input type="radio" name="th" id="th2" class="theme-radio">
<input type="radio" name="th" id="th3" class="theme-radio">
<div id="app">
  <div id="sidebar">
    <div id="shead">
      <h1>🗺️ 五彩湾 UE 知识库</h1>
      <p>本地离线速查 · 双击即开 · 纯静态</p>
    </div>
    <div class="themes">
      <label for="th0" class="theme-lbl">🖍️ 学霸荧光</label>
      <label for="th1" class="theme-lbl">🌿 薄荷清新</label>
      <label for="th2" class="theme-lbl">🌅 黄昏暖读</label>
      <label for="th3" class="theme-lbl">🌙 深空夜读</label>
    </div>
    <input id="search" type="text" placeholder="搜索问题 / 报错 / 节点…">
    <div id="tools">
      <button id="expandBtn" type="button">全部展开</button>
      <button id="collapseBtn" type="button">收起子项</button>
    </div>
    <div id="sidebarTip">本页内容已直接写入 HTML，<b>无需 JavaScript</b> 即可逐级点开主题→子主题→卡片。顶部可切换 4 套配色；答案已按步骤分段，关键词荧光标注（黄色=术语，红色=报错码/坐标）。</div>
  </div>
  <div id="main">
    <header id="mhead">
      <h2>📚 五彩湾 UE 开发知识库 · 速查手册</h2>
      <p>__STAT__ 张卡片，源自你的 Epic 开发者助手对话。点击主题 → 子主题 → 卡片逐级展开查看。</p>
    </header>
    <div id="content">
__TREE__
    </div>
  </div>
__TAGBAR__
</div>
<noscript><div class="noscript">⚠️ 当前环境未启用 JavaScript：搜索与一键展开不可用，但所有卡片内容均可逐级点击展开查看。</div></noscript>
<script>
/* ====== 增强：搜索 + 全部展开/收起（不执行也不影响核心阅读） ====== */
(function(){
  try{
    var box=document.getElementById('search'); if(!box) return;
    var cards=[].slice.call(document.querySelectorAll('details.card'));
    box.addEventListener('input',function(){
      var q=box.value.trim().toLowerCase();
      cards.forEach(function(c){
        var hit=!q||(c.getAttribute('data-text')||'').indexOf(q)>=0;
        c.hidden=!hit;
        if(hit&&q){ var p=c.parentElement; while(p&&p.tagName==='DETAILS'){ p.open=true; p=p.parentElement; } }
      });
    });
    var eb=document.getElementById('expandBtn'); if(eb) eb.onclick=function(){document.querySelectorAll('details').forEach(function(d){d.open=true;});};
    var cb=document.getElementById('collapseBtn'); if(cb) cb.onclick=function(){document.querySelectorAll('details.sub,details.card').forEach(function(d){d.open=false;});};
  }catch(e){}
})();
/* ====== 增强2：标签导航（纯 CSS 筛选已生效；这里补展开路径 + 滚动定位 + 计数） ====== */
(function(){
  try{
    var radios=[].slice.call(document.querySelectorAll('input[name="tagf"]'));
    var cards=[].slice.call(document.querySelectorAll('details.card'));
    var stat=document.getElementById('tagStat');
    var total=cards.length;
    radios.forEach(function(r){
      r.addEventListener('change',function(){
        if(!r.checked) return;
        var slug=r.id.slice(5);
        if(slug==='all'){ if(stat) stat.textContent='全部 '+total+' 张卡片'; return; }
        var lbl=document.querySelector('label[for="tagf-'+slug+'"]');
        var nm=(lbl&&lbl.firstChild)?lbl.firstChild.textContent.trim():slug;
        var hits=cards.filter(function(c){
          return (' '+(c.getAttribute('data-tags')||'')+' ').indexOf(' '+slug+' ')>=0;
        });
        if(stat) stat.textContent=nm+' · 命中 '+hits.length+' 张卡片';
        if(!hits.length) return;
        var first=hits[0];
        var p=first.parentElement;
        while(p&&p.tagName==='DETAILS'){ p.open=true; p=p.parentElement; }
        if(first.scrollIntoView){ first.scrollIntoView({behavior:'smooth',block:'start'}); }
      });
    });
  }catch(e){}
})();
</script>
</body>
</html>
'''


DIALOGUE_HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>五彩湾知识库 · 原始对话档案</title>
<style>
/* ============ 主题变量（与主站一致的 4 套配色，radio-hack 切换，纯 CSS） ============ */
:root{
  --bg:#faf6ec; --panel:#fffdf7; --panel2:#f6efdc; --card:#fffbea;
  --border:#e6dcc2; --text:#3d3526; --muted:#7c7156; --dim:#a89a7c;
  --accent:#e08a1e; --accent2:#2e9e6b;
  --codebg:#f7f1df; --codefg:#b3531d;
  --mark:#ffdf5e; --markfg:#4a3a00;
  --markerr:#ffc1c1; --markerrfg:#8f1f1f;
}
#th1:checked ~ #app{--bg:#eef6ef;--panel:#f7fcf8;--panel2:#e4f1e7;--card:#f2faf4;
  --border:#cfe3d4;--text:#2f4236;--muted:#5f7a6a;--dim:#8aa395;
  --accent:#2e9e6b;--accent2:#3a7bd5;--codebg:#e8f3ec;--codefg:#1f6b43;
  --mark:#9fe8c8;--markfg:#104a30;--markerr:#ffd0c9;--markerrfg:#9a2b1c}
#th2:checked ~ #app{--bg:#f8f1e7;--panel:#fdf9f1;--panel2:#f3e6d2;--card:#fbf4e7;
  --border:#e8d5b8;--text:#4a3a28;--muted:#8a7052;--dim:#b09a7c;
  --accent:#d97a2b;--accent2:#8a5cc0;--codebg:#f6eee0;--codefg:#a05a1a;
  --mark:#ffc478;--markfg:#5c3608;--markerr:#ffd0c0;--markerrfg:#9a331c}
#th3:checked ~ #app{--bg:#0e1116;--panel:#151a23;--panel2:#1b2230;--card:#1d2433;
  --border:#2a3346;--text:#e8ecf4;--muted:#9aa4b8;--dim:#6b7688;
  --accent:#4da3ff;--accent2:#3ddc97;--codebg:#0a0d13;--codefg:#7fd4ff;
  --mark:#4da3ff55;--markfg:#dbeafe;--markerr:#5a2a2a;--markerrfg:#ff9c9c}
.theme-radio{display:none}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font:14px/1.65 "Segoe UI","Microsoft YaHei",system-ui,sans-serif}
#app{display:flex;height:100vh;overflow:hidden}
#sidebar{width:280px;min-width:280px;background:var(--panel);border-right:1px solid var(--border);
  display:flex;flex-direction:column;overflow:hidden}
#shead{padding:15px 16px 8px;border-bottom:1px solid var(--border)}
#shead h1{font-size:15px;color:var(--accent)}
#shead p{font-size:11px;color:var(--dim);margin-top:3px}
.themes{display:flex;flex-wrap:wrap;gap:6px;padding:12px 12px 4px}
.theme-lbl{flex:1 1 44%;text-align:center;padding:6px 4px;border:1px solid var(--border);
  border-radius:8px;background:var(--panel2);color:var(--muted);cursor:pointer;
  font-size:11.5px;user-select:none;transition:all .15s}
.theme-lbl:hover{border-color:var(--accent)}
#th0:checked ~ #app label[for="th0"],#th1:checked ~ #app label[for="th1"],
#th2:checked ~ #app label[for="th2"],#th3:checked ~ #app label[for="th3"]{
  border-color:var(--accent);color:var(--accent);font-weight:700;background:var(--mark)}
#sidebarTip{padding:12px 14px;color:var(--dim);font-size:11px;line-height:1.6;border-top:1px solid var(--border);margin:0 12px}
#main{flex:1;display:flex;flex-direction:column;overflow:hidden}
#mhead{padding:16px 24px 12px;border-bottom:1px solid var(--border);background:var(--panel)}
#mhead h2{font-size:18px}
#mhead p{font-size:12.5px;color:var(--muted);margin-top:4px}
#content{flex:1;overflow-y:auto;padding:18px 26px 70px;max-width:1080px}
/* ===== 消息列表（学霸笔记风） ===== */
.dmsg{border:1px solid var(--border);border-radius:10px;margin:8px 0;background:var(--card);overflow:hidden}
.dmsg>summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:10px;
  padding:10px 14px;user-select:none}
.dmsg>summary::-webkit-details-marker{display:none}
.drole{flex:none;font-size:11px;font-weight:700;border-radius:9px;padding:1px 9px}
.drole-user{background:var(--mark);color:var(--markfg)}
.drole-assistant{background:var(--markerr);color:var(--markerrfg)}
.dseq{flex:none;font-size:11px;color:var(--dim);font-family:Consolas,monospace}
.dtext{flex:1;font-size:12.5px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.dmsg[open]>summary{border-bottom:1px dashed var(--border);background:var(--panel2)}
.dmsg .dbd{padding:10px 16px 12px;background:var(--panel);font-size:13.5px}
.dmsg .dbd p{margin:6px 0}
.dmsg .dbd h1,.dmsg .dbd h2,.dmsg .dbd h3,.dmsg .dbd h4{margin:10px 0 5px;font-size:14px;color:var(--accent2)}
.dmsg .dbd ul,.dmsg .dbd ol{margin:6px 0 6px 22px}
.dmsg .dbd li{margin:3px 0}
.dmsg .dbd code{background:var(--codebg);border:1px solid var(--border);border-radius:4px;padding:1px 5px;
  font-size:12px;color:var(--codefg);font-family:Consolas,monospace}
.dmsg .dbd pre{background:var(--codebg);border:1px solid var(--border);border-radius:8px;padding:12px;overflow-x:auto;margin:8px 0}
.dmsg .dbd pre code{background:none;border:none;padding:0;font-size:12px;line-height:1.5}
.dmsg .dbd blockquote{border-left:3px solid var(--accent);padding:4px 12px;margin:8px 0;color:var(--muted);
  background:var(--panel2);border-radius:0 6px 6px 0}
.dmsg.active{border-color:var(--accent);outline:2px solid var(--accent);outline-offset:-1px}
.dmsg.active>summary{background:var(--mark);color:var(--markfg)}
.noscript{background:#3a2a2a;color:#ffb4b4;border:1px solid #5a3a3a;padding:10px 16px;font-size:12.5px;margin:0}
::-webkit-scrollbar{width:9px;height:9px}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:5px}
::-webkit-scrollbar-track{background:transparent}
</style>
</head>
<body>
<input type="radio" name="th" id="th0" class="theme-radio" checked>
<input type="radio" name="th" id="th1" class="theme-radio">
<input type="radio" name="th" id="th2" class="theme-radio">
<input type="radio" name="th" id="th3" class="theme-radio">
<div id="app">
  <div id="sidebar">
    <div id="shead">
      <h1>🗨️ 原始对话档案</h1>
      <p>知识库卡片对应的完整对话记录</p>
    </div>
    <div class="themes">
      <label for="th0" class="theme-lbl">🖍️ 学霸荧光</label>
      <label for="th1" class="theme-lbl">🌿 薄荷清新</label>
      <label for="th2" class="theme-lbl">🌅 黄昏暖读</label>
      <label for="th3" class="theme-lbl">🌙 深空夜读</label>
    </div>
    <div id="sidebarTip">从主站任意卡片点「💬 对话上下文」会跳到对应问答并高亮，自动展开前后各 3 条。<br><br>本页所有消息默认展开：无 JavaScript 也可逐条查看完整对话；启用后定位跳转更聚焦。</div>
  </div>
  <div id="main">
    <header id="mhead">
      <h2>🗨️ Epic 开发者助手 · 原始对话</h2>
      <p>__STAT__ 条消息，按时间顺序排列。用户提问 / 助手回答。</p>
    </header>
    <div id="content">
__MSGS__
    </div>
  </div>
</div>
<noscript><div class="noscript">⚠️ 当前环境未启用 JavaScript：全部消息默认展开，浏览器原生锚点跳转仍可用。</div></noscript>
<script>
/* ====== 增强：锚点定位 → 高亮目标 + 展开前后各 3 条 + 平滑滚动（无 JS 时全可见） ====== */
(function(){
  try{
    var h=location.hash||'';
    if(h.indexOf('#msg-')!==0) return;
    var t=document.getElementById(h.slice(1));
    if(!t) return;
    var msgs=[].slice.call(document.querySelectorAll('.dmsg'));
    var idx=msgs.indexOf(t);
    if(idx<0) return;
    var lo=Math.max(0,idx-3), hi=Math.min(msgs.length-1,idx+3);
    msgs.forEach(function(m,i){
      if(i>=lo&&i<=hi){ m.open=true; } else { m.open=false; }
      if(m===t){ m.classList.add('active'); }
    });
    if(t.scrollIntoView){ t.scrollIntoView({behavior:'smooth',block:'start'}); }
  }catch(e){}
})();
</script>
</body>
</html>
'''


def main():
    os.makedirs(OUT, exist_ok=True)
    data = build_data()

    # 对话档案：先完成卡片 -> 消息 id 匹配（tree 渲染时卡片需要 msg_id）
    msgs, user_idx = load_conversations()
    nmatched = 0
    for t, meta in data.items():
        for su in meta['subs'].values():
            for c in su['cards']:
                c['msg_id'] = match_card_to_msg(c['q'], user_idx)
                if c['msg_id']:
                    nmatched += 1

    tree = ''.join(topic_html(t, meta, 't' + str(i)) for i, (t, meta) in enumerate(data.items()))
    total = sum(len(su['cards']) for t in data.values() for su in t['subs'].values())
    nsub = sum(len(t['subs']) for t in data.values())
    ntop = len(data)
    stat = '{} 大主题 · {} 子主题 · {}'.format(ntop, nsub, total)

    groups = build_tag_index(data)
    tag_css_rules = tag_css(groups)
    tagbar = tagbar_html(groups, total)

    html_out = (INDEX_HTML
                .replace('__STAT__', stat)
                .replace('__TREE__', tree)
                .replace('__TAGCSS__', tag_css_rules)
                .replace('__TAGBAR__', tagbar))
    with open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_out)

    dlg_stat = '{} 条消息 · 来自 2 段对话'.format(len(msgs))
    dialogue_html = (DIALOGUE_HTML
                     .replace('__STAT__', dlg_stat)
                     .replace('__MSGS__', build_dialogue_msgs(msgs)))
    with open(os.path.join(OUT, 'dialogue.html'), 'w', encoding='utf-8') as f:
        f.write(dialogue_html)

    print('博客站点已重新生成（学霸笔记风 · 纯静态预渲染版）: {}'.format(os.path.join(OUT, 'index.html')))
    print('  主题数: {}  子主题数: {}  卡片总数: {}'.format(ntop, nsub, total))
    ntag = sum(len(e) for _, e in groups)
    print('  标签组: {}  标签总数: {}'.format(len(groups), ntag))
    print('  对话档案: {} 条消息 -> {}'.format(len(msgs), os.path.join(OUT, 'dialogue.html')))
    print('  卡片定位对话: {}/{}'.format(nmatched, total))


if __name__ == '__main__':
    main()
