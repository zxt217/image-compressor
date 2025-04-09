# 图片压缩工具

一个基于 Flask 的在线图片压缩工具，支持批量上传和处理。

## 功能特点

- 支持多图片批量上传
- 拖拽上传支持
- 可调节压缩质量
- 实时压缩进度显示
- 原图与压缩图对比预览
- 支持批量下载
- 自动清理过期文件

## 技术栈

- 后端：Flask
- 图片处理：Pillow
- 前端：Bootstrap 5
- 部署：Vercel

## 本地开发

1. 克隆仓库：
```bash
git clone https://github.com/your-username/image-compressor.git
cd image-compressor
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 运行应用：
```bash
python app.py
```

访问 http://localhost:5000 即可使用。

## 环境变量

- `SECRET_KEY`: 应用密钥
- `PORT`: 运行端口（默认 5000）
- `LOG_LEVEL`: 日志级别（默认 INFO）

## 部署到 Vercel

1. Fork 本仓库
2. 在 Vercel 中导入项目
3. 设置环境变量
4. 完成部署

## 注意事项

- 上传文件大小限制为 50MB
- 支持的图片格式：PNG、JPG、JPEG
- 压缩文件保留 7 天后自动清理
- 建议使用现代浏览器以获得最佳体验

## License

MIT
