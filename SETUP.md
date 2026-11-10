# GitHub 个人主页发布步骤

GitHub 会在你的主页 `github.com/yanmingyu92` 顶部显示一个特殊仓库 `yanmingyu92/yanmingyu92` 里的 `README.md`。目前这个仓库还**不存在**，下面的步骤会创建它。

## 本文件夹内容

| 文件 | 作用 |
|---|---|
| `README.md` | 主页正文：neofetch 卡片、徽章、精选项目、论文、技术栈、贪吃蛇（可选） |
| `neofetch.json` | 卡片上显示的文字（职位、技能、联系方式），改这里即可 |
| `assets/portrait.jpg` | 证件照，脚本会把它转成彩色 ASCII 头像 |
| `scripts/generate_card.py` | 生成 `dist/neofetch-dark.svg` 和 `dist/neofetch-light.svg`（只依赖 Pillow） |
| `dist/*.svg` | 已生成的卡片（深色 / 浅色主题自动切换） |
| `.github/workflows/neofetch.yml` | 每周一自动刷新卡片里的 GitHub 统计；改 `neofetch.json` 后也会自动重画 |
| `.github/workflows/snake.yml` | 可选：贡献图贪吃蛇动画，发布到 `output` 分支 |
| `preview_card.html` | 本地预览用，不需要上传 |

## 1. 本地重新生成卡片（可选）

```bash
cd github_profile
```

```bash
pip install pillow
```

```bash
GITHUB_TOKEN=$(gh auth token) python scripts/generate_card.py
```

不联网时可以加 `--offline`，这样就不显示统计数据。

> 用你本人的 token 生成时，Contributions 数会包含私有仓库的贡献。Actions 里的 `GITHUB_TOKEN` 只能看到公开贡献，所以自动刷新后数字可能变小。不想显示这一项的话，把 `neofetch.json` → `stats.fields` 里的 `"contributions"` 删掉。

## 2. 创建主页仓库并推送

```bash
gh repo create yanmingyu92/yanmingyu92 --public --description "GitHub profile README"
```

```bash
cd github_profile && git init -b main && git add README.md SETUP.md neofetch.json assets scripts dist .github && git commit -m "feat: neofetch-style GitHub profile"
```

```bash
git remote add origin https://github.com/yanmingyu92/yanmingyu92.git && git push -u origin main
```

## 3. 启用 Actions

> **当前状态（2026-11-10）：** 仓库已创建并推送，但 GitHub 拒绝运行 Actions（"account is locked due to a billing issue"）。卡片 SVG 已提交在 `dist/`，主页正常显示，只是统计数字不会自动更新。两个工作流已暂停。在 **Settings → Billing and plans** 解决账单问题后，执行：
>
> ```bash
> gh workflow enable neofetch.yml -R yanmingyu92/yanmingyu92 && gh workflow run neofetch.yml -R yanmingyu92/yanmingyu92
> ```
>
> 想要贪吃蛇的话，同样启用并运行 `snake.yml`，再把 snake 的 `<picture>` 块加回 README（见 git 历史里第一次提交的版本）。

1. 打开仓库的 **Settings → Actions → General → Workflow permissions**，选 **Read and write permissions**。脚本需要提交刷新后的 SVG。
2. 打开 **Actions** 标签页，手动运行一次 **Refresh neofetch card**。
3. 如果要贪吃蛇：手动运行一次 **Contribution snake**，它会创建 `output` 分支。不要的话，删掉 `snake.yml` 和 README 里的 snake 块。

## 4. 建议同步更新的资料

- **Settings → Public profile**：Name 改成 `Jaime Yan, PhD`；Bio、Company `@Kardigan`、Location `Morristown, NJ`、Website `https://jaimeyan.com` 目前都是空的。
- **Pin** 6 个仓库：py4csr、shiny-gxp-governance、clinical-figure-library、clinical-r-in-practice、admiralagent、clinprog-bench。
- 清理公开仓库：`actions-probe-tmp`（描述是 "diag"）可以设为私有或删除；也可以给 `py4csr`、`usdm-toolkit`、`eSubmission-Benchmark`、`synethetic_data`、`gxp-sce` 补上描述。

## 备选方案：托管版 neofetch-profile

[jeantimex/neofetch-profile](https://github.com/jeantimex/neofetch-profile)（MIT）是一个部署在 Vercel 上的 Node 服务，会实时把头像转成 ASCII 并拉取统计数据。一行就能用：

```markdown
![Neofetch](https://neofetch-profile.vercel.app/api?username=yanmingyu92&theme=github-dark)
```

缺点：
- 依赖第三方服务的可用性和速率限制；
- 卡片布局固定为 38×25 的 ASCII 区；
- 只能用模板变量，不能写自定义字段。

所以这里改用自己生成的静态 SVG，外观风格一致，但没有外部依赖，文字完全可控。
