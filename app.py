#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图片压缩工具 - Flask应用主文件
"""

import os
import uuid
import logging
import json
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from PIL import Image
from io import BytesIO
import zipfile

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'static/uploads')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB最大上传限制

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 允许的文件类型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """
    检查文件扩展名是否被允许
    
    Args:
        filename: 要检查的文件名
        
    Returns:
        bool: 如果文件扩展名被允许，返回True
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size(file_path):
    """
    获取文件大小
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 格式化的文件大小（KB）
    """
    size_in_bytes = os.path.getsize(file_path)
    size_in_kb = size_in_bytes / 1024
    return f"{size_in_kb:.2f} KB"

def get_file_size_bytes(file_path):
    """
    获取文件大小（字节）
    
    Args:
        file_path: 文件路径
        
    Returns:
        int: 文件大小（字节）
    """
    return os.path.getsize(file_path)

def compress_image(input_path, output_path, quality):
    """
    压缩图片
    
    Args:
        input_path: 输入图片路径
        output_path: 输出图片路径
        quality: 压缩质量（1-100）
        
    Returns:
        tuple: (压缩前大小, 压缩后大小, 压缩百分比)
    """
    # 打开图片
    img = Image.open(input_path)
    
    # 保存压缩后的图片
    img.save(output_path, optimize=True, quality=quality)
    
    # 获取压缩前后的文件大小
    original_size = get_file_size(input_path)
    compressed_size = get_file_size(output_path)
    
    # 计算压缩百分比
    original_bytes = get_file_size_bytes(input_path)
    compressed_bytes = get_file_size_bytes(output_path)
    compression_percent = round((1 - (compressed_bytes / original_bytes)) * 100)
    
    return original_size, compressed_size, compression_percent

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
    
    quality = int(request.form.get('quality', 80))
    logger.debug(f"压缩质量: {quality}")
    
    if file.filename == '':
        logger.error("文件名为空")
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        # 生成唯一文件名
        original_filename = str(uuid.uuid4())
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{original_filename}.{file_ext}")
        compressed_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{original_filename}_compressed.{file_ext}")
        
        logger.debug(f"原始路径: {original_path}")
        logger.debug(f"压缩后路径: {compressed_path}")
        
        # 保存原始文件
        file.save(original_path)
        logger.debug("原始文件已保存")
        
        try:
            # 压缩图片
            original_size, compressed_size, compression_percent = compress_image(original_path, compressed_path, quality)
            logger.debug(f"压缩成功: 原始大小 {original_size}, 压缩后大小 {compressed_size}, 压缩率 {compression_percent}%")
            
            return jsonify({
                'success': True,
                'original_filename': file.filename,
                'original_image': f"/static/uploads/{original_filename}.{file_ext}",
                'compressed_image': f"/static/uploads/{original_filename}_compressed.{file_ext}",
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_percent': compression_percent,
                'filename': f"{original_filename}_compressed.{file_ext}"
            })
        except Exception as e:
            logger.error(f"压缩过程中出错: {str(e)}")
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
    
    quality = int(request.form.get('quality', 80))
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
            original_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{original_filename}.{file_ext}")
            compressed_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{original_filename}_compressed.{file_ext}")
            
            # 保存原始文件
            file.save(original_path)
            
            # 压缩图片
            original_size, compressed_size, compression_percent = compress_image(original_path, compressed_path, quality)
            
            results.append({
                'original_filename': file.filename,
                'original_image': f"/static/uploads/{original_filename}.{file_ext}",
                'compressed_image': f"/static/uploads/{original_filename}_compressed.{file_ext}",
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_percent': compression_percent,
                'filename': f"{original_filename}_compressed.{file_ext}"
            })
            
        except Exception as e:
            logger.error(f"处理文件 {file.filename} 时出错: {str(e)}")
            errors.append(f"处理文件 {file.filename} 时出错: {str(e)}")
    
    return jsonify({
        'success': len(results) > 0,
        'results': results,
        'errors': errors
    })

@app.route('/download/<filename>')
def download_file(filename):
    """下载单个压缩后的图片"""
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], path=filename, as_attachment=True)

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
            for i, filename in enumerate(filenames):
                # 安全检查，确保文件在上传目录中
                if '..' in filename or filename.startswith('/'):
                    logger.warning(f"跳过不安全的文件路径: {filename}")
                    continue
                
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(file_path):
                    # 获取原始文件名（去掉UUID部分）
                    if '_compressed.' in filename:
                        original_filename = filename.split('_compressed.')[-1]
                    else:
                        original_filename = filename
                        
                    # 如果有多个同名文件，添加数字后缀
                    if filenames.count(filename) > 1:
                        base_name, ext = original_filename.rsplit('.', 1)
                        original_filename = f"{base_name}_{i+1}.{ext}"
                    
                    zf.write(file_path, arcname=original_filename)
                    files_added += 1
                    logger.debug(f"添加文件到压缩包: {filename} -> {original_filename}")
                else:
                    logger.warning(f"文件不存在: {file_path}")
                    
        if files_added == 0:
            return jsonify({'error': '所选文件均不存在或无效'}), 404
            
        # 设置文件指针到文件开头
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