# 图片压缩工具

一个具有苹果风格设计的网页应用，用于压缩PNG和JPG图片，减小文件大小。

## 功能

- 上传PNG、JPG格式图片
- 可调节压缩比例
- 实时预览原图和压缩后的图片
- 显示压缩前后的文件大小
- 下载压缩后的图片

## 项目结构

```
image_compressor/
├── api/               # Vercel部署相关
│   └── index.py       # Vercel入口文件
├── app.py             # Flask应用主文件
├── static/            # 静态资源
│   ├── css/           # 样式文件
│   │   └── styles.css # 主样式表
│   ├── js/            # JavaScript文件
│   │   └── script.js  # 主脚本
│   └── uploads/       # 上传的图片存储目录
├── templates/         # HTML模板
│   └── index.html     # 主页面
├── requirements.txt   # 项目依赖
└── vercel.json        # Vercel配置文件
```

## 本地安装与使用

1. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

2. 运行应用：
   ```
   python app.py
   ```

3. 在浏览器中访问：
   ```
   http://localhost:5000
   ```

## 部署到Vercel

### 前提条件

- [Vercel账号](https://vercel.com/signup)
- [Git](https://git-scm.com/downloads)
- [Vercel CLI](https://vercel.com/cli) (可选)

### 部署步骤

1. 将项目推送到GitHub、GitLab或Bitbucket仓库

2. 使用Vercel CLI部署（方法一）：
   ```
   # 安装Vercel CLI
   npm i -g vercel

   # 部署
   vercel
   ```

3. 通过Vercel网站部署（方法二）：
   - 登录[Vercel](https://vercel.com/)
   - 点击"New Project"
   - 导入你的Git仓库
   - 选择项目
   - 点击"Deploy"

### 注意事项

- Vercel上的文件系统是临时的，所有上传的图片会在重新部署后丢失
- 对于生产环境，建议使用如[Vercel Blob Storage](https://vercel.com/docs/storage/vercel-blob)、AWS S3或其他云存储服务来存储图片 