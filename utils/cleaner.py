"""
文件清理模块
"""
import os
import time
import logging
from datetime import datetime
from threading import Thread, Event
import config

logger = logging.getLogger(__name__)

class FileCleaner:
    """文件清理器，用于定期清理过期的上传文件"""
    
    def __init__(self):
        self._stop_event = Event()
        self._thread = None
        
    def start(self):
        """启动清理线程"""
        if self._thread is not None:
            return
            
        self._stop_event.clear()
        self._thread = Thread(target=self._cleanup_loop, daemon=True)
        self._thread.start()
        logger.info("文件清理器已启动")
        
    def stop(self):
        """停止清理线程"""
        if self._thread is None:
            return
            
        self._stop_event.set()
        self._thread.join()
        self._thread = None
        logger.info("文件清理器已停止")
        
    def _cleanup_loop(self):
        """清理循环"""
        while not self._stop_event.is_set():
            try:
                self._cleanup_old_files()
            except Exception as e:
                logger.error(f"清理文件时出错: {str(e)}", exc_info=True)
                
            # 等待下次清理，可被停止事件打断
            self._stop_event.wait(timeout=config.CLEANUP_INTERVAL.total_seconds())
            
    def _cleanup_old_files(self):
        """清理过期文件"""
        now = time.time()
        retention_seconds = config.FILE_RETENTION_DAYS * 24 * 3600
        cleaned_count = 0
        
        for filename in os.listdir(config.UPLOAD_FOLDER):
            file_path = os.path.join(config.UPLOAD_FOLDER, filename)
            if not os.path.isfile(file_path):
                continue
                
            # 检查文件年龄
            file_age = now - os.path.getmtime(file_path)
            if file_age > retention_seconds:
                try:
                    os.remove(file_path)
                    cleaned_count += 1
                    logger.debug(f"已删除过期文件: {filename}")
                except Exception as e:
                    logger.error(f"删除文件 {filename} 时出错: {str(e)}")
                    
        if cleaned_count > 0:
            logger.info(f"清理完成，共删除 {cleaned_count} 个过期文件") 