"""
Fruit Identifier — Streamlit version.

上传一张水果图,调 Claude vision 识别是什么水果。
"""

import base64
import io
import os

import anthropic
import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Fruit Identifier",
    page_icon="🍎",
    layout="centered",
)

# ──────────────────────────────────────────────────────────────────────
# API key: secrets > env > sidebar
# ──────────────────────────────────────────────────────────────────────
def _resolve_api_key() -> str | None:
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass
    return os.environ.get("ANTHROPIC_API_KEY") or None


API_KEY = _resolve_api_key()

with st.sidebar:
    st.header("Settings")
    if not API_KEY:
        API_KEY = st.text_input(
            "Anthropic API key",
            type="password",
            help="https://console.anthropic.com/settings/keys 申请",
        )
    else:
        st.success("Key 已加载(secrets / env)")

    model = st.selectbox(
        "Model",
        options=[
            "claude-haiku-4-5-20251001",
            "claude-sonnet-4-6",
            "claude-opus-4-7",
        ],
        index=0,
        help="Haiku 最快最便宜,够识别水果用。",
    )

    multi = st.toggle("多图模式", value=False, help="开启后可一次上传多张图")
    show_confidence = st.toggle("要 Claude 给置信度", value=True)


# ──────────────────────────────────────────────────────────────────────
# Page
# ──────────────────────────────────────────────────────────────────────
st.title("🍎 Fruit Identifier")
st.caption("Upload a fruit photo · powered by Claude vision")

if not API_KEY:
    st.warning("👈 在 sidebar 填一个 Anthropic key,或在 Streamlit Secrets 里设 `ANTHROPIC_API_KEY`。")
    st.stop()


# ──────────────────────────────────────────────────────────────────────
# Upload
# ──────────────────────────────────────────────────────────────────────
tab_upload, tab_camera = st.tabs(["🖼️ Upload", "📷 Camera"])

files: list = []
with tab_upload:
    if multi:
        ups = st.file_uploader(
            "Select images",
            type=["jpg", "jpeg", "png", "gif", "webp"],
            accept_multiple_files=True,
        )
        if ups:
            files.extend(ups)
    else:
        up = st.file_uploader(
            "Select an image",
            type=["jpg", "jpeg", "png", "gif", "webp"],
        )
        if up:
            files.append(up)

with tab_camera:
    cam = st.camera_input("Take a photo")
    if cam:
        files.append(cam)


# ──────────────────────────────────────────────────────────────────────
# Identify
# ──────────────────────────────────────────────────────────────────────
def identify(img_bytes: bytes, mime: str, key: str, model_id: str, want_conf: bool) -> str:
    client = anthropic.Anthropic(api_key=key)
    b64 = base64.standard_b64encode(img_bytes).decode("utf-8")
    instruction = (
        "What fruit is shown in this image? Reply with the fruit name only."
        if not want_conf
        else "What fruit is shown in this image? Reply in this format: "
             "`<fruit name> — <one-line note about variety/ripeness/confidence>`."
    )
    msg = client.messages.create(
        model=model_id,
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": mime, "data": b64}},
                {"type": "text", "text": instruction},
            ],
        }],
    )
    return msg.content[0].text.strip()


if files:
    st.markdown("---")
    if st.button("🚀 Identify", type="primary"):
        for idx, f in enumerate(files, start=1):
            with st.container(border=True):
                col_img, col_res = st.columns([1, 1])
                with col_img:
                    st.image(f, caption=getattr(f, "name", f"Image {idx}"), use_container_width=True)
                with col_res:
                    with st.spinner("Analyzing..."):
                        try:
                            data = f.getvalue()
                            mime = getattr(f, "type", None) or "image/jpeg"
                            # 把超大图缩到 1600px 上限,Claude vision 不需要那么大,省 token
                            img = Image.open(io.BytesIO(data))
                            if max(img.size) > 1600:
                                img.thumbnail((1600, 1600))
                                buf = io.BytesIO()
                                fmt = (img.format or "JPEG").upper()
                                if fmt == "JPEG":
                                    img = img.convert("RGB")
                                img.save(buf, format=fmt)
                                data = buf.getvalue()
                                mime = f"image/{fmt.lower()}"
                            result = identify(data, mime, API_KEY, model, show_confidence)
                            st.success(result)
                        except anthropic.AuthenticationError:
                            st.error("API key 无效。请到 sidebar 重新填。")
                        except anthropic.APIError as e:
                            st.error(f"Claude API 错误: {e}")
                        except Exception as e:
                            st.error(f"识别失败: {e}")
else:
    st.info("先上传一张图或者拍一张。")

st.markdown("---")
st.caption(
    "Tip: Claude vision 对常见水果识别很准,少见品种(比如热带水果不同变种)有可能出错。"
)
