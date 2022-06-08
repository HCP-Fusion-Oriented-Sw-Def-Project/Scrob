import os
from utility import *
from glist import is_glist_matched, is_group_matched


class CompareResult(object):
    """
    结果类
    存储各个数据的输出路径
    以及变化的节点
    最好将这个输出结果可以直接运用于scorb viewer进行查看
    """

    def __init__(self, base_compelete_tree, updated_complete_tree, output_path):
        self.output_path = output_path

        self.removed_nodes = []
        self.changed_nodes = []
        self.added_nodes = []

        self.base_visible_nodes = []
        self.base_invisible_nodes = []

        self.updated_visible_nodes = []
        self.updated_invisible_nodes = []

        # 对比所需要的完全树
        self.base_complete_tree = base_compelete_tree
        self.updated_complete_tree = updated_complete_tree

        # 待比较的screen路径
        self.base_img_path = self.base_complete_tree.main_xml_tree.img_path
        self.updated_img_path = self.updated_complete_tree.main_xml_tree.img_path

    def single_nodes_compare(self):
        """
        首先比较single_nodes
        :return:
        """

        # 首先对所有节点进行匹配 使用非绝对路径的xpath
        for node in self.base_complete_tree.single_nodes:
            get_matched_node_for_single_nodes(node, self.updated_complete_tree.single_nodes, 0)


        # 再次进行匹配
        for node in self.base_complete_tree.single_nodes:
            if node.matched_node_no == -1:
                get_matched_node_for_single_nodes(node, self.updated_complete_tree.single_nodes, 2)

    def get_single_nodes_result(self):
        """
        获取single nodes对比结果
        对于single_nodes 忽略xpath发生变化的节点
        :return:
        """

        self.single_nodes_compare()

        for node in self.base_complete_tree.single_nodes:
            # 获取移除的节点
            if node.matched_node_no == -1 and node.dynamic_changed_type != ChangedType.STATE.value:
                self.removed_nodes.append(node)
            elif node.matched_node_no != -1:
                # 获取变化的节点
                matched_node = get_matched_node_by_idx(node.matched_node_no, self.updated_complete_tree.single_nodes)

                if is_node_changed(node, matched_node) and node.dynamic_changed_type != ChangedType.STATE.value:
                    self.changed_nodes.append(node)

        for node in self.updated_complete_tree.single_nodes:
            # 获取增加的节点
            if node.matched_node_no == -1 and node.dynamic_changed_type != ChangedType.STATE.value:
                self.added_nodes.append(node)

        return self.removed_nodes, self.changed_nodes, self.added_nodes

    def get_list_nodes_result(self):
        """
        获得list nodes的比对结果
        :return:
        """

        self.list_nodes_compare()

        return self.removed_nodes, self.changed_nodes, self.added_nodes

    def list_nodes_compare(self):
        """
        比较列表内部的节点
        :return:
        """

        # 首先是glist的匹配 然后是group的匹配 最后是各个节点的匹配
        for x_glist in self.base_complete_tree.glists:
            for y_glist in self.updated_complete_tree.glists:
                if is_glist_matched(x_glist, y_glist) and y_glist.is_matched == False:
                    x_glist.matched_glist = y_glist
                    y_glist.matched_glist = x_glist
                    y_glist.is_matched = True

        # 然后去搜集没有匹配上的glist
        for x_glist in self.base_complete_tree.glists:
            if x_glist.matched_glist is None:
                for desc in x_glist.leaf_desc:
                    self.removed_nodes.append(desc)

        for y_glist in self.updated_complete_tree.glists:
            if y_glist.matched_glist is None:
                for desc in y_glist.leaf_desc:
                    self.added_nodes.append(desc)

        # 比对匹配上的glists
        for x_glist in self.base_complete_tree.glists:
            if x_glist.matched_glist is not None:
                matched_glist = x_glist.matched_glist
                self.glists_compare(x_glist, matched_glist)

    def glists_compare(self, x_glist, y_glist):
        """
        对glist的变化进行比较
        :param x_glist:
        :param y_glist:
        :return:
        """

        if x_glist.width != y_glist.width or x_glist.height != y_glist.height:
            x_glist.root_changed_attrs['size'] = 1

        if x_glist.x_loc != y_glist.x_loc or x_glist.y_loc != y_glist.y_loc:
            x_glist.root_changed_attrs['location'] = 1

        for x_group in x_glist.groups:
            for y_group in y_glist.groups:
                if is_group_matched(x_group, y_group):
                    x_group.matched_group = y_group
                    y_group.matched_group = x_group
                    x_group.is_matched = True
                    y_group.is_matched = True

        # 处理一下没有匹配上的group
        for x_group in x_glist.groups:
            if x_group.matched_group is None:
                for node in x_group.nodes:
                    self.removed_nodes.append(node)

        for y_group in y_glist.groups:
            if y_group.matched_group is None:
                for node in y_group.nodes:
                    self.added_nodes.append(node)

        # 处理一下匹配上的group节点 比较共性是否发生变化
        for x_group in x_glist.groups:
            if x_group.matched_group is not None:
                matched_group = x_group.matched_group
                self.groups_compare(x_group, matched_group)

    def groups_compare(self, x_group, y_group):
        """
        判断节点的共性是否发生变化
        :param x_group:
        :param y_group:
        :return:
        """

        # 取出两个样本节点 进行比较 以x_sample_node为准比较共性
        x_sample_node = x_group.nodes[0]
        y_sample_node = y_group.nodes[0]

        if x_group.common_features['class'] == 1:
            if x_sample_node.attrib['class'] != y_sample_node.attrib['class']:
                x_group.changed_common_features['class'] = 1
                if not x_group.is_changed:
                    x_group.is_changed = True

        if x_group.common_features['resource-id'] == 1:
            if x_sample_node.attrib['resource-id'] != y_sample_node.attrib['resource-id']:
                x_group.changed_common_features['resource-id'] = 1
                if not x_group.is_changed:
                    x_group.is_changed = True

        if x_group.common_features['text'] == 1:
            if x_sample_node.attrib['text'] != y_sample_node.attrib['text']:
                x_group.changed_common_features['text'] = 1
                if not x_group.is_changed:
                    x_group.is_changed = True

        if x_group.common_features['content-desc'] == 1:
            if x_sample_node.attrib['content-desc'] != y_sample_node.attrib['content-desc']:
                x_group.changed_common_features['content-desc'] = 1
                if not x_group.is_changed:
                    x_group.is_changed = True

        if x_group.common_features['size'] == 1:
            if is_size_changed(x_sample_node, y_sample_node, True):
                x_group.changed_common_features['size'] = 1
                if not x_group.is_changed:
                    x_group.is_changed = True

        if x_group.common_features['rel_location'] == 1:
            if is_rel_location_changed(x_sample_node, y_sample_node):
                x_group.changed_common_features['rel_location'] = 1
                if not x_group.is_changed:
                    x_group.is_changed = True

        if x_group.common_features['color'] == 1:
            if is_image(x_sample_node):
                if is_image_changed_2(x_sample_node, y_sample_node, x_sample_node.img_path, y_sample_node.img_path):
                    x_group.changed_common_features['color'] = 1
                    if not x_group.is_changed:
                        x_group.is_changed = True

        if x_group.is_changed:
            for node in x_group.nodes:
                for key in x_group.changed_common_features:
                    if x_group.changed_common_features[key] == 1:
                        node.real_changed_attrs[key] = 1

                self.changed_nodes.append(node)
                # 临时查看代码
                node.matched_node = y_sample_node

    def save_single_results(self):
        """
        保存最终的结果图
        :return:
        """

        single_path = self.output_path + '/' + 'single'
        if not os.path.exists(single_path):
            os.makedirs(single_path)

        base_img = cv2.imread(self.base_img_path)
        updated_img = cv2.imread(self.updated_img_path)

        for node in self.removed_nodes:
            if not node.is_in_list:
                x1, y1, x2, y2 = node.parse_bounds()
                base_img = cv2.rectangle(base_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        for node in self.changed_nodes:
            if not node.is_in_list:
                x1, y1, x2, y2 = node.parse_bounds()
                base_img = cv2.rectangle(base_img, (x1, y1), (x2, y2), (255, 0, 0), 2)

        for node in self.added_nodes:
            if not node.is_in_list:
                x1, y1, x2, y2 = node.parse_bounds()
                updated_img = cv2.rectangle(updated_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        cv2.imwrite(single_path + '/base.png', base_img)
        cv2.imwrite(single_path + '/updated.png', updated_img)

    def save_list_results(self):
        """
        计算滑动列表内部元素结果
        :return:
        """

        list_path = self.output_path + '/' + 'list'
        if not os.path.exists(list_path):
            os.makedirs(list_path)

        # 记录一下list元素的变化 写在记事本里面
        f = open(list_path + '/' + 'list_changes.txt', 'w')
        f.write('removed-----------' + '\n')
        for node in self.removed_nodes:
            if node.is_in_list and node.source_xml_id == 1:
                if node.attrib['class'] != 'android.view.View' and 'layout' not in node.attrib['class'].lower():
                    f.write('-------------' + '\n')
                    f.write(node.attrib['class'] + '\n')
                    f.write(node.attrib['resource-id'] + '\n')
                    f.write(node.attrib['text'] + '\n')
                    f.write(node.attrib['content-desc'] + '\n')

        f.write('changed-----------' + '\n')
        for node in self.changed_nodes:
            if node.is_in_list and node.source_xml_id == 1:
                if node.attrib['class'] != 'android.view.View' and 'layout' not in node.attrib['class'].lower():
                    f.write('-------------' + '\n')
                    f.write(node.attrib['class'] + '\n')
                    f.write(node.attrib['resource-id'] + '\n')
                    f.write(node.attrib['text'] + '\n')
                    f.write(node.attrib['content-desc'] + '\n')
                    f.write(str(node.real_changed_attrs) + '\n')

        f.write('added-----------' + '\n')
        for node in self.added_nodes:
            if node.is_in_list and node.source_xml_id == 1:
                if node.attrib['class'] != 'android.view.View' and 'layout' not in node.attrib['class'].lower():
                    f.write('-------------' + '\n')
                    f.write(node.attrib['class'] + '\n')
                    f.write(node.attrib['resource-id'] + '\n')
                    f.write(node.attrib['text'] + '\n')
                    f.write(node.attrib['content-desc'] + '\n')

        f.close()

        base_img = cv2.imread(self.base_img_path)
        updated_img = cv2.imread(self.updated_img_path)

        for node in self.removed_nodes:
            if node.is_in_list and node.source_xml_id == 1:
                x1, y1, x2, y2 = node.parse_bounds()
                base_img = cv2.rectangle(base_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        for node in self.changed_nodes:
            if node.is_in_list and node.source_xml_id == 1:
                x1, y1, x2, y2 = node.parse_bounds()
                base_img = cv2.rectangle(base_img, (x1, y1), (x2, y2), (255, 0, 0), 2)

        for node in self.added_nodes:
            if node.is_in_list and node.source_xml_id == 1:
                x1, y1, x2, y2 = node.parse_bounds()
                updated_img = cv2.rectangle(updated_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        cv2.imwrite(list_path + '/base.png', base_img)
        cv2.imwrite(list_path + '/updated.png', updated_img)

        # 再保存一下group的匹配结果
        group_path = list_path + '/' + 'group'
        if not os.path.exists(group_path):
            os.makedirs(group_path)

        count = 0
        for glist in self.base_complete_tree.glists:
            for group in glist.groups:
                if group.matched_group is not None and group.is_changed:
                    base_img = cv2.imread(self.base_img_path)
                    updated_img = cv2.imread(self.updated_img_path)
                    for node in group.nodes:
                        x1, y1, x2, y2 = node.parse_bounds()
                        base_img = cv2.rectangle(base_img, (x1, y1), (x2, y2), (255, 0, 0), 2)
                        cv2.imwrite(group_path + '/' + str(count) + 'group.png', base_img)

                    for node in group.matched_group.nodes:
                        x1, y1, x2, y2 = node.parse_bounds()
                        updated_img = cv2.rectangle(updated_img, (x1, y1), (x2, y2), (255, 0, 0), 2)
                        cv2.imwrite(group_path + '/' + str(count) + 'mathched_group.png', updated_img)

                count += 1


def get_matched_node_for_single_nodes(node, nodes_list, index):
    """
    为single_nodes 进行匹配
    :param is_normal:
    :param node:
    :param nodes_list:
    :return:
    """

    if index == 0:
        # 使用xpath进行唯一匹配

        # 首先获取xpath可以匹配上的节点列表
        for tmp_node in nodes_list:
            if tmp_node.matched_node_no == -1 and \
                    is_xpath_matched(node, tmp_node):
                node.matched_node_no = tmp_node.idx
                tmp_node.matched_node_no = node.idx
                break

    elif index == 1:

        # 使用str的相似度来计算得分 加了这玩意 反而精确率下降
        tmp_nodes_list = []
        for tmp_node in nodes_list:
            # 这里要求class相同 其实有的时候class也会变
            if tmp_node.matched_node_no == -1 and node.attrib['class'] == tmp_node.attrib['class']:
                tmp_nodes_list.append(tmp_node)

            max_sim = 0
            matched_node = None
            if tmp_nodes_list:
                # 然后找相似度最大的
                for tmp_node in tmp_nodes_list:
                    sim = get_str_sim(node, tmp_node)
                    if sim > max_sim:
                        max_sim = sim
                        matched_node = tmp_node

            if matched_node is not None:
                if max_sim >= 0.5:
                    node.matched_node_no = tmp_node.idx
                    tmp_node.matched_node_no = node.idx
    else:
        tmp_nodes_list = []
        for tmp_node in nodes_list:
            # 这里要求class相同 其实有的时候class也会变
            if tmp_node.matched_node_no == -1 and node.attrib['class'] == tmp_node.attrib['class']:
                tmp_nodes_list.append(tmp_node)

        if tmp_nodes_list != []:
            # 然后找最近邻的
            distances = [0] * len(tmp_nodes_list)

            index = 0
            for tmp_node in tmp_nodes_list:
                # 距离计算为xpath的雷文森距离 + 元素的位置和长宽距离
                dis = get_levenshtein_distance(node, tmp_node) + get_GUI_distance(node, tmp_node)
                distances[index] = dis
                index += 1

            min_dis = min(distances)
            min_index = -1

            for i in range(len(distances)):
                if min_dis == distances[i]:
                    min_index = i
                    break

            matched_node = tmp_nodes_list[min_index]

            # 最后在这里进行了限制
            flag = True
            if get_levenshtein_distance(node, matched_node) / max(len(node.xpath[0]), len(matched_node.xpath[0])) > 0.5:
                flag = False

            if abs(node.width - matched_node.width) / node.width > 0.3:
                flag = False

            if abs(node.height - matched_node.height) / node.height > 0.3:
                flag = False

            if abs(node.x_loc - matched_node.x_loc) / node.width > 1:
                flag = False

            if abs(node.y_loc - matched_node.y_loc) / node.height > 1:
                flag = False

            if flag:
                node.matched_node_no = matched_node.idx
                matched_node.matched_node_no = node.idx


def is_node_changed(x_node, y_node):
    """
    判断在跨版本中节点是否发生变化
    :param x_node:
    :param y_node:
    :return:
    """

    has_changed = False

    if x_node.attrib['resource-id'] != y_node.attrib['resource-id']:
        has_changed = True
        if x_node.dynamic_changed_attrs['resource-id'] == 0:
            x_node.real_changed_attrs['resource-id'] = 1
        if y_node.dynamic_changed_attrs['resource-id'] == 0:
            y_node.real_changed_attrs['resource-id'] = 1

    if x_node.attrib['text'] != y_node.attrib['text']:
        has_changed = True
        if x_node.dynamic_changed_attrs['text'] == 0:
            x_node.real_changed_attrs['text'] = 1
        if y_node.dynamic_changed_attrs['text'] == 0:
            y_node.real_changed_attrs['text'] = 1

    if x_node.attrib['content-desc'] != y_node.attrib['content-desc']:
        has_changed = True
        if x_node.dynamic_changed_attrs['content-desc'] == 0:
            x_node.real_changed_attrs['content-desc'] = 1
        if y_node.dynamic_changed_attrs['content-desc'] == 0:
            y_node.real_changed_attrs['content-desc'] = 1

    if is_location_changed(x_node, y_node, True):
        has_changed = True
        if x_node.dynamic_changed_attrs['location'] == 0:
            x_node.real_changed_attrs['location'] = 1
        if y_node.dynamic_changed_attrs['location'] == 0:
            y_node.real_changed_attrs['location'] = 1

    if is_size_changed(x_node, y_node, True):
        has_changed = True
        if x_node.dynamic_changed_attrs['size'] == 0:
            x_node.real_changed_attrs['size'] = 1
        if y_node.dynamic_changed_attrs['size'] == 0:
            y_node.real_changed_attrs['size'] = 1

    if is_image(x_node):
        if is_image_changed_2(x_node, y_node, x_node.img_path, y_node.img_path):
            has_changed = True
            if x_node.dynamic_changed_attrs['color'] == 0:
                x_node.real_changed_attrs['color'] = 1
            if y_node.dynamic_changed_attrs['color'] == 0:
                y_node.real_changed_attrs['color'] = 1

    return has_changed
