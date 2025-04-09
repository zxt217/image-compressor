#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图片压缩工具 - Flask应用主文件
"""

import os
import sys
import uuid
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from PIL import Image
from io import BytesIO
import zipfile
import config

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    stream=sys.stdout  # 输出到控制台
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
app.config['SECRET_KEY'] = config.SECRET_KEY

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """检查文件扩展名是否被允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

def get_file_size(file_path):
    """获取文件大小（带单位）"""
    size_bytes = os.path.getsize(file_path)
    for unit in ['B', 'KB', 'MB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}GB"

def compress_image(file, quality=None):
    """
    压缩图片（直接处理内存中的图片）
    
    Args:
        file: 文件对象
        quality: 压缩质量 (1-100)，None 时使用默认值
    
    Returns:
        BytesIO: 压缩后的图片数据
    """
    if quality is None:
        quality = config.DEFAULT_QUALITY
    quality = max(config.MIN_QUALITY, min(config.MAX_QUALITY, quality))
    
    # 读取原始图片
    img = Image.open(file)
    
    # 调整图片尺寸
    if img.width > config.MAX_WIDTH or img.height > config.MAX_HEIGHT:
        ratio = min(config.MAX_WIDTH/img.width, config.MAX_HEIGHT/img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    # 压缩到内存
    output = BytesIO()
    img.save(output, format=img.format or 'JPEG', quality=quality, optimize=True)
    output.seek(0)
    return output

@app.route('/')
def index():
    """渲染主页"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """处理单张图片上传和压缩"""
    logger.debug("收到上传请求")
    
    if 'file' not in request.files:
        logger.error("没有文件字段在请求中")
        return jsonify({'error': '没有选择文件'}), 400
    
    file = request.files['file']
    logger.debug(f"文件名: {file.filename}")
    
    quality = int(request.form.get('quality', config.DEFAULT_QUALITY))
    logger.debug(f"压缩质量: {quality}")
    
    if file.filename == '':
        logger.error("文件名为空")
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # 生成唯一文件名
            original_filename = str(uuid.uuid4())
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            
            # 压缩图片
            compressed_data = compress_image(file, quality)
            
            # 计算原始大小
            file.seek(0, 2)  # 移动到文件末尾
            original_size = file.tell()
            file.seek(0)  # 重置文件指针
            
            # 计算压缩后大小
            compressed_size = compressed_data.getbuffer().nbytes
            
            # 保存到临时目录
            compressed_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{original_filename}_compressed.{file_ext}")
            with open(compressed_path, 'wb') as f:
                f.write(compressed_data.getvalue())
            
            return jsonify({
                'success': True,
                'original_filename': file.filename,
                'compressed_image': f"/download/{original_filename}_compressed.{file_ext}",
                'original_size': f"{original_size/1024:.1f}KB",
                'compressed_size': f"{compressed_size/1024:.1f}KB",
                'compression_ratio': f"{(1 - compressed_size/original_size) * 100:.1f}%",
                'filename': f"{original_filename}_compressed.{file_ext}"
            })
            
        except Exception as e:
            logger.error(f"压缩过程中出错: {str(e)}", exc_info=True)
            return jsonify({'error': f'压缩过程中出错: {str(e)}'}), 500
    
    logger.error("不支持的文件类型")
    return jsonify({'error': '不支持的文件类型，请上传PNG或JPG格式图片'}), 400

@app.route('/batch-upload', methods=['POST'])
def batch_upload():
    """处理批量图片上传和压缩"""
    logger.debug("收到批量上传请求")
    
    if 'files[]' not in request.files:
        logger.error("没有文件字段在请求中")
        return jsonify({'error': '没有选择文件'}), 400
    
    files = request.files.getlist('files[]')
    logger.debug(f"文件数量: {len(files)}")
    
    quality = int(request.form.get('quality', config.DEFAULT_QUALITY))
    logger.debug(f"压缩质量: {quality}")
    
    if not files or len(files) == 0:
        logger.error("文件列表为空")
        return jsonify({'error': '没有选择文件'}), 400
    
    results = []
    errors = []
    
    for file in files:
        if file.filename == '':
            continue
        
        if not allowed_file(file.filename):
            errors.append(f"文件 {file.filename} 不是支持的格式")
            continue
        
        try:
            # 生成唯一文件名
            original_filename = str(uuid.uuid4())
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            
            # 压缩图片
            compressed_data = compress_image(file, quality)
            
            # 计算原始大小
            file.seek(0, 2)
            original_size = file.tell()
            file.seek(0)
            
            # 计算压缩后大小
            compressed_size = compressed_data.getbuffer().nbytes
            
            # 保存到临时目录
            compressed_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{original_filename}_compressed.{file_ext}")
            with open(compressed_path, 'wb') as f:
                f.write(compressed_data.getvalue())
            
            results.append({
                'original_filename': file.filename,
                'compressed_image': f"/download/{original_filename}_compressed.{file_ext}",
                'original_size': f"{original_size/1024:.1f}KB",
                'compressed_size': f"{compressed_size/1024:.1f}KB",
                'compression_ratio': f"{(1 - compressed_size/original_size) * 100:.1f}%",
                'filename': f"{original_filename}_compressed.{file_ext}"
            })
            
        except Exception as e:
            logger.error(f"处理文件 {file.filename} 时出错: {str(e)}", exc_info=True)
            errors.append(f"处理文件 {file.filename} 时出错: {str(e)}")
    
    return jsonify({
        'success': len(results) > 0,
        'results': results,
        'errors': errors
    })

@app.route('/download/<filename>')
def download_file(filename):
    """下载压缩后的图片"""
    try:
        return send_from_directory(
            directory=app.config['UPLOAD_FOLDER'],
            path=filename,
            as_attachment=True
        )
    except Exception as e:
        logger.error(f"下载文件时出错: {str(e)}", exc_info=True)
        return jsonify({'error': '文件不存在或已过期'}), 404

@app.route('/download-batch', methods=['POST'])
def download_batch():
    """打包下载多个压缩图片"""
    try:
        data = request.get_json()
        if not data or 'filenames' not in data or not data['filenames']:
            return jsonify({'error': '未选择任何文件'}), 400
        
        filenames = data['filenames']
        logger.debug(f"批量下载请求: {len(filenames)} 个文件")
        
        # 创建一个内存中的zip文件
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            files_added = 0
            for filename in filenames:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(file_path):
                    zf.write(file_path, filename)
                    files_added += 1
                    logger.debug(f"添加文件到压缩包: {filename}")
                else:
                    logger.warning(f"文件不存在: {file_path}")
        
        if files_added == 0:
            return jsonify({'error': '所选文件均不存在或已过期'}), 404
        
        # 设置文件指针到开头
        memory_file.seek(0)
        
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name='compressed_images.zip'
        )
        
    except Exception as e:
        logger.error(f"创建压缩包时出错: {str(e)}", exc_info=True)
        return jsonify({'error': f'下载过程中出错: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False) 