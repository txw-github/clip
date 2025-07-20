
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能API选择器 - 根据用户需求自动推荐最佳API配置
"""

import json
import os
from typing import Dict, Any, List, Tuple
from api_config_helper import config_helper

class SmartAPISelector:
    """智能API选择器"""
    
    def __init__(self):
        self.config_helper = config_helper
        
        # API类型分类
        self.api_categories = {
            'official': {
                'name': '官方API',
                'pros': ['最新功能', '官方支持', '稳定性高'],
                'cons': ['需要魔法上网', '可能有地区限制'],
                'suitable_for': ['追求最新功能', '稳定性要求高', '有海外网络环境']
            },
            'proxy': {
                'name': '中转API',
                'pros': ['国内可访问', '无需魔法上网', '价格便宜'],
                'cons': ['功能可能滞后', '依赖第三方'],
                'suitable_for': ['国内用户', '快速部署', '成本控制']
            }
        }
        
        # 模型特性分析
        self.model_features = {
            'claude-3-5-sonnet-20240620': {
                'strengths': ['文本分析', '逻辑推理', '创意写作'],
                'best_for': '剧情分析和内容理解',
                'speed': 'medium',
                'cost': 'medium'
            },
            'deepseek-r1': {
                'strengths': ['深度思考', '复杂推理', '代码分析'],
                'best_for': '复杂逻辑分析和决策',
                'speed': 'slow',
                'cost': 'low',
                'special': 'reasoning_content'
            },
            'gemini-2.5-pro': {
                'strengths': ['多模态', '长文本', '快速响应'],
                'best_for': '多媒体内容分析',
                'speed': 'fast',
                'cost': 'medium'
            },
            'gpt-4o': {
                'strengths': ['通用能力', '稳定输出', '指令遵循'],
                'best_for': '通用文本处理',
                'speed': 'medium',
                'cost': 'high'
            }
        }
    
    def analyze_user_needs(self) -> Dict[str, Any]:
        """分析用户需求"""
        print("🔍 智能API配置向导")
        print("=" * 50)
        print("我来帮您选择最适合的AI模型配置！\n")
        
        needs = {}
        
        # 1. 网络环境
        print("1️⃣ 您的网络环境:")
        print("   a. 可以访问国外网站（有魔法上网）")
        print("   b. 只能访问国内网站")
        
        network = input("\n请选择 (a/b): ").lower().strip()
        needs['can_access_foreign'] = network == 'a'
        
        # 2. 使用场景
        print("\n2️⃣ 主要使用场景:")
        print("   a. 电视剧剧情分析")
        print("   b. 通用文本处理")
        print("   c. 复杂逻辑推理")
        print("   d. 多媒体内容分析")
        
        scenario = input("\n请选择 (a-d): ").lower().strip()
        needs['scenario'] = {
            'a': 'drama_analysis',
            'b': 'general_text', 
            'c': 'complex_reasoning',
            'd': 'multimodal'
        }.get(scenario, 'drama_analysis')
        
        # 3. 成本考虑
        print("\n3️⃣ 成本考虑:")
        print("   a. 追求最佳效果，成本不是主要考虑")
        print("   b. 平衡效果和成本")
        print("   c. 优先考虑低成本")
        
        cost = input("\n请选择 (a-c): ").lower().strip()
        needs['cost_priority'] = {
            'a': 'quality_first',
            'b': 'balanced',
            'c': 'cost_first'
        }.get(cost, 'balanced')
        
        # 4. 响应速度要求
        print("\n4️⃣ 响应速度要求:")
        print("   a. 要求快速响应")
        print("   b. 可以接受较慢但更准确的分析")
        
        speed = input("\n请选择 (a/b): ").lower().strip()
        needs['speed_priority'] = speed == 'a'
        
        return needs
    
    def recommend_api(self, needs: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any], float]]:
        """根据需求推荐API配置"""
        recommendations = []
        
        for service_key, service_config in self.config_helper.service_templates.items():
            score = self._calculate_match_score(needs, service_key, service_config)
            if score > 0:
                recommendations.append((service_key, service_config, score))
        
        # 按匹配度排序
        recommendations.sort(key=lambda x: x[2], reverse=True)
        return recommendations[:3]  # 返回前3个推荐
    
    def _calculate_match_score(self, needs: Dict[str, Any], service_key: str, 
                              service_config: Dict[str, Any]) -> float:
        """计算匹配分数"""
        score = 0.0
        
        # 网络环境匹配
        is_official = service_config.get('is_official', False)
        if needs['can_access_foreign']:
            score += 30 if is_official else 20  # 有魔法上网优先官方API
        else:
            score += 40 if not is_official else 0  # 无魔法上网只能用中转
        
        # 模型适用性
        default_model = service_config.get('default_model', '')
        model_features = self.model_features.get(default_model, {})
        
        scenario_bonus = {
            'drama_analysis': {
                'claude-3-5-sonnet-20240620': 25,
                'deepseek-r1': 20,
                'gpt-4o': 15,
                'gemini-2.5-pro': 10
            },
            'complex_reasoning': {
                'deepseek-r1': 25,
                'claude-3-5-sonnet-20240620': 20,
                'gpt-4o': 15,
                'gemini-2.5-pro': 10
            },
            'multimodal': {
                'gemini-2.5-pro': 25,
                'gpt-4o': 20,
                'claude-3-5-sonnet-20240620': 15,
                'deepseek-r1': 5
            }
        }
        
        scenario = needs.get('scenario', 'drama_analysis')
        score += scenario_bonus.get(scenario, {}).get(default_model, 0)
        
        # 成本考虑
        cost_priority = needs.get('cost_priority', 'balanced')
        if cost_priority == 'cost_first':
            score += 15 if model_features.get('cost') == 'low' else 0
        elif cost_priority == 'quality_first':
            score += 15 if model_features.get('cost') in ['medium', 'high'] else 0
        
        # 速度要求
        if needs.get('speed_priority', False):
            score += 10 if model_features.get('speed') == 'fast' else 0
        
        # 服务商稳定性
        if service_key == 'chataiapi':
            score += 10  # ChatAI稳定性加分
        
        return score
    
    def present_recommendations(self, recommendations: List[Tuple[str, Dict[str, Any], float]]) -> str:
        """展示推荐结果"""
        print("\n🎯 为您推荐以下配置方案:")
        print("=" * 50)
        
        for i, (service_key, service_config, score) in enumerate(recommendations, 1):
            print(f"\n{i}. {service_config['name']} (匹配度: {score:.0f}%)")
            print(f"   📍 API类型: {'官方API' if service_config.get('is_official') else '中转API'}")
            print(f"   🤖 推荐模型: {service_config['default_model']}")
            
            if 'description' in service_config:
                print(f"   📝 特点: {service_config['description']}")
            
            # 显示模型特性
            model_features = self.model_features.get(service_config['default_model'], {})
            if model_features:
                print(f"   ⚡ 适用场景: {model_features.get('best_for', '通用')}")
                print(f"   🚀 响应速度: {model_features.get('speed', 'medium')}")
                print(f"   💰 成本: {model_features.get('cost', 'medium')}")
            
            if 'features' in service_config:
                print(f"   🎁 特色功能: {', '.join(service_config['features'])}")
        
        print(f"\n请选择配置方案 (1-{len(recommendations)}): ", end="")
        while True:
            try:
                choice = int(input().strip())
                if 1 <= choice <= len(recommendations):
                    return recommendations[choice - 1][0]
                else:
                    print(f"请输入 1-{len(recommendations)} 之间的数字: ", end="")
            except ValueError:
                print("请输入有效数字: ", end="")
    
    def smart_configure(self) -> bool:
        """智能配置流程"""
        # 分析用户需求
        needs = self.analyze_user_needs()
        
        # 生成推荐
        recommendations = self.recommend_api(needs)
        
        if not recommendations:
            print("❌ 未找到合适的配置方案")
            return False
        
        # 展示推荐并让用户选择
        selected_service = self.present_recommendations(recommendations)
        
        # 配置选定的服务
        return self.config_helper._configure_service(selected_service)

# 全局智能选择器实例
smart_selector = SmartAPISelector()
