from enum import Enum


class ChangedType(Enum):
    """
    节点变化分类
    """
    REMAIN = 0  # 不发生变化
    STATE = 1  # 表示这个节点时有时五
    ATTR = 2  # 某些属性发生变化


def is_xpath_matched(x_node, y_node):
    """
    判断两个节点是否可以根据xpath匹配上
    """

    for x_xpath in x_node.xpath:
        if x_xpath in y_node.xpath:
            return True

    return False


def is_location_changed(x_node, y_node):
    """
    判断节点坐标是否变化
    """
    if abs(x_node.x_loc - y_node.x_loc) + abs(x_node.y_loc - y_node.y_loc) > 0:
        return True

    return False


def is_size_changed(x_node, y_node):
    """
    判断节点的尺寸大小是否发生变化
    """

    if x_node.width != y_node.width or x_node.height != y_node.height:
        return True

    return False


def nodes_attr_tag(x_node, y_node):
    """
    对节点属性是否变化进行标记
    """

    is_changed = False

    if x_node.attrib['class'] != y_node.attrib['class']:
        is_changed = True
        if x_node.changed_attrs['class'] == 0:
            x_node.changed_attrs['class'] = 1
        if y_node.changed_attrs['class'] == 0:
            y_node.changed_attrs['class'] = 1

    if x_node.attrib['resource-id'] != y_node.attrib['resource-id']:
        is_changed = True
        if x_node.changed_attrs['resource-id'] == 0:
            x_node.changed_attrs['resource-id'] = 1
        if y_node.changed_attrs['resource-id'] == 0:
            y_node.changed_attrs['resource-id'] = 1

    if x_node.attrib['text'] != y_node.attrib['text']:
        is_changed = True
        if x_node.changed_attrs['text'] == 0:
            x_node.changed_attrs['text'] = 1
        if y_node.changed_attrs['text'] == 0:
            y_node.changed_attrs['text'] = 1

    if x_node.attrib['content-desc'] != y_node.attrib['content-desc']:
        is_changed = True
        if x_node.changed_attrs['content-desc'] == 0:
            x_node.changed_attrs['content-desc'] = 1
        if y_node.changed_attrs['content-desc'] == 0:
            y_node.changed_attrs['content-desc'] = 1

    if is_location_changed(x_node, y_node):
        is_changed = True
        if x_node.changed_attrs['location'] == 0:
            x_node.changed_attrs['location'] = 1
        if y_node.changed_attrs['location'] == 0:
            y_node.changed_attrs['location'] = 1

    if is_size_changed(x_node, y_node):
        is_changed = True
        if x_node.changed_attrs['location'] == 0:
            x_node.changed_attrs['location'] = 1
        if y_node.changed_attrs['location'] == 0:
            y_node.changed_attrs['location'] = 1

    if is_changed:
        x_node.changed_type = ChangedType.ATTR
        y_node.changed_type = ChangedType.ATTR

    # todo 图片颜色判断
