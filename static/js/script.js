/**
 * 图片压缩工具 - 批量处理版本
 */

// DOM元素
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const qualitySlider = document.getElementById('quality-slider');
const qualityValue = document.getElementById('quality-value');
const compressButton = document.getElementById('compress-button');
const addMoreButton = document.getElementById('add-more-button');
const resultContainer = document.getElementById('result-container');
const imageQueueContainer = document.getElementById('image-queue-container');
const imageQueue = document.getElementById('image-queue');
const queueCount = document.getElementById('queue-count');
const resultsGrid = document.getElementById('results-grid');
const selectAllButton = document.getElementById('select-all-button');
const selectNoneButton = document.getElementById('select-none-button');
const downloadSelectedButton = document.getElementById('download-selected-button');
const newBatchButton = document.getElementById('new-batch-button');
const loader = document.getElementById('loader');
const processingStatus = document.getElementById('processing-status');

// 全局变量
let selectedFiles = [];
let compressedResults = [];
const MAX_FILES = 10;

// 事件监听器
document.addEventListener('DOMContentLoaded', () => {
    console.log('页面加载完成');
    
    // 确保所有DOM元素已加载
    if (!uploadArea) console.error('无法找到上传区域元素');
    if (!fileInput) console.error('无法找到文件输入元素');
    if (!compressButton) console.error('无法找到压缩按钮元素');
    
    // 上传区域点击事件
    uploadArea.addEventListener('click', () => {
        console.log('点击上传区域');
        fileInput.click();
    });

    // 文件选择事件
    fileInput.addEventListener('change', (event) => {
        console.log('选择文件变更');
        handleFilesSelect(event);
    });

    // 拖放事件
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);

    // 压缩质量滑块事件
    qualitySlider.addEventListener('input', updateQualityValue);

    // 压缩按钮事件
    compressButton.addEventListener('click', () => {
        console.log('点击压缩按钮');
        compressImages();
    });
    
    // 添加更多图片按钮事件
    addMoreButton.addEventListener('click', () => {
        console.log('点击添加更多图片按钮');
        fileInput.click();
    });

    // 全选按钮事件
    selectAllButton.addEventListener('click', selectAllImages);

    // 取消全选按钮事件
    selectNoneButton.addEventListener('click', deselectAllImages);
    
    // 下载选中按钮事件
    downloadSelectedButton.addEventListener('click', downloadSelectedImages);

    // 新批次按钮事件
    newBatchButton.addEventListener('click', resetUI);
});

/**
 * 处理多文件选择
 * @param {Event} event - 文件选择事件
 */
function handleFilesSelect(event) {
    const files = event.target.files;
    console.log('处理文件选择:', files ? files.length : 0, '个文件');
    
    if (!files || files.length === 0) return;
    
    addFilesToQueue(files);
}

/**
 * 添加文件到队列
 * @param {FileList} files - 文件列表
 */
function addFilesToQueue(files) {
    // 检查文件数量限制
    if (selectedFiles.length + files.length > MAX_FILES) {
        alert(`最多只能上传${MAX_FILES}张图片，请减少选择数量`);
        return;
    }
    
    // 添加文件到选择列表
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        if (isValidFile(file)) {
            selectedFiles.push(file);
            addFileToQueueUI(file);
        }
    }
    
    // 更新UI
    updateQueueCount();
    compressButton.disabled = selectedFiles.length === 0;
    
    // 显示队列容器
    if (selectedFiles.length > 0) {
        imageQueueContainer.classList.remove('hidden');
        addMoreButton.classList.remove('hidden');
    }
}

/**
 * 将文件添加到队列UI
 * @param {File} file - 文件对象
 */
function addFileToQueueUI(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const queueItem = document.createElement('div');
        queueItem.className = 'queue-item';
        queueItem.dataset.filename = file.name;
        
        queueItem.innerHTML = `
            <img src="${e.target.result}" alt="${file.name}">
            <button class="remove-btn" title="移除">×</button>
            <div class="file-info">${file.name.length > 15 ? file.name.substring(0, 12) + '...' : file.name}</div>
        `;
        
        // 添加删除按钮事件
        queueItem.querySelector('.remove-btn').addEventListener('click', (event) => {
            event.stopPropagation();
            removeFileFromQueue(file.name);
        });
        
        imageQueue.appendChild(queueItem);
    };
    reader.readAsDataURL(file);
}

/**
 * 从队列中移除文件
 * @param {string} filename - 文件名
 */
function removeFileFromQueue(filename) {
    // 从数组中移除
    selectedFiles = selectedFiles.filter(file => file.name !== filename);
    
    // 从UI中移除
    const queueItem = imageQueue.querySelector(`.queue-item[data-filename="${filename}"]`);
    if (queueItem) {
        queueItem.remove();
    }
    
    // 更新UI状态
    updateQueueCount();
    compressButton.disabled = selectedFiles.length === 0;
    
    // 如果没有文件，隐藏队列容器
    if (selectedFiles.length === 0) {
        imageQueueContainer.classList.add('hidden');
        addMoreButton.classList.add('hidden');
    }
}

/**
 * 更新队列计数
 */
function updateQueueCount() {
    queueCount.textContent = selectedFiles.length;
}

/**
 * 处理拖拽经过事件
 * @param {Event} event - 拖拽经过事件
 */
function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    uploadArea.classList.add('dragover');
}

/**
 * 处理拖拽离开事件
 * @param {Event} event - 拖拽离开事件
 */
function handleDragLeave(event) {
    event.preventDefault();
    event.stopPropagation();
    uploadArea.classList.remove('dragover');
}

/**
 * 处理拖放事件
 * @param {Event} event - 拖放事件
 */
function handleDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    uploadArea.classList.remove('dragover');
    
    console.log('处理文件拖放');
    const files = event.dataTransfer.files;
    if (files && files.length > 0) {
        addFilesToQueue(files);
    }
}

/**
 * 验证文件类型
 * @param {File} file - 要验证的文件
 * @returns {boolean} 如果文件类型有效返回true
 */
function isValidFile(file) {
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg'];
    console.log('验证文件类型:', file.type);
    
    if (!validTypes.includes(file.type)) {
        console.error('文件类型无效:', file.type);
        alert(`文件 "${file.name}" 不是支持的格式，请上传PNG或JPG格式图片`);
        return false;
    }
    return true;
}

/**
 * 更新质量值显示
 */
function updateQualityValue() {
    qualityValue.textContent = `${qualitySlider.value}%`;
}

/**
 * 压缩所有图片
 */
function compressImages() {
    if (selectedFiles.length === 0) {
        console.error('没有选择文件');
        return;
    }
    
    console.log('开始压缩图片，共', selectedFiles.length, '张');
    console.log('压缩质量:', qualitySlider.value);
    
    // 显示加载动画
    loader.classList.remove('hidden');
    processingStatus.textContent = `0/${selectedFiles.length}`;
    
    // 创建表单数据
    const formData = new FormData();
    selectedFiles.forEach(file => {
        formData.append('files[]', file);
    });
    formData.append('quality', qualitySlider.value);
    
    console.log('发送批量请求到服务器');
    
    // 发送请求
    fetch('/batch-upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        console.log('收到服务器响应:', response.status);
        if (!response.ok) {
            return response.json().then(data => {
                console.error('服务器错误:', data);
                throw new Error(data.error || '上传失败');
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('响应数据:', data);
        if (data.success) {
            // 保存结果
            compressedResults = data.results;
            
            // 显示结果
            displayResults(data.results, data.errors);
            
            // 显示结果区域
            resultContainer.classList.remove('hidden');
            
            // 隐藏上传区域和队列
            document.querySelector('.upload-container').classList.add('hidden');
        } else {
            throw new Error(data.errors.join(', ') || '压缩失败');
        }
    })
    .catch(error => {
        console.error('请求错误:', error);
        alert(`错误: ${error.message}`);
        compressButton.disabled = false;
    })
    .finally(() => {
        // 隐藏加载动画
        loader.classList.add('hidden');
        console.log('请求处理完成');
    });
}

/**
 * 显示压缩结果
 * @param {Array} results - 压缩结果数组
 * @param {Array} errors - 错误信息数组
 */
function displayResults(results, errors) {
    // 清空结果网格
    resultsGrid.innerHTML = '';
    
    // 添加结果卡片
    results.forEach(result => {
        const resultCard = document.createElement('div');
        resultCard.className = 'result-card';
        resultCard.dataset.filename = result.filename;
        
        resultCard.innerHTML = `
            <div class="result-card-header">
                <div class="result-card-title" title="${result.original_filename}">${result.original_filename}</div>
                <input type="checkbox" class="result-checkbox" data-filename="${result.filename}">
            </div>
            <div class="comparison-container">
                <div class="image-preview-small">
                    <img src="${result.compressed_image}" alt="压缩后">
                </div>
                <div class="size-comparison">
                    <span>原始: ${result.original_size}</span>
                    <span>压缩: ${result.compressed_size}</span>
                </div>
                <div class="compression-percent">节省 ${result.compression_percent}%</div>
            </div>
            <button class="button-primary download-button" data-filename="${result.filename}">下载</button>
        `;
        
        // 添加单个下载按钮事件
        resultCard.querySelector('.download-button').addEventListener('click', (e) => {
            e.preventDefault();
            downloadSingleImage(result.filename);
        });
        
        // 添加复选框点击事件
        resultCard.querySelector('.result-checkbox').addEventListener('change', (e) => {
            updateSelectedCount();
        });
        
        resultsGrid.appendChild(resultCard);
    });
    
    // 如果有错误信息，显示警告
    if (errors && errors.length > 0) {
        const errorMessage = document.createElement('div');
        errorMessage.className = 'error-message';
        errorMessage.textContent = `处理过程中有 ${errors.length} 个错误: ${errors.join('; ')}`;
        resultsGrid.prepend(errorMessage);
    }
    
    // 初始化下载按钮状态
    updateSelectedCount();
}

/**
 * 更新选中图片计数并更新下载按钮状态
 */
function updateSelectedCount() {
    const checkboxes = document.querySelectorAll('.result-checkbox');
    const checkedCount = Array.from(checkboxes).filter(cb => cb.checked).length;
    
    // 更新下载按钮状态
    downloadSelectedButton.disabled = checkedCount === 0;
    downloadSelectedButton.textContent = `下载所选图片 (${checkedCount})`;
}

/**
 * 全选所有图片
 */
function selectAllImages() {
    const checkboxes = document.querySelectorAll('.result-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = true;
    });
    updateSelectedCount();
}

/**
 * 取消全选
 */
function deselectAllImages() {
    const checkboxes = document.querySelectorAll('.result-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
    });
    updateSelectedCount();
}

/**
 * 下载单个图片
 * @param {string} filename - 文件名
 */
function downloadSingleImage(filename) {
    window.location.href = `/download/${filename}`;
}

/**
 * 下载所有选中的图片
 */
function downloadSelectedImages() {
    const checkboxes = document.querySelectorAll('.result-checkbox:checked');
    if (checkboxes.length === 0) {
        alert('请至少选择一张图片');
        return;
    }
    
    // 获取所有选中的文件名
    const filenames = Array.from(checkboxes).map(cb => cb.dataset.filename);
    
    // 显示加载动画
    loader.classList.remove('hidden');
    processingStatus.textContent = `正在准备下载...`;
    
    // 发送下载请求
    fetch('/download-batch', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ filenames })
    })
    .then(response => {
        if (!response.ok) {
            // 隐藏加载动画
            loader.classList.add('hidden');
            return response.json().then(data => {
                throw new Error(data.error || '下载失败');
            });
        }
        
        // 返回响应的blob数据流（不是对blob的promise）
        return response.blob();
    })
    .then(blobData => {
        // 隐藏加载动画
        loader.classList.add('hidden');
        
        // 创建Blob URL并触发下载
        const url = window.URL.createObjectURL(blobData);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'compressed_images.zip';
        document.body.appendChild(a);
        a.click();
        
        // 释放URL对象
        setTimeout(() => {
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        }, 100);
    })
    .catch(error => {
        console.error('下载请求错误:', error);
        alert(`错误: ${error.message}`);
        loader.classList.add('hidden');
    });
}

/**
 * 重置UI以处理新批次图片
 */
function resetUI() {
    console.log('重置UI');
    
    // 重置文件输入和选择
    fileInput.value = '';
    selectedFiles = [];
    compressedResults = [];
    
    // 清空图片队列
    imageQueue.innerHTML = '';
    
    // 重置UI状态
    compressButton.disabled = true;
    addMoreButton.classList.add('hidden');
    imageQueueContainer.classList.add('hidden');
    resultContainer.classList.add('hidden');
    document.querySelector('.upload-container').classList.remove('hidden');
    
    // 更新计数
    updateQueueCount();
} 