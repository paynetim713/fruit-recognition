# Fruit Identifier

上传一张水果照片，调 Claude 的 vision 模型识别是什么水果。Flask + 单页前端。

写这个是因为想玩一下 Claude vision API，找了个最简单的"分类"场景练手。

## 跑起来

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=你的key
python app.py
```

key 在 https://console.anthropic.com/settings/keys 申请。

打开 `http://localhost:5000`，点一下上传图片就行。支持 JPEG / PNG / GIF / WEBP，最大 16MB。

## 部署

```
web: gunicorn app:app
```

Heroku / Railway / Render 都能直接跑，记得把 `ANTHROPIC_API_KEY` 写到环境变量。

## 一些细节

- 图片在内存里转成 base64 发给 Claude，不落盘。
- 后端不存历史记录——每张图识别完就丢了。如果想做个相册功能要加数据库。
- 只识别"是什么水果"，没做营养分析、产地推荐这些扩展。

## 协议

MIT。
