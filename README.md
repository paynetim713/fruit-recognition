# Fruit Identifier

上传一张水果照片,Claude vision 识别是什么水果。两个版本:

- **`streamlit_app.py`** — Streamlit 版,可一键部署到 Streamlit Cloud。带多图模式、相机拍照、模型选择(Haiku/Sonnet/Opus)、大图自动缩放省 token。**推荐用这个。**
- **`app.py`** — 原始 Flask 版,纯前后端分离。

写这个项目最初是想玩一下 Claude vision API,挑了个最简单的"分类"场景练手。

## Streamlit 版本(推荐)

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

打开 `http://localhost:8501`,sidebar 填一个 Anthropic key 就能跑。

部署到 Streamlit Cloud:

1. push 到 GitHub
2. https://share.streamlit.io/ → New app → 选这个 repo
3. Main file path: `streamlit_app.py`
4. 部署后进 app Settings → Secrets,加一行 `ANTHROPIC_API_KEY = "sk-ant-..."`

## Flask 版本(原版)

```bash
export ANTHROPIC_API_KEY=你的key
python app.py
```

打开 `http://localhost:5000`,支持多图拖拽上传,最大 16MB/张。

部署:

```
web: gunicorn app:app
```

Heroku / Railway / Render 都行,环境变量设 `ANTHROPIC_API_KEY`。

## 一些细节

- key 在 https://console.anthropic.com/settings/keys 申请
- 图片在内存里转 base64 发给 Claude,不落盘
- Streamlit 版会把超过 1600px 的图自动缩放,省 token
- 后端不存历史记录——每张图识别完就丢了

## 协议

MIT。
