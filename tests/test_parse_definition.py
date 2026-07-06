"""_parse_flow_inputs_from_definition 解析逻辑测试"""

import json

from yuppie_mcp_alibabacloud_fnf.utils.alibabacloud_fnf.client import (
    _extract_template_data,
    _parse_flow_inputs_from_definition,
)


# ── 基础场景 ──


def test_parse_no_def_node():
    """没有开始-入参说明节点时返回空列表"""
    states = [
        {"Name": "开始", "Type": "Pass", "GlobalConstructor": {}},
        {"Name": "结束", "Type": "Succeed", "End": True},
    ]
    definition_str = json.dumps({"States": states})
    assert _parse_flow_inputs_from_definition(definition_str) == []


def test_parse_empty_definition():
    """空 Definition 返回空列表"""
    assert _parse_flow_inputs_from_definition("") == []


def test_parse_no_states():
    """没有 States 返回空列表"""
    assert _parse_flow_inputs_from_definition('{"Type":"StateMachine"}') == []


def test_parse_no_start_state():
    """没有开始-入参说明节点返回空列表"""
    definition_str = json.dumps({
        "States": [{"Name": "其他", "Type": "Pass"}],
    })
    assert _parse_flow_inputs_from_definition(definition_str) == []


def test_parse_invalid_json():
    """无效 JSON 返回空列表"""
    assert _parse_flow_inputs_from_definition("{invalid}") == []


# ── TemplateTransform 解析 ──


def _make_definition(template: dict | None = None) -> str:
    """构造带 TemplateTransform 节点的 Definition"""
    states = [
        {"Name": "开始", "Type": "Pass", "Next": "开始-入参说明"},
        {
            "Name": "开始-入参说明",
            "Type": "Task",
            "Action": "Extensions:TemplateTransform",
            "Parameters": {"template": template or {}},
        },
        {"Name": "结束", "Type": "Succeed", "End": True},
    ]
    return json.dumps({"States": states})


def test_parse_template_transform():
    """TemplateTransform 的 template 应正确解析"""
    template = {
        "title": {"type": "string", "label": "文章标题", "required": 1},
        "count": {"type": "int", "label": "数量"},
        "dept": {"type": "select", "enum": ["销售部", "技术部"]},
    }
    definition_str = _make_definition(template)
    params = _parse_flow_inputs_from_definition(definition_str)
    assert len(params) == 3
    assert params[0]["variable"] == "title"
    assert params[0]["type"] == "string"
    assert params[0]["label"] == "文章标题"
    assert params[0]["required"] is True  # required: 1 → True
    assert params[1]["variable"] == "count"
    assert params[1]["type"] == "int"
    assert params[2]["variable"] == "dept"
    assert params[2]["type"] == "select"
    assert params[2]["enum"] == ["销售部", "技术部"]


def test_parse_template_order():
    """入参顺序按 template key 顺序"""
    template = {
        "a": {"type": "string"},
        "b": {"type": "int"},
        "c": {"type": "boolean"},
    }
    definition_str = _make_definition(template)
    params = _parse_flow_inputs_from_definition(definition_str)
    assert [p["variable"] for p in params] == ["a", "b", "c"]


def test_parse_template_extra_fields():
    """template 中的额外字段应保留"""
    template = {
        "title": {"type": "string", "label": "标题", "description": "这是文章标题", "required": 1},
    }
    definition_str = _make_definition(template)
    params = _parse_flow_inputs_from_definition(definition_str)
    assert params[0]["description"] == "这是文章标题"


def test_parse_template_non_dict_value():
    """template 中 value 不是 dict 的情况只返回变量名"""
    template = {"title": "just a string"}
    definition_str = _make_definition(template)
    params = _parse_flow_inputs_from_definition(definition_str)
    assert params == [{"variable": "title"}]


# ── 节点查找规则 ──


def test_wrong_action_ignored():
    """同名但 Action 不是 TemplateTransform 的节点应忽略"""
    states = [
        {"Name": "开始", "Type": "Pass"},
        {
            "Name": "开始-入参说明",
            "Type": "Task",
            "Action": "SomeOtherAction",
            "Parameters": {"template": {"x": {"type": "int"}}},
        },
        {"Name": "结束", "Type": "Succeed", "End": True},
    ]
    definition_str = json.dumps({"States": states})
    assert _parse_flow_inputs_from_definition(definition_str) == []


def test_wrong_name_ignored():
    """不是开始-入参说明名字的节点应忽略"""
    states = [
        {"Name": "开始", "Type": "Pass"},
        {
            "Name": "其他节点",
            "Type": "Task",
            "Action": "Extensions:TemplateTransform",
            "Parameters": {"template": {"x": {"type": "int"}}},
        },
        {"Name": "结束", "Type": "Succeed", "End": True},
    ]
    definition_str = json.dumps({"States": states})
    assert _parse_flow_inputs_from_definition(definition_str) == []


# ── _extract_template_data 单元测试 ──


def test_extract_data_dict():
    """直接传 dict 原样返回"""
    data = {"title": {"type": "string"}}
    assert _extract_template_data(data) == data


def test_extract_data_with_data_tag():
    """<data>...</data> 包裹的 JSON 应能正确提取"""
    template_str = "<data>\n{\n    \"title\": {\n        \"type\": \"string\",\n        \"label\": \"文章标题\",\n        \"required\": 1\n    }\n}\n</data>"
    result = _extract_template_data(template_str)
    assert result == {"title": {"type": "string", "label": "文章标题", "required": 1}}


def test_extract_data_multiple_fields():
    """<data> 中多个字段正确解析"""
    template_str = "<data>\n{\n    \"a\": {\"type\": \"string\"},\n    \"b\": {\"type\": \"int\"}\n}\n</data>"
    result = _extract_template_data(template_str)
    assert result == {"a": {"type": "string"}, "b": {"type": "int"}}


def test_extract_data_no_data_tag():
    """没有 <data> 标签的纯 JSON 字符串也能解析"""
    template_str = '{"a": {"type": "string"}}'
    result = _extract_template_data(template_str)
    assert result == {"a": {"type": "string"}}


def test_extract_data_invalid_string():
    """无效 JSON 字符串返回 None"""
    assert _extract_template_data("not json") is None


# ── <data> 格式的集成测试 ──


def _make_definition_with_data_tag(template_str: str) -> str:
    """构造带 <data> 标签包裹 template 的 Definition"""
    states = [
        {"Name": "开始", "Type": "Pass", "Next": "开始-入参说明"},
        {
            "Name": "开始-入参说明",
            "Type": "Task",
            "Action": "Extensions:TemplateTransform",
            "Parameters": {"template": template_str},
        },
        {"Name": "结束", "Type": "Succeed", "End": True},
    ]
    return json.dumps({"States": states})


def test_parse_data_tag_template():
    """真实场景：template 为带 <data> 标签的字符串"""
    template_str = (
        "<data>\n"
        '{\n'
        '    "title": {\n'
        '        "type": "string",\n'
        '        "label": "文章标题",\n'
        '        "required": 1\n'
        '    },\n'
        '    "dept": {\n'
        '        "type": "select",\n'
        '        "label": "部门",\n'
        '        "enum": ["销售部", "技术部"]\n'
        '    }\n'
        "}\n"
        "</data>"
    )
    definition_str = _make_definition_with_data_tag(template_str)
    params = _parse_flow_inputs_from_definition(definition_str)
    assert len(params) == 2
    assert params[0]["variable"] == "title"
    assert params[0]["type"] == "string"
    assert params[0]["label"] == "文章标题"
    assert params[0]["required"] is True
    assert params[1]["variable"] == "dept"
    assert params[1]["type"] == "select"
    assert params[1]["enum"] == ["销售部", "技术部"]


# ── YAML 格式 Definition ──


def test_parse_yaml_definition():
    """YAML 格式的 Definition 应正确解析"""
    yaml_def = """Type: StateMachine
Name: test-flow
States:
  - Name: 开始
    Type: Pass
    Next: 开始-入参说明
  - Name: 开始-入参说明
    Type: Task
    Action: 'Extensions:TemplateTransform'
    Parameters:
      template: |-
        <data>
        {
            "event": {
                "type": "select",
                "label": "事件",
                "enum": ["Group Bot Message", "Send Bot Message"]
            },
            "status": {
                "type": "select",
                "label": "返回状态",
                "enum": ["正常", "异常"]
            }
        }
        </data>
    Next: 结束
  - Name: 结束
    Type: Succeed
    End: true
"""
    params = _parse_flow_inputs_from_definition(yaml_def)
    assert len(params) == 2
    assert params[0]["variable"] == "event"
    assert params[0]["type"] == "select"
    assert params[0]["label"] == "事件"
    assert params[0]["enum"] == ["Group Bot Message", "Send Bot Message"]
    assert params[1]["variable"] == "status"
    assert params[1]["type"] == "select"
    assert params[1]["label"] == "返回状态"
    assert params[1]["enum"] == ["正常", "异常"]


def test_parse_yaml_invalid():
    """无效 YAML 返回空列表"""
    assert _parse_flow_inputs_from_definition("{{invalid yaml") == []


def test_parse_yaml_not_dict():
    """YAML 解析后不是 dict 返回空列表"""
    assert _parse_flow_inputs_from_definition("hello") == []
