"""
号码检测器测试
测试号码识别、验证和清理功能
"""

import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from phone_detector import PhoneDetector

class TestPhoneDetector(unittest.TestCase):
    """号码检测器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.detector = PhoneDetector()
    
    def test_pure_number_detection(self):
        """测试纯数字号码检测"""
        # 有效的纯数字
        valid_numbers = [
            "13812345678",
            "18888888888",
            "15012345678",
            "12345678",  # 最小长度
            "123456789012345"  # 最大长度
        ]
        
        for number in valid_numbers:
            with self.subTest(number=number):
                result = self.detector.detect_phone_number(number)
                self.assertEqual(result, number, f"应该检测到号码: {number}")
    
    def test_invalid_pure_numbers(self):
        """测试无效的纯数字"""
        invalid_numbers = [
            "1234567",  # 太短
            "1234567890123456",  # 太长
            "00000000",  # 全零
            "11111111",  # 重复数字
            "22222222",  # 重复数字
            "",  # 空字符串
            "abc123456",  # 包含字母
        ]
        
        for number in invalid_numbers:
            with self.subTest(number=number):
                result = self.detector.detect_phone_number(number)
                self.assertIsNone(result, f"不应该检测到号码: {number}")
    
    def test_keyword_number_detection(self):
        """测试带关键词的号码检测"""
        test_cases = [
            ("号码：13812345678", "13812345678"),
            ("客户：138-1234-5678", "13812345678"),
            ("电话：(138) 1234.5678", "13812345678"),
            ("手机：138 1234 5678", "13812345678"),
            ("联系方式：+86 138 1234 5678", "8613812345678"),
            ("号码: 13812345678", "13812345678"),  # 英文冒号
            ("客户电话：13812345678", "13812345678"),
        ]
        
        for message, expected in test_cases:
            with self.subTest(message=message):
                result = self.detector.detect_phone_number(message)
                self.assertEqual(result, expected, f"消息: {message}")
    
    def test_number_cleaning(self):
        """测试号码清理功能"""
        test_cases = [
            ("138-1234-5678", "13812345678"),
            ("(138) 1234.5678", "13812345678"),
            ("138 1234 5678", "13812345678"),
            ("+86 138 1234 5678", "8613812345678"),
            ("138.1234.5678", "13812345678"),
            ("138_1234_5678", "13812345678"),
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input=input_text):
                result = self.detector._clean_number(input_text)
                self.assertEqual(result, expected)
    
    def test_validation(self):
        """测试号码验证"""
        # 有效号码
        valid_phones = [
            "13812345678",
            "18888888888",
            "12345678",
            "123456789012345"
        ]
        
        for phone in valid_phones:
            with self.subTest(phone=phone):
                self.assertTrue(self.detector._is_valid_phone(phone))
        
        # 无效号码
        invalid_phones = [
            "1234567",  # 太短
            "1234567890123456",  # 太长
            "00000000",  # 全零
            "11111111",  # 重复数字
            "abc12345",  # 包含字母
            "",  # 空字符串
        ]
        
        for phone in invalid_phones:
            with self.subTest(phone=phone):
                self.assertFalse(self.detector._is_valid_phone(phone))
    
    def test_complex_messages(self):
        """测试复杂消息"""
        test_cases = [
            ("今天的客户号码：13812345678，请记录", "13812345678"),
            ("联系电话是138-1234-5678，备注：VIP客户", "13812345678"),
            ("号码：13812345678 姓名：张三", "13812345678"),
            ("这不是号码：123", None),  # 太短
            ("随便聊天，没有号码", None),
            ("电话：00000000", None),  # 无效号码
        ]
        
        for message, expected in test_cases:
            with self.subTest(message=message):
                result = self.detector.detect_phone_number(message)
                self.assertEqual(result, expected)
    
    def test_case_insensitive_keywords(self):
        """测试关键词大小写不敏感"""
        test_cases = [
            ("号码：13812345678", "13812345678"),
            ("号码：13812345678", "13812345678"),
            ("客户：13812345678", "13812345678"),
            ("客户：13812345678", "13812345678"),
        ]
        
        for message, expected in test_cases:
            with self.subTest(message=message):
                result = self.detector.detect_phone_number(message)
                self.assertEqual(result, expected)
    
    def test_multiple_numbers_in_message(self):
        """测试消息中包含多个号码的情况"""
        # 应该返回第一个有效号码
        message = "号码：13812345678，备用电话：15012345678"
        result = self.detector.detect_phone_number(message)
        self.assertEqual(result, "13812345678")
    
    def test_edge_cases(self):
        """测试边界情况"""
        edge_cases = [
            (None, None),
            ("", None),
            ("   ", None),
            ("号码：", None),
            ("号码：abc", None),
            ("号码：123", None),  # 太短
        ]
        
        for message, expected in edge_cases:
            with self.subTest(message=message):
                result = self.detector.detect_phone_number(message)
                self.assertEqual(result, expected)

if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
