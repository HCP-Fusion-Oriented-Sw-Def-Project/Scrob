import cv2
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


def is_image_changed(x_node, y_node, x_tree, y_tree):
    """
    判断图片颜色是否发生变化
    """

    x_img = cv2.imread(x_tree.img_path)
    y_img = cv2.imread(y_tree.img_path)

    # 获取截图
    x1, y1, x2, y2 = x_node.parse_bounds()
    cropped_x_img = x_img[y1:y2, x1:x2]

    x3, y3, x4, y4 = y_node.parse_bounds()
    cropped_y_img = y_img[y3:y4, x3:x4]

    width = int((cropped_x_img.shape[0] + cropped_y_img.shape[0]) / 2)
    height = int((cropped_x_img.shape[1] + cropped_y_img.shape[1]) / 2)

    # 更改图片尺寸
    cropped_x_img = cv2.resize(cropped_x_img, (width, height))
    cropped_y_img = cv2.resize(cropped_y_img, (width, height))

    # 转化为灰度图
    cropped_x_img_grey = cv2.cvtColor(cropped_x_img, cv2.COLOR_BGR2BGRA)
    cropped_y_img_grey = cv2.cvtColor(cropped_y_img, cv2.COLOR_BGR2BGRA)

    # 计算两个图片所对应的直方图

    x_hist = cv2.calcHist([cropped_x_img_grey], [0], None, [256], [0, 255])
    y_hist = cv2.calcHist([cropped_y_img_grey], [0], None, [256], [0, 255])

    # 相关性计算
    res = cv2.compareHist(x_hist, y_hist, method=cv2.HISTCMP_CORREL)

    if res >= 0.9:
        return False

    return True


def get_nodes_attr_tag(x_node, y_node, x_tree, y_tree):
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

    if 'image' in x_node.attrib['class'].lower():
        if is_image_changed(x_node, y_node, x_tree, y_tree):
            is_changed = True
            if x_node.changed_attrs['color'] == 0:
                x_node.changed_attrs['color'] = 1
            if y_node.changed_attrs['color'] == 0:
                y_node.changed_attrs['color'] = 1

    if is_changed:
        x_node.changed_type = ChangedType.ATTR
        y_node.changed_type = ChangedType.ATTR


def get_nodes_tag(x_tree, y_tree):
    """
    对节点属性进行标记 判断是时有时无 还是属性变化
    """

    x_nodes = x_tree.get_nodes()
    y_nodes = y_tree.get_nodes()

    for x_node in x_nodes:
        has_matched = False
        for y_node in y_nodes:
            if is_xpath_matched(x_node, y_node):
                has_matched = True
                if x_node.changed_type == ChangedType.REMAIN or y_node.changed_type == ChangedType.REMAIN:
                    get_nodes_attr_tag(x_node, y_node, x_tree, y_tree)

        if not has_matched:
            x_node.changed_type = ChangedType.STATE

    for y_node in y_nodes:
        has_matched = False
        for x_node in x_nodes:
            if is_xpath_matched(x_node, y_node):
                has_matched = True

        if not has_matched:
            y_node.changed_type = ChangedType.STATE


def get_nodes_common_ans(x_node, y_node):
    """
    获取两个节点的最低公共祖先节点
    """

    ans = x_node.parent

    while y_node not in ans.descendants:
        if ans.full_xpath != '//':
            ans = ans.parent
        else:
            return None

    return ans


# def has_cls_desc_changed(node):
#     """
#     判断一个节点是否有子孙节点发生变化
#     且这个子孙节点存在于某个聚类当中
#     符合上述两个特征的节点 通常都处于列表节点当中
#     """
#
#     for desc in node.descendants:
#         if desc.children == [] and desc.changed_type != ChangedType.REMAIN and desc.cluster_id != -1:
#             return True
#
#     return False


def has_desc_in_changed_cls(node, xml_tree):
    """
    判断一个节点是否有子孙节点
    存在于（会变化的聚类：指的是内部含有元素会变化）当中
    """

    for desc in node.descendants:
        if not desc.children:
            for cluster_id in xml_tree.attr_changed_clusters:
                if desc.cluster_id == cluster_id:
                    return True

    return False
