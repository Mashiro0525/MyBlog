# 静态博客 + 在线编辑 可复现工作流

> 本文档是「纯静态博客（GitHub Pages）+ 浏览器在线编辑（Sveltia CMS）+ 对话上下文跳转 + ima 知识库收录」端到端流水线的运行手册。  
> 照着做即可从零复现，或在新项目里套用。  
> 配套 AI 技能：`sveltia-cms-github-pages`（已装在 user-level skills）。

---

## 0. 前置约束（务必先看，否则后面必踩坑）

| 约束                                  | 说明                                                                                       |
| ----------------------------------- | ---------------------------------------------------------------------------------------- |
| **仓库必须 public**                     | GitHub Pages 仅对 public 仓库免费；private 仓库 Pages 设置会被禁用                                      |
| **内容必须可公开**                         | 站点 + 对话源都会进公开仓库，含原始对话元数据                                                                 |
| **浏览器/预览可能禁 JS**                    | 所有交互必须纯静态 + 纯 CSS，JS 只做渐进增强                                                              |
| **fine-grained PAT 需 Workflows 权限** | 只给 contents 权限推 `.github/workflows/*.yml` 会 403                                          |
| **绝不用 Decap 默认 OAuth**              | Decap/Sveltia 的 "Log in with GitHub" 在 GitHub Pages 下走 Netlify 代理 → 404，必须用 **PAT 模式**登录 |
| **Sveltia 包名带 scope**               | CDN 是 `@sveltia/cms`，不是 `sveltia-cms`                                                    |

---

## 1. 准备 Markdown 源

目录结构（两层：`主题/子主题.md`）：

```
pkm_cards_v2/
  蓝图交互/射线检测与点击.md
  蓝图交互/属性查询系统.md
  GIS坐标/坐标转换.md
  Cpp工程/编译与调试.md
  ...
```

- 每张卡片在 `.md` 里以 `## 1. 问题标题` 起头，下面是回答
- 早期脚本可能生成三级冗余目录（`pkm_cards_v2/主题/子主题/卡片.md`），**不要混用**，`.gitignore` 排除之

---

## 2. 本地生成器 `build_blog.py`

职责：扫描 `pkm_cards_v2/` → 生成 `pkm_blog/index.html`（单文件）+ `pkm_blog/dialogue.html`（对话档案）。

### 2.1 核心特性（生成期静态写入，零运行时 JS 依赖）

1. **学霸笔记风 + 步骤分段**：识别 `1.` / `第一步：` / `方法A·B` / `节点N` 等 → 步骤块；行首角色标签（`[操作]`/`[观察]`/`[原因]`/`[结论]`…）→ 彩色小标签
2. **关键词荧光**：词表词 → `<mark class="kw">` 主题荧光；模式词（`EPSG:\d+`/`code:\d+`/`0x…`）→ `<mark class="err">` 红荧光
   - ⚠️ 词边界：全 ASCII 词必须加 `(?<![A-Za-z0-9_])(?![A-Za-z0-9_])` 边界，否则 `Pawn` 误命中 `Spawn`
3. **四套可切换配色**：CSS 变量 + 4 套 radio（学霸荧光默认 / 薄荷清新 / 黄昏暖读 / 深空夜读）
4. **右侧栏标签导航**：每张卡片算命中标签 slug → 写 `data-tags="ue5 射线检测 code:51"`；CSS `:has()` + radio 实现零 JS 筛选
   - 权重：`Q_WEIGHT=3`（问题优先）/`A_WEIGHT=1`（答案兜底），可改
   - 依赖 CSS `:has()`（Chrome/Edge 105+、Safari 15.4+、Firefox 121+），老浏览器降级为"无筛选"
5. **对话上下文跳转**：读 `conversation_*.json` + `conversation.md` → 生成 `dialogue.html`（消息折叠列表 + `msg-<id>` 锚点）；卡片底部加「💬 对话上下文」链接
   - 匹配：`问题文本前缀 30 字` 双源匹配，实测 99.7% 命中；未命中显示灰色"对话未收录"
   - ⚠️ `main()` 必须先做卡片→消息匹配、再渲染卡片 HTML

### 2.2 运行

```bash
python build_blog.py
# 产物：pkm_blog/index.html（≈3MB）、pkm_blog/dialogue.html（≈1.9MB）
```

本地预览：

```bash
cd pkm_blog && python -m http.server 8000 --bind 127.0.0.1
# 打开 http://127.0.0.1:8000/ 与 /dialogue.html
```

---

## 3. 建仓库 + `.gitignore`

GitHub 手动建 `<user>/<repo>`（**public**）。本地：

```bash
git init
git add build_blog.py pkm_cards_v2/<主题>/*.md   # 逐主题精确 add，避免误纳三级目录
git commit -m "init: 笔记库 + 生成器"
```

`.gitignore`：

```gitignore
pkm_blog/                                # 产物，不进仓（Actions 重建）
pkm_cards_v2/*/*/                        # 排除三级冗余目录
conversation*/                           # 排除其他会话产物
```

> ⚠️ 若启用了对话上下文功能，`conversation_*.json` / `conversation.md` 被上面的 `conversation*` 忽略，**必须**后续 `git add -f` 强制纳入（见 §6）。

---

## 4. Actions 工作流 `.github/workflows/build.yml`

```yaml
name: Build and Deploy Blog
on:
  push:
    branches: [main]
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
concurrency:
  group: pages
  cancel-in-progress: false
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: python build_blog.py
      - name: Assemble publish directory
        run: |
          mkdir -p _site
          cp -r pkm_blog/* _site/
          cp -r admin _site/admin
      - uses: actions/upload-pages-artifact@v3
        with: { path: _site }
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

要点：`checkout` → `setup-python` → `python build_blog.py` → 打包 `_site`（pkm_blog + admin）→ 上传 → 部署。

---

## 5. GitHub Pages 设置

- 仓库 **Settings → Pages → Source** 选 **GitHub Actions**
- **不要**点 "Configure with a custom domain" 旁的按钮（会覆盖我们的 `build.yml`）
- 勾选 **Enforce HTTPS**

---

## 6. Sveltia CMS 后台 `admin/`

### `admin/index.html`

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="robots" content="noindex" />
  <title>知识库 · 编辑后台</title>
</head>
<body>
  <script src="https://unpkg.com/@sveltia/cms@latest/dist/sveltia-cms.js"></script>
</body>
</html>
```

### `admin/config.yml`

```yaml
backend:
  name: github
  repo: <user>/<repo>
  branch: main

media_folder: "pkm_cards_v2/uploads"
public_folder: "/pkm_cards_v2/uploads"

collections:
  - name: "blueprint"
    label: "蓝图交互"
    folder: "pkm_cards_v2/蓝图交互"
    create: true
    slug: "{{slug}}"
    fields:
      - { name: body, label: "Markdown 内容", widget: "markdown" }
  # …每个主题一个 collection
```

> 只配 `backend`，**不要**加 `auth` / `client_id` / `scope`（对 GitHub Pages 场景无效）。  
> ⚠️ 若配置文件里登录说明写着 "Device Flow"，那是过时/错误的——以 **PAT 模式**登录为准（§7）。

---

## 7. 首次推送 + 登录

### 7.1 推送到 GitHub

创建 fine-grained PAT，勾选：

- `contents: Read and Write`
- `Workflows: Read and Write`（推工作流必需）

```bash
git remote add origin "https://<user>:<PAT>@github.com/<user>/<repo>.git"
# 若启用对话上下文，先把对话源强制纳入：
git add -f conversation_*.json conversation.md
git add .
git commit -m "feat: 博客 + 在线编辑 + 对话上下文"
git push origin main
git remote remove origin   # 推送完立刻清掉，避免 PAT 残留在 .git/config
```

### 7.2 登录后台

1. 等 Actions 跑完（约 1–2 分钟），确认 build + deploy 全绿
2. 访问 `https://<user>.github.io/<repo>/admin/`
3. **不要**点 "Log in with GitHub"（OAuth 跳 Netlify 会 404）
4. 点弹窗下方 **"Use a personal access token instead"**，粘贴 fine-grained PAT
5. 进后台 → 改任意 md → 保存 → 自动 commit → 自动触发构建 → 自动部署

---

## 8. 导入 ima 知识库（可选）

用已连通的 `ima-mcp` 连接器（自带鉴权，无需额外凭证）：

1. `get_knowledge_base_list`（type=KBT_MINE_KB）找到目标库，记下**数字 ID**（如 `7495025046853290`）
   > ⚠️ 这是 MCP 连接器的数字 ID，与 OpenAPI 长串 `kb_id` 是同一库不同表示，别混用（混用报 220001）
2. `import_urls`：
   ```json
   {
     "knowledge_base_id": "7495025046853290",
     "folder_id": "",
     "urls": [
       "https://<user>.github.io/<repo>/",
       "https://<user>.github.io/<repo>/admin/"
     ]
   }
   ```
   - `folder_id` 空 = 根目录；要放指定子文件夹先 `get_knowledge_list`（FOLDER 过滤）查 folder_id
3. 验证：`get_knowledge_list`（WEB 过滤）确认两条 `media_type: 2` 已入库
   - `admin/` 需 PAT 登录，ima 抓取得到登录页 → 仅存链接；主站为公开静态页可正常解析

---

## 9. 坑速查表

| # | 现象                        | 根因 / 解决                                                   |
| - | ------------------------- | --------------------------------------------------------- |
| 1 | 登录跳 `api.netlify.com` 404 | Decap/Sveltia 默认 OAuth 走 Netlify 代理 → 改用 **PAT 模式**       |
| 2 | 推工作流 403                  | PAT 缺 `Workflows: Read&Write`                             |
| 3 | Pages 设置被禁用               | 仓库是 private → 改 public                                    |
| 4 | Sveltia 脚本 404            | 包名应为 `@sveltia/cms` 不是 `sveltia-cms`                      |
| 5 | 全部卡片显示"对话未收录"             | 对话源被 `conversation*` 忽略 → `git add -f`；且 `main()` 须先匹配后渲染 |
| 6 | 标签筛选在老浏览器失效               | `:has()` 需 2022+ 浏览器，降级为无筛选                               |
| 7 | ima 报 220001              | 用了 OpenAPI 长串 kb_id，应改用 MCP 数字 ID                         |
| 8 | Pawn 误命中 Spawn            | 荧光词缺词边界，加前后非词字符断言                                         |

---

## 10. 复现清单（打勾即完成）

- [ ] 笔记按 `主题/子主题.md` 组织
- [ ] `build_blog.py` 生成 `index.html` + `dialogue.html`，本地预览正常
- [ ] GitHub 建 **public** 仓库
- [ ] `.gitignore` 排除产物/三级目录
- [ ] `.github/workflows/build.yml` 双 job 就位
- [ ] Pages Source = GitHub Actions，Enforce HTTPS 勾选
- [ ] `admin/index.html` + `admin/config.yml`（只 backend，无 auth）
- [ ] `git add -f` 对话源（若启用对话上下文）
- [ ] PAT（contents+Workflows）推送，`remote remove origin`
- [ ] Actions 绿，访问 `/admin/` 用 **PAT 模式**登录成功
- [ ] （可选）`import_urls` 把站点收录进 ima 知识库
