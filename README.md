# view-html

阅读报告 / HTML report 的 GitHub Pages 托管仓库。

- 每份报告是 `reports/<报告名>/` 下的一个**自包含文件夹**（入口为 `index.html`）。
- 根目录 `index.html` 是自动生成的导航首页，由 `build_index.py` 扫描 `reports/` 重建——**不要手改**。
- 通过 `/view-html` skill 一键部署：在某份报告文件夹里运行，它会把文件夹同步进 `reports/`、重建索引、push。

## 访问地址

- 首页：https://a1henu.github.io/view-html/
- 单份报告：https://a1henu.github.io/view-html/reports/<报告名>/

## 手动重建索引

```bash
python3 build_index.py && git add -A && git commit -m "rebuild index" && git push
```
