"""
数据导出管理模块
处理数据导出为各种格式
"""

import csv
import json
import logging
from datetime import datetime
from typing import List, Dict
import tempfile
import os
from pathlib import Path
import pytz
from 配置管理 import Config

logger = logging.getLogger(__name__)

class ExportManager:
    """数据导出管理器"""
    
    def __init__(self):
        self.timezone = pytz.timezone(Config.TIMEZONE)
    
    def export_to_csv(self, records: List[Dict], filename: str = None) -> str:
        """导出为CSV格式"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"phone_records_{timestamp}.csv"
        
        try:
            # 创建临时文件
            temp_dir = tempfile.gettempdir()
            filepath = os.path.join(temp_dir, filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
                if not records:
                    csvfile.write("暂无数据\n")
                    return filepath
                
                # 定义CSV字段
                fieldnames = [
                    '序号', '号码', '提交人', '用户名', '用户ID', 
                    '提交时间', '群组ID', '原始消息', '是否重复'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for i, record in enumerate(records, 1):
                    # 格式化时间
                    timestamp = self._format_timestamp_for_export(record['timestamp'])
                    
                    writer.writerow({
                        '序号': i,
                        '号码': record['phone_number'],
                        '提交人': record['first_name'],
                        '用户名': record.get('username', ''),
                        '用户ID': record['user_id'],
                        '提交时间': timestamp,
                        '群组ID': record.get('group_id', ''),
                        '原始消息': record['original_message'],
                        '是否重复': '是' if record.get('is_duplicate', False) else '否'
                    })
            
            logger.info(f"CSV导出成功: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"CSV导出失败: {e}")
            raise
    
    def export_to_json(self, records: List[Dict], filename: str = None) -> str:
        """导出为JSON格式"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"phone_records_{timestamp}.json"
        
        try:
            # 创建临时文件
            temp_dir = tempfile.gettempdir()
            filepath = os.path.join(temp_dir, filename)
            
            # 准备导出数据
            export_data = {
                'export_time': datetime.now(self.timezone).isoformat(),
                'total_records': len(records),
                'records': []
            }
            
            for record in records:
                export_record = {
                    'phone_number': record['phone_number'],
                    'submitter': {
                        'first_name': record['first_name'],
                        'username': record.get('username', ''),
                        'user_id': record['user_id']
                    },
                    'submission_time': self._format_timestamp_for_export(record['timestamp']),
                    'group_id': record.get('group_id', ''),
                    'original_message': record['original_message'],
                    'is_duplicate': record.get('is_duplicate', False)
                }
                export_data['records'].append(export_record)
            
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, ensure_ascii=False, indent=2)
            
            logger.info(f"JSON导出成功: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"JSON导出失败: {e}")
            raise
    
    def export_to_text(self, records: List[Dict], filename: str = None) -> str:
        """导出为文本格式"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"phone_records_{timestamp}.txt"
        
        try:
            # 创建临时文件
            temp_dir = tempfile.gettempdir()
            filepath = os.path.join(temp_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as txtfile:
                # 写入标题
                txtfile.write("客户号码统计报告\n")
                txtfile.write("=" * 50 + "\n")
                txtfile.write(f"导出时间: {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S')}\n")
                txtfile.write(f"记录总数: {len(records)}\n\n")
                
                if not records:
                    txtfile.write("暂无数据\n")
                    return filepath
                
                # 统计信息
                unique_phones = set(record['phone_number'] for record in records)
                duplicate_count = sum(1 for record in records if record.get('is_duplicate', False))
                
                txtfile.write("统计摘要:\n")
                txtfile.write(f"- 唯一号码数: {len(unique_phones)}\n")
                txtfile.write(f"- 重复提交数: {duplicate_count}\n")
                txtfile.write(f"- 重复率: {(duplicate_count/len(records)*100):.1f}%\n\n")
                
                # 详细记录
                txtfile.write("详细记录:\n")
                txtfile.write("-" * 50 + "\n")
                
                for i, record in enumerate(records, 1):
                    timestamp = self._format_timestamp_for_export(record['timestamp'])
                    duplicate_mark = " [重复]" if record.get('is_duplicate', False) else ""
                    
                    txtfile.write(f"{i}. {record['phone_number']}{duplicate_mark}\n")
                    txtfile.write(f"   提交人: {record['first_name']}")
                    if record.get('username'):
                        txtfile.write(f" (@{record['username']})")
                    txtfile.write(f"\n   时间: {timestamp}\n")
                    txtfile.write(f"   原始消息: {record['original_message']}\n\n")
            
            logger.info(f"文本导出成功: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"文本导出失败: {e}")
            raise
    
    def create_summary_report(self, records: List[Dict], stats: Dict) -> str:
        """创建汇总报告"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"summary_report_{timestamp}.txt"
            temp_dir = tempfile.gettempdir()
            filepath = os.path.join(temp_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as txtfile:
                # 报告标题
                txtfile.write("客户号码统计汇总报告\n")
                txtfile.write("=" * 60 + "\n")
                txtfile.write(f"生成时间: {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # 基础统计
                txtfile.write("📊 基础统计\n")
                txtfile.write("-" * 30 + "\n")
                txtfile.write(f"总记录数: {stats['total_submissions']}\n")
                txtfile.write(f"唯一号码数: {stats['unique_numbers']}\n")
                txtfile.write(f"重复号码数: {stats['duplicate_numbers']}\n")
                txtfile.write(f"重复提交数: {stats['total_duplicates']}\n")
                
                if stats['total_submissions'] > 0:
                    duplicate_rate = (stats['total_duplicates'] / stats['total_submissions']) * 100
                    txtfile.write(f"重复率: {duplicate_rate:.1f}%\n")
                
                txtfile.write("\n")
                
                # 提交者统计
                if records:
                    submitters = {}
                    for record in records:
                        name = record['first_name']
                        if name not in submitters:
                            submitters[name] = {'count': 0, 'duplicates': 0}
                        submitters[name]['count'] += 1
                        if record.get('is_duplicate', False):
                            submitters[name]['duplicates'] += 1
                    
                    txtfile.write("👥 提交者统计 (前10名)\n")
                    txtfile.write("-" * 30 + "\n")
                    
                    sorted_submitters = sorted(submitters.items(), key=lambda x: x[1]['count'], reverse=True)
                    for i, (name, data) in enumerate(sorted_submitters[:10], 1):
                        txtfile.write(f"{i}. {name}: {data['count']}次")
                        if data['duplicates'] > 0:
                            txtfile.write(f" (重复{data['duplicates']}次)")
                        txtfile.write("\n")
                    
                    txtfile.write("\n")
                
                # 时间分析
                if records:
                    txtfile.write("⏰ 时间分析\n")
                    txtfile.write("-" * 30 + "\n")
                    
                    first_record = min(records, key=lambda x: x['timestamp'])
                    last_record = max(records, key=lambda x: x['timestamp'])
                    
                    first_time = self._format_timestamp_for_export(first_record['timestamp'])
                    last_time = self._format_timestamp_for_export(last_record['timestamp'])
                    
                    txtfile.write(f"首次记录: {first_time}\n")
                    txtfile.write(f"最新记录: {last_time}\n")
                    
                    # 按日期统计
                    daily_stats = {}
                    for record in records:
                        date_str = self._format_timestamp_for_export(record['timestamp'])[:10]
                        if date_str not in daily_stats:
                            daily_stats[date_str] = 0
                        daily_stats[date_str] += 1
                    
                    if len(daily_stats) > 1:
                        txtfile.write(f"活跃天数: {len(daily_stats)}天\n")
                        avg_daily = len(records) / len(daily_stats)
                        txtfile.write(f"日均提交: {avg_daily:.1f}次\n")
            
            logger.info(f"汇总报告生成成功: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"汇总报告生成失败: {e}")
            raise
    
    def _format_timestamp_for_export(self, timestamp) -> str:
        """格式化时间戳用于导出"""
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                return timestamp
        
        # 确保时间戳是本地时区
        if timestamp.tzinfo is None:
            timestamp = self.timezone.localize(timestamp)
        elif timestamp.tzinfo != self.timezone:
            timestamp = timestamp.astimezone(self.timezone)
        
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """清理临时文件"""
        try:
            temp_dir = tempfile.gettempdir()
            now = datetime.now()
            
            for filename in os.listdir(temp_dir):
                if filename.startswith(('phone_records_', 'summary_report_')):
                    filepath = os.path.join(temp_dir, filename)
                    try:
                        file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                        if (now - file_time).total_seconds() > max_age_hours * 3600:
                            os.remove(filepath)
                            logger.debug(f"清理临时文件: {filepath}")
                    except Exception as e:
                        logger.warning(f"清理文件失败 {filepath}: {e}")
                        
        except Exception as e:
            logger.error(f"清理临时文件失败: {e}")
