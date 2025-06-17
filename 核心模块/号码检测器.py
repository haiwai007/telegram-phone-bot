"""
号码检测和验证模块
处理消息中的号码识别、提取、清理和验证
"""

import re
import logging
from typing import Optional, List, Tuple
from .配置管理 import Config

logger = logging.getLogger(__name__)

class PhoneDetector:
    """号码检测器"""
    
    def __init__(self):
        self.keywords = Config.PHONE_KEYWORDS
        self.min_length = Config.MIN_PHONE_LENGTH
        self.max_length = Config.MAX_PHONE_LENGTH
        
        # 编译正则表达式以提高性能
        self._compile_patterns()
    
    def _compile_patterns(self):
        """编译正则表达式模式"""
        # 纯数字模式（8-15位）
        self.pure_number_pattern = re.compile(r'^\d{8,15}$')

        # 带关键词的模式 - 修复为单个捕获组
        keyword_patterns = []
        for keyword in self.keywords:
            # 转义特殊字符并创建模式
            escaped_keyword = re.escape(keyword)
            # 匹配关键词后跟数字（可能包含分隔符）
            pattern = f'{escaped_keyword}\\s*([\\d\\s\\-\\(\\)\\.\\+]+)'
            keyword_patterns.append(pattern)

        # 合并所有关键词模式，使用非捕获组
        combined_pattern = '(?:' + ')|(?:'.join(keyword_patterns) + ')'
        self.keyword_pattern = re.compile(combined_pattern, re.IGNORECASE)

        # 数字提取模式（提取所有数字）
        self.digit_pattern = re.compile(r'\d+')

        # 无效号码模式
        self.invalid_patterns = [
            re.compile(r'^0+$'),  # 全零
            re.compile(r'^(\d)\1+$'),  # 重复单个数字
        ]
    
    def detect_phone_number(self, message: str) -> Optional[str]:
        """
        从消息中检测并提取号码
        返回清理后的号码字符串，如果没有检测到有效号码则返回None
        """
        if not message or not message.strip():
            return None
        
        message = message.strip()
        
        # 方法1: 检查是否为纯数字消息
        phone = self._detect_pure_number(message)
        if phone:
            return phone
        
        # 方法2: 检查带关键词的消息
        phone = self._detect_keyword_number(message)
        if phone:
            return phone
        
        return None
    
    def _detect_pure_number(self, message: str) -> Optional[str]:
        """检测纯数字消息"""
        # 清理消息，只保留数字
        cleaned = self._clean_number(message)
        
        if not cleaned:
            return None
        
        # 验证长度
        if not (self.min_length <= len(cleaned) <= self.max_length):
            return None
        
        # 验证格式
        if self._is_valid_phone(cleaned):
            logger.debug(f"检测到纯数字号码: {cleaned}")
            return cleaned
        
        return None
    
    def _detect_keyword_number(self, message: str) -> Optional[str]:
        """检测带关键词的号码"""
        # 使用search而不是findall来获取匹配对象
        match = self.keyword_pattern.search(message)

        if match:
            # 获取所有捕获组
            groups = match.groups()
            # 找到第一个非空的捕获组
            for group in groups:
                if group and group.strip():
                    # 清理提取的号码部分
                    cleaned = self._clean_number(group)

                    if not cleaned:
                        continue

                    # 验证长度
                    if not (self.min_length <= len(cleaned) <= self.max_length):
                        continue

                    # 验证格式
                    if self._is_valid_phone(cleaned):
                        logger.debug(f"检测到关键词号码: {cleaned} (原文: {group})")
                        return cleaned

        return None
    
    def _clean_number(self, text: str) -> str:
        """
        清理号码字符串，只保留数字
        移除空格、连字符、括号、点等分隔符
        """
        if not text:
            return ""
        
        # 提取所有数字并连接
        digits = self.digit_pattern.findall(text)
        cleaned = ''.join(digits)
        
        return cleaned
    
    def _is_valid_phone(self, phone: str) -> bool:
        """验证号码格式是否有效"""
        if not phone:
            return False
        
        # 检查是否为纯数字
        if not phone.isdigit():
            return False
        
        # 检查长度
        if not (self.min_length <= len(phone) <= self.max_length):
            return False
        
        # 检查无效模式
        for pattern in self.invalid_patterns:
            if pattern.match(phone):
                logger.debug(f"号码匹配无效模式: {phone}")
                return False
        
        return True
    
    def extract_all_numbers(self, message: str) -> List[str]:
        """
        从消息中提取所有可能的号码
        用于调试和分析
        """
        numbers = []
        
        if not message:
            return numbers
        
        # 提取纯数字
        pure_number = self._detect_pure_number(message)
        if pure_number:
            numbers.append(pure_number)
        
        # 提取关键词号码
        keyword_number = self._detect_keyword_number(message)
        if keyword_number and keyword_number not in numbers:
            numbers.append(keyword_number)
        
        return numbers
    
    def is_phone_message(self, message: str) -> bool:
        """判断消息是否包含号码"""
        return self.detect_phone_number(message) is not None
    
    def get_detection_info(self, message: str) -> dict:
        """
        获取检测详细信息，用于调试
        """
        info = {
            'original_message': message,
            'detected_phone': None,
            'detection_method': None,
            'all_numbers': [],
            'is_valid': False
        }
        
        if not message:
            return info
        
        # 尝试检测
        phone = self.detect_phone_number(message)
        if phone:
            info['detected_phone'] = phone
            info['is_valid'] = True
            
            # 确定检测方法
            if self._detect_pure_number(message):
                info['detection_method'] = 'pure_number'
            elif self._detect_keyword_number(message):
                info['detection_method'] = 'keyword'
        
        # 提取所有可能的数字
        info['all_numbers'] = self.extract_all_numbers(message)
        
        return info
