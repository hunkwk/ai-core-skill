"""
MCDA Core - DecisionMaker 数据模型单元测试

测试决策者数据模型的创建、验证和不可变性。
"""

import pytest

from mcda_core.group.models import DecisionMaker


class TestDecisionMaker:
    """测试 DecisionMaker 数据模型"""

    def test_create_valid_decision_maker(self):
        """测试创建有效的决策者"""
        dm = DecisionMaker(
            id="DM1",
            name="张三",
            weight=1.0
        )

        assert dm.id == "DM1"
        assert dm.name == "张三"
        assert dm.weight == 1.0
        assert dm.expertise is None

    def test_decision_maker_with_expertise(self):
        """测试带专业知识的决策者"""
        dm = DecisionMaker(
            id="DM1",
            name="李四",
            weight=1.0,
            expertise={"成本": 0.8, "质量": 0.9, "技术": 0.7}
        )

        assert dm.expertise is not None
        assert dm.expertise["成本"] == 0.8
        assert dm.expertise["质量"] == 0.9
        assert dm.expertise["技术"] == 0.7

    def test_decision_maker_default_weight(self):
        """测试默认权重为 1.0"""
        dm = DecisionMaker(id="DM1", name="王五")
        assert dm.weight == 1.0

    def test_decision_maker_empty_id_raises_error(self):
        """测试空 ID 抛出异常"""
        with pytest.raises(ValueError, match="id 不能为空"):
            DecisionMaker(id="", name="张三")

    def test_decision_maker_empty_name_raises_error(self):
        """测试空名称抛出异常"""
        with pytest.raises(ValueError, match="name 不能为空"):
            DecisionMaker(id="DM1", name="")

    def test_decision_maker_negative_weight_raises_error(self):
        """测试负权重抛出异常"""
        with pytest.raises(ValueError, match="weight.*不能为负数"):
            DecisionMaker(id="DM1", name="张三", weight=-0.5)

    def test_decision_maker_invalid_expertise_type_raises_error(self):
        """测试无效专业知识类型抛出异常"""
        with pytest.raises(ValueError, match="expertise.*必须是数值类型"):
            DecisionMaker(
                id="DM1",
                name="张三",
                expertise={"成本": "高"}  # 字符串而非数值
            )

    def test_decision_maker_invalid_expertise_range_raises_error(self):
        """测试无效专业知识范围抛出异常"""
        with pytest.raises(ValueError, match="expertise.*必须在 0-1 范围内"):
            DecisionMaker(
                id="DM1",
                name="张三",
                expertise={"成本": 1.5}  # 超出范围
            )

    def test_decision_maker_immutability(self):
        """测试决策者不可变性"""
        dm = DecisionMaker(id="DM1", name="张三", weight=1.0)

        with pytest.raises(Exception):  # FrozenInstanceError
            dm.name = "李四"

    def test_decision_maker_with_zero_weight(self):
        """测试零权重决策者"""
        dm = DecisionMaker(id="DM1", name="张三", weight=0.0)
        assert dm.weight == 0.0

    def test_decision_maker_expertise_with_zero_weight(self):
        """测试专业知识权重为零"""
        dm = DecisionMaker(
            id="DM1",
            name="张三",
            expertise={"成本": 0.0, "质量": 0.5}
        )
        assert dm.expertise["成本"] == 0.0

    def test_decision_maker_with_float_weight(self):
        """测试浮点权重"""
        dm = DecisionMaker(id="DM1", name="张三", weight=0.75)
        assert dm.weight == 0.75
