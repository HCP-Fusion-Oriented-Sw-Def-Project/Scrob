import cv2
from enum import Enum

import Levenshtein


class ChangedType(Enum):
    """
    节点变化分类
    """
    REMAIN = 0  # 不发生变化
    STATE = 1  # 表示这个节点时有时五
    ATTR = 2  # 某些属性发生变化


def is_image(node):
    """
    判断一个元素是不是图片
    :return:
    """

    if 'image' in node.attrib['class'].lower():
        return True

    return False


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


def is_image_changed(x_node, y_node, x_img_path, y_img_path):
    """
    判断图片颜色是否发生变化 单通道直方图
    """

    x_img = cv2.imread(x_img_path)
    y_img = cv2.imread(y_img_path)

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

    x_hist = cv2.calcHist([cropped_x_img], [0], None, [256], [0, 255])
    y_hist = cv2.calcHist([cropped_y_img], [0], None, [256], [0, 255])

    # 相关性计算
    res = cv2.compareHist(x_hist, y_hist, method=cv2.HISTCMP_CORREL)

    if res >= 0.9:
        return False

    return True


def is_image_changed_2(x_node, y_node, x_img_path, y_img_path):
    """
    计算三通道的直方图相似度
    :param x_node:
    :param y_node:
    :param x_img_path:
    :param y_img_path:
    :return:
    """

    x_img = cv2.imread(x_img_path)
    y_img = cv2.imread(y_img_path)

    # 获取截图
    x1, y1, x2, y2 = x_node.parse_bounds()

    try:
        cropped_x_img = x_img[y1:y2, x1:x2]
    except Exception as e:
        print(x1, y1, x2, y2)
        print(x_img)
        print(x_img_path)
        print(y_img_path)
        # cv2不能够读取中文路径 所以出错
        exit(0)

    x3, y3, x4, y4 = y_node.parse_bounds()
    cropped_y_img = y_img[y3:y4, x3:x4]

    # 三通道直方图对比算法 好使
    # 将图像resize后 分离为RGB三个通道 再计算每个通道的相似值
    image_x = cv2.resize(cropped_x_img, (256, 256))
    image_y = cv2.resize(cropped_y_img, (256, 256))

    sub_image_x = cv2.split(image_x)
    sub_image_y = cv2.split(image_y)

    res = 0

    for img_x, img_y in zip(sub_image_x, sub_image_y):
        res += calculate(img_x, img_y)

    res /= 3

    if res >= 0.9:
        return False

    return True


def calculate(image_x, image_y):
    """
    计算单通道直方图的相似值
    :param image_x:
    :param image_y:
    :return:
    """

    hist1 = cv2.calcHist([image_x], [0], None, [256], [0.0, 255.0])
    hist2 = cv2.calcHist([image_y], [0], None, [256], [0.0, 255.0])
    # # 计算直方图的重合度
    degree = 0
    for i in range(len(hist1)):
        if hist1[i] != hist2[i]:
            # 计算像素点数量的差异 也就是计算直方图的重合度 否则计算 同值的 有多少个像素点相同 比例占多大
            degree += abs(hist1[i][0] - hist2[i][0]) / max(hist1[i][0], hist2[i][0])
        else:
            # 如果完全相同 那么重合度为1
            degree += 1

    degree /= len(hist1)

    return degree


def get_nodes_attr_tag(x_node, y_node, x_tree, y_tree):
    """
    对节点属性是否变化进行标记
    """

    has_changed = False

    if x_node.attrib['class'] != y_node.attrib['class']:
        has_changed = True
        if x_node.dynamic_changed_attrs['class'] == 0:
            x_node.dynamic_changed_attrs['class'] = 1
        if y_node.dynamic_changed_attrs['class'] == 0:
            y_node.dynamic_changed_attrs['class'] = 1

    if x_node.attrib['resource-id'] != y_node.attrib['resource-id']:
        has_changed = True
        if x_node.dynamic_changed_attrs['resource-id'] == 0:
            x_node.dynamic_changed_attrs['resource-id'] = 1
        if y_node.dynamic_changed_attrs['resource-id'] == 0:
            y_node.dynamic_changed_attrs['resource-id'] = 1

    if x_node.attrib['text'] != y_node.attrib['text']:
        has_changed = True
        if x_node.dynamic_changed_attrs['text'] == 0:
            x_node.dynamic_changed_attrs['text'] = 1
        if y_node.dynamic_changed_attrs['text'] == 0:
            y_node.dynamic_changed_attrs['text'] = 1

    if x_node.attrib['content-desc'] != y_node.attrib['content-desc']:
        has_changed = True
        if x_node.dynamic_changed_attrs['content-desc'] == 0:
            x_node.dynamic_changed_attrs['content-desc'] = 1
        if y_node.dynamic_changed_attrs['content-desc'] == 0:
            y_node.dynamic_changed_attrs['content-desc'] = 1

    if is_location_changed(x_node, y_node):
        has_changed = True
        if x_node.dynamic_changed_attrs['location'] == 0:
            x_node.dynamic_changed_attrs['location'] = 1
        if y_node.dynamic_changed_attrs['location'] == 0:
            y_node.dynamic_changed_attrs['location'] = 1

    if is_size_changed(x_node, y_node):
        has_changed = True
        if x_node.dynamic_changed_attrs['size'] == 0:
            x_node.dynamic_changed_attrs['size'] = 1
        if y_node.dynamic_changed_attrs['size'] == 0:
            y_node.dynamic_changed_attrs['size'] = 1

    if is_image(x_node):
        if is_image_changed_2(x_node, y_node, x_tree.img_path, y_tree.img_path):
            has_changed = True
            if x_node.dynamic_changed_attrs['color'] == 0:
                x_node.dynamic_changed_attrs['color'] = 1
            if y_node.dynamic_changed_attrs['color'] == 0:
                y_node.dynamic_changed_attrs['color'] = 1

    if has_changed:
        x_node.dynamic_changed_type = ChangedType.ATTR.value
        y_node.dynamic_changed_type = ChangedType.ATTR.value


def get_nodes_tag(x_tree, y_tree):
    """
    对节点属性进行标记 判断是时有时无 还是属性变化
    """

    x_nodes = x_tree.nodes
    y_nodes = y_tree.nodes

    for x_node in x_nodes:
        has_matched = False
        for y_node in y_nodes:
            if x_node.xpath[0] == y_node.xpath[0]:
                has_matched = True
                if (x_node.dynamic_changed_type == ChangedType.REMAIN.value or
                        y_node.dynamic_changed_type == ChangedType.REMAIN.value):
                    get_nodes_attr_tag(x_node, y_node, x_tree, y_tree)

        if not has_matched:
            x_node.dynamic_changed_type = ChangedType.STATE.value

    for y_node in y_nodes:
        has_matched = False
        for x_node in x_nodes:
            if x_node.xpath[0] == y_node.xpath[0]:
                has_matched = True

        if not has_matched:
            y_node.dynamic_changed_type = ChangedType.STATE.value


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


def has_desc_in_changed_cls(node, xml_tree):
    """
    判断一个节点是否有子孙节点
    存在于（会变化的聚类：指的是内部含有元素会变化）当中
    暂时弃用
    """

    for desc in node.descendants:
        if not desc.children:
            for cluster_id in xml_tree.attr_changed_clusters:
                if desc.cluster_id == cluster_id:
                    return True

    return False


def has_dynamic_desc(node):
    """
    判断一个节点的子孙节点是否是动态的
    :param node:
    :return:
    """

    for desc in node.descendants:
        if not desc.children and desc.dynamic_changed_type != ChangedType.REMAIN.value:
            return True

    return False


def has_common_desc(x_node, y_node):
    """
    判断两个非叶子节点是否有公共的子孙节点
    """

    for x_desc in x_node.descendants:
        for y_desc in y_node.descendants:
            if x_desc.idx == y_desc.idx:
                return True

    return False


def is_filter(node):
    """
    用于判断一个叶子节点是否需要被过滤
    :param node:
    :return:
    """

    if 'layout' in node.attrib['class'].lower():
        return True

    return False


def is_filter_list_node(node, clusters):
    """
    过滤掉那些不太像是组合的含有动态元素的列表
    :return:
    """

    count_desc = 0

    for desc in node.descendants:
        if not desc.children:
            count_desc += 1

    if count_desc <= 1:
        return True

    if node.cluster_id != -1 and node.cluster_id in clusters.keys():
        dynamic_list_nodes_count = 0
        cluster = clusters[node.cluster_id]

        for tmp_node in cluster.nodes:
            if has_dynamic_desc(tmp_node):
                dynamic_list_nodes_count += 1

        if dynamic_list_nodes_count / len(clusters[node.cluster_id].nodes) < 0.5:
            return True

    return False


def get_levenshtein_distance(x_node, y_node):
    """
    计算文本间的编辑距离
    :param str_x:
    :param str_y:
    :return:
    """

    return Levenshtein.distance(x_node.xpath[0], y_node.xpath[0])


def get_GUI_distance(x_node, y_node):
    """
    获取节点之间的gui距离
    :param x_node:
    :param y_node:
    :return:
    """
    return (abs(x_node.width - y_node.width) +
            abs(x_node.height - y_node.height) +
            abs(x_node.x_loc - y_node.x_loc) +
            abs(x_node.y_loc - y_node.y_loc))


def get_visual_similar(x_node, y_node):
    """
    获取节点之间的像素点差异
    :param x_node:
    :param y_node:
    :return:
    """

    x_img = cv2.imread(x_node.img_path)
    y_img = cv2.imread(y_node.img_path)

    # 获取截图
    x1, y1, x2, y2 = x_node.parse_bounds()
    cropped_x_img = x_img[y1:y2, x1:x2]

    x3, y3, x4, y4 = y_node.parse_bounds()
    cropped_y_img = y_img[y3:y4, x3:x4]

    # 三通道直方图对比算法 好使
    # 将图像resize后 分离为RGB三个通道 再计算每个通道的相似值
    image_x = cv2.resize(cropped_x_img, (256, 256))
    image_y = cv2.resize(cropped_y_img, (256, 256))

    sub_image_x = cv2.split(image_x)
    sub_image_y = cv2.split(image_y)

    res = 0

    for img_x, img_y in zip(sub_image_x, sub_image_y):
        res += calculate(img_x, img_y)

    res /= 3

    return res


def get_matched_node_by_idx(idx, nodes_list):
    """
    通过匹配元素的idx找回匹配元素
    :param idx:
    :param nodes_list:
    :return:
    """

    for node in nodes_list:
        if node.idx == idx:
            return node

    return None


def is_rel_location_changed(x_node, y_node):
    """

    :param x_node:
    :param y_node:
    :return:
    """

    x1, y1, x2, y2 = x_node.parse_rel_bounds()

    x3, y3, x4, y4 = y_node.parse_rel_bounds()

    if x1 != x3 or y1 != y3:
        return True

    return False


def get_str_sim(x_node, y_node):
    """
    获取两个节点间的字符文本相似度
    :param x_node:
    :param y_node:
    :return:
    """

    id_flag = False
    text_flag = False
    content_flag = False

    if x_node.attrib['resource-id'] != '' or y_node.attrib['resource-id'] != '':
        x_id = x_node.attrib['resource-id']
        y_id = y_node.attrib['resource-id']
        if x_node.attrib['resource-id'] != '':
            x_id = x_id.split('/')[1]

        if y_node.attrib['resource-id'] != '':
            y_id = y_id.split('/')[1]

        id_flag = True

        id_sim = 1 - Levenshtein.distance(x_id, y_id) / max(len(x_id), len(y_id))

    if x_node.attrib['text'] != '' or y_node.attrib['text'] != '':
        x_text = x_node.attrib['text']
        y_text = y_node.attrib['text']

        text_flag = True

        text_sim = 1 - Levenshtein.distance(x_text, y_text) / max(len(x_text), len(y_text))

    if x_node.attrib['content-desc'] != '' or y_node.attrib['content-desc'] != '':
        x_content = x_node.attrib['content-desc']
        y_content = y_node.attrib['content-desc']

        content_flag = True
        content_sim = 1 - Levenshtein.distance(x_content, y_content) / max(len(x_content), len(y_content))

    sim_list = []

    if id_flag:
        sim_list.append(id_sim)

    if text_flag:
        sim_list.append(text_sim)

    if content_flag:
        sim_list.append(content_sim)

    final_sim = 0

    sim_flag = True
    for sim in sim_list:
        final_sim += sim
        if sim < 0.6:
            sim_flag = False

    if len(sim_list) != 0 and sim_flag:
        return final_sim / len(sim_list)
    else:
        return 0
