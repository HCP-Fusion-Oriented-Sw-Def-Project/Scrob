import Levenshtein

from utility import is_size_changed, is_image, is_image_changed_2, is_rel_location_changed


class GList(object):
    """
    GList 类 内部存储 list_root list_node 以及list中的叶子节点
    """

    def __init__(self, root_node):
        self.root = root_node
        self.nodes = []
        self.leaf_desc = []
        # 将leaf_nodes中的节点进行分组所得
        self.groups = []

        # 可以去发现一下glist的坐标以及长宽的变化
        self.width = self.root.width
        self.height = self.root.height

        self.x_loc = self.root.x_loc
        self.y_loc = self.root.y_loc

        # 匹配上的glist
        self.matched_glist = None
        self.is_matched = False

        self.root_changed_attrs = {
            'location': 0,
            'size': 0,
        }

    def group_leaf_desc(self):
        """
        对子孙节点进行分组
        按照一个类似聚类的算法
        :return:
        """

        # 先初始化一个group 然后向其中加入一个节点
        first_group = ListNodeGroup()
        first_group.nodes.append(self.leaf_desc[0])
        self.groups.append(first_group)

        for node in self.leaf_desc[1:]:
            # 生成一个数组 用于存储得分  数组长度等于group的数量
            scores = [0] * len(self.groups)
            index = 0
            for group in self.groups:
                score = get_node_group_similar(node, group)
                scores[index] = score
                index += 1

            # 获取最大得分
            max_score = max(scores)

            # 如果最大相似值超过阈值
            if max_score >= 0.8:
                max_index = -1
                for i in range(len(scores)):
                    if scores[i] == max_score:
                        max_index = i
                        break

                group = self.groups[max_index]
                # 将此节点加入
                group.nodes.append(node)

            else:
                # 否则 创建一个新的group
                group = ListNodeGroup()
                group.nodes.append(node)
                self.groups.append(group)

        # 分组完后 获取每个组节点的相似属性
        for group in self.groups:
            group.get_common_features()


class ListNodeGroup(object):
    """
    列表节点组
    主要是对列表节点中的叶子节点进行分组统计
    """

    def __init__(self):
        self.nodes = []
        self.common_features = {
            'class': 0,
            'resource-id': 0,
            'text': 0,
            'content-desc': 0,
            'rel_location': 0,
            'size': 0,
            'color': 0,
        }

        self.changed_common_features = {
            'class': 0,
            'resource-id': 0,
            'text': 0,
            'content-desc': 0,
            'rel_location': 0,
            'size': 0,
            'color': 0,
        }

        self.is_changed = False

        self.matched_group = None
        self.is_matched = False

    def get_common_features(self):
        """
        获取该组节点的相似特征
        :return:
        """

        class_flag = True
        id_flag = True
        text_flag = True
        desc_flag = True
        size_flag = True
        color_flag = True
        rel_location_flag = True

        sample_node = self.nodes[0]

        for node in self.nodes[1:]:
            if sample_node.attrib['class'] != node.attrib['class']:
                class_flag = False

            if sample_node.attrib['resource-id'] != node.attrib['resource-id']:
                id_flag = False

            if sample_node.attrib['text'] != node.attrib['text']:
                text_flag = False

            if sample_node.attrib['content-desc'] != node.attrib['content-desc']:
                desc_flag = False

            if is_size_changed(sample_node, node, True):
                size_flag = False

            if is_rel_location_changed(sample_node, node):
                rel_location_flag = False

            if is_image(sample_node):
                if is_image_changed_2(sample_node, node, sample_node.img_path, node.img_path):
                    color_flag = False

        if class_flag:
            self.common_features['class'] = 1

        if id_flag:
            self.common_features['resource-id'] = 1

        if text_flag:
            self.common_features['text'] = 1

        if desc_flag:
            self.common_features['content-desc'] = 1

        if size_flag:
            self.common_features['size'] = 1

        if rel_location_flag:
            self.common_features['rel_location'] = 1

        if color_flag:
            self.common_features['color'] = 1


def get_node_group_similar(node, group):
    """
    获得节点与节点组之间的相似值
    :param node:
    :param group:
    :return:
    """

    score = 0
    for tmp_node in group.nodes:
        score += get_nodes_similar_score_across_versions(node, tmp_node)

    score /= len(group.nodes)

    return score


def is_glist_matched(x_glist, y_glist):
    """
    判断两个list列表是否可以匹配上
    :param x_glist:
    :param y_list:
    :return:
    """

    count = 0

    for x_desc in x_glist.leaf_desc:
        for y_desc in y_glist.leaf_desc:
            if is_list_node_matched(x_desc, y_desc):
                count += 1

    if count / max(len(x_glist.leaf_desc), len(y_glist.leaf_desc)) >= 0.5:
        return True

    return False


def is_group_matched(x_group, y_group):
    """
    判断两个group是否可以匹配上
    :param x_group:
    :param y_group:
    :return:
    """

    count = 0
    for x_node in x_group.nodes:
        for y_node in y_group.nodes:
            if is_list_node_matched(x_node, y_node):
                count += 1

    if count / max(len(x_group.nodes), len(y_group.nodes)) >= 0.5:
        return True

    return False


def is_list_node_matched(x_node, y_node):
    """
    判断列表中的两个叶子节点是否匹配
    :return:
    """

    score = get_nodes_similar_score_across_versions(x_node, y_node)

    if score >= 0.8:
        return True

    return False


def get_nodes_similar_score_across_versions(x_node, y_node):
    """
    跨版本对比列表中叶子节点时所使用的得分计算
    :param x_node:
    :param y_node:
    :return:
    """

    if x_node.attrib['class'] != y_node.attrib['class']:
        return 0

    x_node_id = x_node.attrib['resource-id']
    y_node_id = y_node.attrib['resource-id']

    x_node_text = x_node.attrib['text']
    y_node_text = y_node.attrib['text']
    x_node_content = x_node.attrib['content-desc']
    y_node_content = y_node.attrib['content-desc']

    if x_node_id.find('/') != -1:
        x_node_id = x_node_id.split('/')[1]

    if y_node_id.find('/') != -1:
        y_node_id = y_node_id.split('/')[1]

    # id 不为空
    if len(x_node_id) != 0 or len(y_node_id) != 0:
        if x_node_id == y_node_id:
            return 1
        return 0

    else:
        # 如果 横/纵 坐标  以及 长/宽 有两者占 则表示是同类 即 横坐标和长度 纵坐标和宽度 一共4种组合
        # 这种方法只对一个页面上的没有id的同类元素有效
        score = 0

        if len(x_node_text) != 0 or len(y_node_text) != 0:
            if x_node_text == y_node_text:
                score += 0.4

        if len(x_node_content) != 0 or len(y_node_content) != 0:
            if x_node_content == y_node_content:
                score += 0.4

        if x_node.x_loc == y_node.x_loc or x_node.y_loc == y_node.y_loc:
            score += 0.4

        if x_node.width == y_node.width or x_node.height == y_node.height:
            score += 0.4

        # 计算相对list的xpath的相似性
        if is_xpath_similar(x_node, y_node):
            score += 0.4

        # 计算相对list的坐标是否是接近的
        x1, y1, x2, y2 = x_node.parse_rel_bounds()

        x3, y3, x4, y4 = y_node.parse_rel_bounds()

        if abs(x1 - x3) / x_node.width < 1 and abs(y1 - y3) / x_node.height < 1:
            score += 0.4

        return score


def is_xpath_similar(x_node, y_node):
    """
    判断列表中的两个叶子节点的相对xpath是否是相似的
    :param x_node:
    :param y_node:
    :return:
    """

    x_xpath = x_node.rel_xpath
    y_xpath = y_node.rel_xpath

    dis_score = Levenshtein.distance(x_xpath, y_xpath) / (max(len(x_xpath), len(y_xpath)))

    if 1 - dis_score >= 0.8:
        return True

    x_xpath = x_node.full_xpath
    y_xpath = y_node.full_xpath

    dis_score = Levenshtein.distance(x_xpath, y_xpath) / (max(len(x_xpath), len(y_xpath)))

    if 1 - dis_score >= 0.8:
        return True

    return False
