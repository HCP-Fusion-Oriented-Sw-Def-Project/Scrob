import os
from utility import *
from xml_tree import get_nodes_similar_score


class CompareResult(object):
    """
    结果类
    存储各个数据的路径
    输出路径
    以及变化的节点
    """

    def __init__(self, base_complete_tree, updated_complete_tree, width, output_path):
        # 基础版本数据 更新版本数据 以及输出 路径
        self.base_data_path = ''
        self.updated_data_path = ''

        self.output_path = output_path

        # 被移除的节点 变化的节点 新增的节点
        self.removed_nodes = []

        self.matched_nodes = []
        self.changed_nodes = []

        self.added_nodes = []

        # 对比屏幕的宽度设置
        self.width = width

        # 对比所需要的完全树
        self.base_complete_tree = base_complete_tree
        self.updated_complete_tree = updated_complete_tree

        # 待比较的screen路径
        self.base_img_path = base_complete_tree.main_xml_tree.img_path
        self.updated_img_path = updated_complete_tree.main_xml_tree.img_path

    def cluster_nodes_compare(self):
        """
        聚类节点对比
        首先对比出增删的聚类节点
        之后将这些聚类找出
        """

        removed_cluster_nodes = []
        added_cluster_nodes = []

        base_cluster_nodes = self.base_complete_tree.list_cluster_nodes
        updated_cluster_nodes = self.updated_complete_tree.list_cluster_nodes

        # 获取增删的聚类
        for node in base_cluster_nodes:
            if not is_cluster_existed(node, updated_cluster_nodes):
                removed_cluster_nodes.append(node)

        for node in updated_cluster_nodes:
            if not is_cluster_existed(node, base_cluster_nodes):
                added_cluster_nodes.append(node)

        # 找出实际GUI中的这些增删的聚类节点
        x_leaf_nodes = self.base_complete_tree.main_xml_tree.leaf_nodes
        y_leaf_nodes = self.updated_complete_tree.main_xml_tree.leaf_nodes

        # 找到删除的聚类节点
        # 存在问题 removed_cluster_nodes内部可能有重复 因为没有id的节点不能聚类在一起
        for node in x_leaf_nodes:
            flag = False
            for tmp_node in removed_cluster_nodes:
                if get_nodes_similar_score(node, tmp_node) >= 0.8:
                    flag = True
            if flag:
                self.removed_nodes.append(node)

        # 找到增加的聚类节点
        for node in y_leaf_nodes:
            flag = False
            for tmp_node in added_cluster_nodes:
                if get_nodes_similar_score(node, tmp_node) >= 0.8:
                    flag = True
            if flag:
                self.added_nodes.append(node)

    def get_matched_single_nodes(self, node, compare_nodes, is_added):
        """
        对single_node进行匹配
        is_added表示是否是从补充的节点匹配
        """

        if not is_added:
            # 使用xpath进行匹配
            for tmp_node in compare_nodes:
                if tmp_node.matched_node is None and is_xpath_matched(node, tmp_node):
                    node.matched_node = tmp_node
                    tmp_node.matched_node = node
                    return True

            # 使用bounds进行匹配
            if len(node.xpath) == 1 or 'image' in node.attrib['class'].lower():  # 说明只有绝对路径构造的xpath 或者只是图片
                for tmp_node in compare_nodes:
                    if tmp_node.matched_node is None and is_bounds_matched(node, tmp_node, self.width):
                        node.matched_node = tmp_node
                        tmp_node.matched_node = node
                        return True

                return False

        else:
            # 使用xpath进行匹配
            for tmp_node in compare_nodes:
                if tmp_node.matched_node is None and is_xpath_matched(node, tmp_node):
                    return True

            # 使用bounds进行匹配
            if len(node.xpath) == 1 or 'image' in node.attrib['class'].lower(): # 说明只有绝对路径构造的xpath 或者只是图片
                for tmp_node in compare_nodes:
                    if tmp_node.matched_node is None and is_bounds_matched(node, tmp_node, self.width):
                        return True

                return False

    def single_nodes_compare(self):
        """
        非列表叶子节点对比
        """

        base_single_nodes = self.base_complete_tree.main_xml_tree.single_nodes
        base_added_single_nodes = self.base_complete_tree.added_single_nodes

        updated_single_nodes = self.updated_complete_tree.main_xml_tree.single_nodes
        updated_added_single_nodes = self.updated_complete_tree.added_single_nodes

        unmatched_base_single_nodes = []
        unmatched_updated_single_nodes = []

        # 常规对比
        for node in base_single_nodes:
            if not self.get_matched_single_nodes(node, updated_single_nodes, False):
                unmatched_base_single_nodes.append(node)

        for node in updated_single_nodes:
            if node.matched_node is None:
                unmatched_updated_single_nodes.append(node)

        # 补充对比
        for node in unmatched_base_single_nodes:
            if not self.get_matched_single_nodes(node, updated_added_single_nodes, True):
                self.removed_nodes.append(node)
            else:
                self.removed_nodes.append(node)

        for node in unmatched_updated_single_nodes:
            if not self.get_matched_single_nodes(node, base_added_single_nodes, True):
                self.added_nodes.append(node)
            else:
                self.added_nodes.append(node)

        # 搜集匹配上的节点
        for node in base_single_nodes:
            if node.matched_node is not None:
                self.matched_nodes.append(node)

    def get_node_changes(self):
        """
        将匹配上的节点进行对比
        识别变化
        """

        for node in self.matched_nodes:
            has_changed = False
            matched_node = node.matched_node

            if node.dynamic_changed_attrs['class'] == 0 and \
                    node.attrib['class'] != matched_node.attrib['class']:
                node.real_changed_attrs['class'] = 1
                has_changed = True

            if node.dynamic_changed_attrs['resource-id'] == 0 and \
                    node.attrib['resource-id'] != matched_node.attrib['resource-id']:
                node.real_changed_attrs['resource-id'] = 1
                has_changed = True

            if node.dynamic_changed_attrs['text'] == 0 and \
                    node.attrib['text'] != matched_node.attrib['text']:
                node.real_changed_attrs['text'] = 1
                has_changed = True

            if node.dynamic_changed_attrs['content-desc'] == 0 and \
                    node.attrib['content-desc'] != matched_node.attrib['content-desc']:
                node.real_changed_attrs['text'] = 1
                has_changed = True

            if node.dynamic_changed_attrs['location'] == 0 and \
                    is_location_changed(node, matched_node, False):
                node.real_changed_attrs['location'] = 1
                has_changed = True

            if node.dynamic_changed_attrs['size'] == 0 and \
                    is_size_changed(node, matched_node, False):
                node.real_changed_attrs['size'] = 1
                has_changed = True

            if 'image' in node.attrib['class'].lower() and \
                    node.dynamic_changed_attrs['color'] == 0 and \
                    is_image_changed(node, matched_node, self.base_img_path, self.updated_img_path):
                node.real_changed_attrs['color'] = 1
                has_changed = True

            if has_changed:
                self.changed_nodes.append(node)
                node.has_changed = True

    def get_result(self):
        """
        获得最终对比的结果
        """

        self.cluster_nodes_compare()
        self.single_nodes_compare()
        self.get_node_changes()

        self.draw_removed_nodes()
        self.draw_changed_nodes()
        self.draw_added_nodes()

    def draw_changed_nodes(self):
        """
        在图中画出变化的节点并打印
        """

        img = cv2.imread(self.base_img_path)

        for node in self.changed_nodes:
            if node.attrib['class'] != 'android.view.View' and \
                    'layout' not in node.attrib['class'].lower():
                x1, y1, x2, y2 = node.parse_bounds()
                img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        cv2.imwrite(self.output_path + '/' + 'changed_nodes.png', img)

        print('changed_nodes:')
        for node in self.changed_nodes:
            print(node.attrib)
            print('----')


    def draw_removed_nodes(self):
        """
        在图中画出移除的节点
        """

        img = cv2.imread(self.base_img_path)

        for node in self.removed_nodes:
            if node.attrib['class'] != 'android.view.View' and \
                    'layout' not in node.attrib['class'].lower():
                x1, y1, x2, y2 = node.parse_bounds()
                img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        cv2.imwrite(self.output_path + '/' + 'removed_nodes.png', img)

        print('removed_nodes:')
        for node in self.removed_nodes:
            print(node.attrib)
            print('----')

    def draw_added_nodes(self):
        """
        在图中画出移除的节点
        """

        img = cv2.imread(self.updated_img_path)

        for node in self.added_nodes:
            if node.attrib['class'] != 'android.view.View' and \
                    'layout' not in node.attrib['class'].lower():
                x1, y1, x2, y2 = node.parse_bounds()
                img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        cv2.imwrite(self.output_path + '/' + 'added_nodes.png', img)

        print('added_nodes:')
        for node in self.added_nodes:
            print(node.attrib)
            print('----')


def is_cluster_existed(node, compared_nodes):
    """
    判断聚类节点是否在另一个版本中存在
    """

    for tmp_node in compared_nodes:
        sim = get_nodes_similar_score(node, tmp_node)
        if sim >= 0.8:
            return True

    return False
