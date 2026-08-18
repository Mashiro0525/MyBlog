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
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, 'pkm_cards_v2')
OUT = os.path.join(BASE, 'pkm_blog')

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
        cards.append({'id': idx, 'q': q,
                      'a_html': render_answer(a, topic),
                      'a_text': strip_md(a)})
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
    q_html = inline_rich(c['q'], topic)
    return ('<details class="card" data-text="' + text + '">'
            '<summary><span class="qid">#' + str(c['id']) + '</span>'
            '<span class="qtext">' + q_html + '</span><span class="tog">▾</span></summary>'
            '<div class="ans">' + c['a_html'] + '</div></details>')


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
</script>
</body>
</html>
'''


def main():
    os.makedirs(OUT, exist_ok=True)
    data = build_data()
    tree = ''.join(topic_html(t, meta, 't' + str(i)) for i, (t, meta) in enumerate(data.items()))
    total = sum(len(su['cards']) for t in data.values() for su in t['subs'].values())
    nsub = sum(len(t['subs']) for t in data.values())
    ntop = len(data)
    stat = '{} 大主题 · {} 子主题 · {}'.format(ntop, nsub, total)
    html_out = (INDEX_HTML
                .replace('__STAT__', stat)
                .replace('__TREE__', tree))
    with open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_out)
    print('博客站点已重新生成（学霸笔记风 · 纯静态预渲染版）: {}'.format(os.path.join(OUT, 'index.html')))
    print('  主题数: {}  子主题数: {}  卡片总数: {}'.format(ntop, nsub, total))


if __name__ == '__main__':
    main()
