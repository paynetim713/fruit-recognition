from flask import Flask, render_template_string, request, jsonify
import anthropic
import base64
import os
from PIL import Image
import io

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fruit Identifier</title>
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif; background: #fafafa; color: #1a1a1a; line-height: 1.6; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .container { max-width: 480px; width: 100%; padding: 60px 40px; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center; }
        h1 { font-size: 24px; font-weight: 600; color: #2d2d2d; margin-bottom: 8px; }
        .subtitle { font-size: 15px; color: #666; margin-bottom: 40px; }
        .upload-area { border: 2px dashed #e0e0e0; border-radius: 8px; padding: 40px 20px; margin: 30px 0; cursor: pointer; transition: all 0.3s; }
        .upload-area:hover { border-color: #007aff; background: #f0f7ff; }
        input[type="file"] { display: none; }
        #preview { max-width: 280px; max-height: 280px; border-radius: 8px; margin: 20px 0; display: none; }
        .result { margin-top: 20px; padding: 18px; border-radius: 8px; font-size: 15px; font-weight: 500; }
        .result.success { background: #f0f9f0; color: #2d5a2d; border: 1px solid #e8f5e8; }
        .result.error { background: #fef5f5; color: #c53030; border: 1px solid #fed7d7; }
        .result.loading { background: #f8f9fa; color: #666; }
        .btn { margin-top: 16px; padding: 12px 28px; background: #007aff; color: white; border: none; border-radius: 6px; font-size: 14px; font-weight: 500; cursor: pointer; }
        .btn:hover { background: #0056cc; }
    </style>
</head>
<body>
<div class="container">
    <h1>🍎 Fruit Identifier</h1>
    <p class="subtitle">Upload an image to identify the fruit using AI</p>
    <div class="upload-area" onclick="document.getElementById('imageInput').click()">
        <input type="file" id="imageInput" accept="image/*" onchange="identify()">
        <img id="preview" alt="preview">
        <div id="uploadText">
            <div style="font-size:16px;color:#666;margin-bottom:8px">Click to select an image</div>
            <div style="font-size:13px;color:#999">JPEG, PNG, GIF, WEBP — max 16MB</div>
        </div>
    </div>
    <div id="result"></div>
</div>
<script>
function identify() {
    const file = document.getElementById("imageInput").files[0];
    if (!file) return;
    const preview = document.getElementById("preview");
    const reader = new FileReader();
    reader.onload = e => { preview.src = e.target.result; preview.style.display = "block"; document.getElementById("uploadText").style.display = "none"; };
    reader.readAsDataURL(file);
    document.getElementById("result").innerHTML = "<div class=\\"result loading\\">Analyzing<span id=\\"dots\\">...</span></div>";
    const form = new FormData();
    form.append("image", file);
    fetch("/identify", { method: "POST", body: form })
        .then(r => r.json())
        .then(data => {
            if (data.success) document.getElementById("result").innerHTML = `<div class="result success">🍓 This is: <strong>${data.result}</strong></div>`;
            else document.getElementById("result").innerHTML = `<div class="result error">⚠️ ${data.error}</div>`;
        })
        .catch(() => { document.getElementById("result").innerHTML = "<div class=\\"result error\\">Network error</div>"; });
}
</script>
</body>
</html>'''

def encode_image_to_base64(image_data):
    return base64.b64encode(image_data).decode('utf-8')

def get_image_media_type(image_format):
    format_map = { 'JPEG': 'image/jpeg', 'PNG': 'image/png', 'GIF': 'image/gif', 'WEBP': 'image/webp' }
    return format_map.get(image_format.upper(), 'image/jpeg')

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/identify', methods=['POST'])
def identify_fruit():
    if 'image' not in request.files:
        return jsonify({"success": False, "error": "No image selected"})
    file = request.files['image']
    if file.filename == '':
        return jsonify({"success": False, "error": "No image selected"})
    try:
        image_data = file.read()
        image = Image.open(io.BytesIO(image_data))
        media_type = get_image_media_type(image.format)
        image_base64 = encode_image_to_base64(image_data)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_base64}},
                {"type": "text", "text": "What fruit is this? Just tell me the name of the fruit, nothing else."}
            ]}]
        )
        return jsonify({"success": True, "result": response.content[0].text.strip()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(debug=False)
