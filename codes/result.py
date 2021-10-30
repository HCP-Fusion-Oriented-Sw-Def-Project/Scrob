import os
from utility import *
from str_utility import delete_num_in_str


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

        # 被移除的节点 变化的节点 新增的节点 single_nodes
        self.removed_single_nodes = []
        self.matched_single_nodes = []
        self.changed_single_nodes = []
        self.added_single_nodes = []

        # 被移除的节点 变化的节点 新增的节点 cluster_nodes
        # 只记录聚类id 也就是list_clusters中的key
        self.removed_cluster_id = []
        self.matched_cluster_id = []
        self.changed_cluster_id = []
        # self.updated_changed_cluster_id = []
        self.added_cluster_id = []

        # 对比屏幕的宽度设置
        self.width = width

        # 对比所需要的完全树
        self.base_complete_tree = base_complete_tree
        self.updated_complete_tree = updated_complete_tree

        # 待比较的screen路径
        self.base_img_path = base_complete_tree.main_xml_tree.img_path
        self.updated_img_path = updated_complete_tree.main_xml_tree.img_path

    # def cluster_nodes_compare(self):
    #     """
    #     聚类节点对比
    #     首先对比出增删的聚类节点
    #     之后将这些聚类找出
    #     """
    #
    #     removed_cluster_nodes = []
    #     added_cluster_nodes = []
    #
    #     base_cluster_nodes = self.base_complete_tree.list_cluster_nodes
    #     updated_cluster_nodes = self.updated_complete_tree.list_cluster_nodes
    #
    #     # 获取增删的聚类
    #     for node in base_cluster_nodes:
    #         if not is_cluster_existed(node, updated_cluster_nodes):
    #             removed_cluster_nodes.append(node)
    #
    #     for node in updated_cluster_nodes:
    #         if not is_cluster_existed(node, base_cluster_nodes):
    #             added_cluster_nodes.append(node)
    #
    #     # 找出实际GUI中的这些增删的聚类节点
    #     x_leaf_nodes = self.base_complete_tree.main_xml_tree.leaf_nodes
    #     y_leaf_nodes = self.updated_complete_tree.main_xml_tree.leaf_nodes
    #
    #     # 找到删除的聚类节点
    #     # 存在问题 removed_cluster_nodes内部可能有重复 因为没有id的节点不能聚类在一起
    #     for node in x_leaf_nodes:
    #         flag = False
    #         for tmp_node in removed_cluster_nodes:
    #             if get_nodes_similar_score(node, tmp_node) >= 0.8:
    #                 flag = True
    #         if flag:
    #             self.removed_single_nodes.append(node)
    #
    #     # 找到增加的聚类节点
    #     for node in y_leaf_nodes:
    #         flag = False
    #         for tmp_node in added_cluster_nodes:
    #             if get_nodes_similar_score(node, tmp_node) >= 0.8:
    #                 flag = True
    #         if flag:
    #             self.added_single_nodes.append(node)

    def get_clusters_changes(self):
        """
        获取聚类的变化
        """

        for x_key in self.matched_cluster_id:
            has_changed = False
            x_node = self.base_complete_tree.list_clusters[x_key]['nodes'][0]
            x_common_attrs = self.base_complete_tree.list_clusters[x_key]['common_attrs']
            y_key = self.base_complete_tree.list_clusters[x_key]['matched_cluster_id']
            y_node = self.updated_complete_tree.list_clusters[y_key]['nodes'][0]

            if x_common_attrs['rel_location'] == 1 and \
                    is_rel_location_changed(x_node, y_node, False):
                has_changed = True
                self.base_complete_tree.list_clusters[x_key]['changed_attrs']['rel_location'] = 1

            if x_common_attrs['size'] == 1 and \
                    is_size_changed(x_node, y_node, False):
                has_changed = True
                self.base_complete_tree.list_clusters[x_key]['changed_attrs']['size'] = 1

            if x_common_attrs['resource-id'] == 1 and \
                    x_node.attrib['resource-id'] != y_node.attrib['resource-id']:
                has_changed = True
                self.base_complete_tree.list_clusters[x_key]['changed_attrs']['resource-id'] = 1

            if x_common_attrs['text'] == 1 and \
                    x_node.attrib['text'] != y_node.attrib['text']:
                has_changed = True
                self.base_complete_tree.list_clusters[x_key]['changed_attrs']['text'] = 1

            if x_common_attrs['content-desc'] == 1 and \
                    x_node.attrib['content-desc'] != y_node.attrib['content-desc']:
                has_changed = True
                self.base_complete_tree.list_clusters[x_key]['changed_attrs']['content-desc'] = 1

            if 'image' in x_node.attrib['class'].lower() and \
                    x_common_attrs['color'] == 1 and \
                    is_image_changed(x_node, y_node, self.base_img_path, self.updated_img_path):
                has_changed = True
                self.base_complete_tree.list_clusters[x_key]['changed_attrs']['color'] = 1

            if has_changed:
                self.changed_cluster_id.append(x_key)

    def list_clusters_compare(self):
        """
        聚类对比
        """

        base_list_clusters = self.base_complete_tree.list_clusters
        updated_list_clusters = self.updated_complete_tree.list_clusters

        for x_key in base_list_clusters.keys():
            x_node = base_list_clusters[x_key]['nodes'][0]
            for y_key in updated_list_clusters.keys():
                y_node = updated_list_clusters[y_key]['nodes'][0]
                if is_same_cluster(x_node, y_node, base_list_clusters[x_key]['common_attrs'],
                                   updated_list_clusters[y_key]['common_attrs']):
                    base_list_clusters[x_key]['matched_cluster_id'] = y_key
                    updated_list_clusters[y_key]['matched_cluster_id'] = x_key

        # 获得移除的聚类 以及匹配上的聚类
        for x_key in base_list_clusters.keys():
            if base_list_clusters[x_key]['matched_cluster_id'] == -1:
                if base_list_clusters[x_key]['nodes'][0].attrib['class'] != 'android.view.View' and \
                        'layout' not in base_list_clusters[x_key]['nodes'][0].attrib['class']:
                    self.removed_cluster_id.append(x_key)
            else:
                self.matched_cluster_id.append(x_key)

        # 获得增加的聚类
        for y_key in updated_list_clusters.keys():
            if updated_list_clusters[y_key]['matched_cluster_id'] == -1 and \
                    updated_list_clusters[y_key]['nodes'][0].attrib['class'] != 'android.view.View' and \
                    'layout' not in updated_list_clusters[y_key]['nodes'][0].attrib['class']:
                self.added_cluster_id.append(y_key)

    def get_matched_single_nodes(self, node, compare_nodes, is_extra):
        """
        对single_node进行匹配
        is_extra表示是否是从其它xml文件中的节点匹配
        """

        if not is_extra:
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
            if len(node.xpath) == 1 or 'image' in node.attrib['class'].lower():  # 说明只有绝对路径构造的xpath 或者只是图片
                for tmp_node in compare_nodes:
                    if tmp_node.matched_node is None and is_bounds_matched(node, tmp_node, self.width):
                        return True

                return False

    def single_nodes_compare(self):
        """
        非列表叶子节点对比
        """

        base_single_nodes = self.base_complete_tree.main_xml_tree.single_nodes
        base_extra_single_nodes = self.base_complete_tree.extra_single_nodes

        updated_single_nodes = self.updated_complete_tree.main_xml_tree.single_nodes
        updated_extra_single_nodes = self.updated_complete_tree.extra_single_nodes

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
            if not self.get_matched_single_nodes(node, updated_extra_single_nodes, True):
                self.removed_single_nodes.append(node)
            else:
                self.removed_single_nodes.append(node)

        for node in unmatched_updated_single_nodes:
            if not self.get_matched_single_nodes(node, base_extra_single_nodes, True):
                self.added_single_nodes.append(node)
            else:
                self.added_single_nodes.append(node)

        # 搜集匹配上的节点
        for node in base_single_nodes:
            if node.matched_node is not None:
                self.matched_single_nodes.append(node)

    def get_single_nodes_changes(self):
        """
        将匹配上的single节点进行对比
        识别变化
        """

        for node in self.matched_single_nodes:
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
                self.changed_single_nodes.append(node)
                node.has_changed = True

    def get_result(self):
        """
        获得最终对比的结果
        """

        self.single_nodes_compare()
        self.get_single_nodes_changes()

        self.list_clusters_compare()

        self.draw_meaningless_list_cluster_nodes()

        # self.get_clusters_changes()

        # self.draw_removed_single_nodes()
        # self.draw_changed_single_nodes()
        # self.draw_added_single_nodes()

        # self.draw_list_nodes()
        # self.draw_removed_cluster_nodes()
        # self.draw_changed_cluster_nodes()

        # self.draw_added_cluster_nodes()
        # self.draw_removed_list_style()
        # self.draw_added_list_style()

        # self.print_result()

    def draw_changed_single_nodes(self):
        """
        在图中画出变化的节点并打印
        """

        img = cv2.imread(self.base_img_path)

        for node in self.changed_single_nodes:
            if node.attrib['class'] != 'android.view.View' and \
                    'layout' not in node.attrib['class'].lower():
                x1, y1, x2, y2 = node.parse_bounds()
                img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        path = self.output_path + '/' + 'single_nodes'
        if not os.path.exists(path):
            os.makedirs(path)

        cv2.imwrite(path + '/' + 'changed_single_nodes.png', img)

    def draw_removed_single_nodes(self):
        """
        在图中画出移除的节点
        """

        img = cv2.imread(self.base_img_path)

        for node in self.removed_single_nodes:
            if node.attrib['class'] != 'android.view.View' and \
                    'layout' not in node.attrib['class'].lower():
                x1, y1, x2, y2 = node.parse_bounds()
                img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        path = self.output_path + '/' + 'single_nodes'

        if not os.path.exists(path):
            os.makedirs(path)

        cv2.imwrite(path + '/' + 'removed_single_nodes.png', img)

    def draw_added_single_nodes(self):
        """
        在图中画出新增的节点
        """

        img = cv2.imread(self.updated_img_path)

        for node in self.added_single_nodes:
            if node.attrib['class'] != 'android.view.View' and \
                    'layout' not in node.attrib['class'].lower():
                x1, y1, x2, y2 = node.parse_bounds()
                img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        path = self.output_path + '/' + 'single_nodes'

        if not os.path.exists(path):
            os.makedirs(path)

        cv2.imwrite(path + '/' + 'added_single_nodes.png', img)

    def draw_list_nodes(self):
        """
        对base_version以及updated_version都画出列表节点以及列表节点的父节点 用于验证
        """

        # base_version
        img = cv2.imread(self.base_img_path)
        for node in self.base_complete_tree.main_xml_tree.list_parent_nodes:
            x1, y1, x2, y2 = node.parse_bounds()
            img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        cv2.imwrite(self.output_path + '/' + 'base_list_parent_nodes.png', img)

        img = cv2.imread(self.base_img_path)
        for node in self.base_complete_tree.main_xml_tree.list_nodes:
            x1, y1, x2, y2 = node.parse_bounds()
            img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.imwrite(self.output_path + '/' + 'base_list_nodes.png', img)

        # updated_version
        img = cv2.imread(self.updated_img_path)
        for node in self.updated_complete_tree.main_xml_tree.list_parent_nodes:
            x1, y1, x2, y2 = node.parse_bounds()
            img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.imwrite(self.output_path + '/' + 'updated_list_parent_nodes.png', img)

        img = cv2.imread(self.updated_img_path)
        for node in self.updated_complete_tree.main_xml_tree.list_nodes:
            x1, y1, x2, y2 = node.parse_bounds()
            img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.imwrite(self.output_path + '/' + 'updated_list_nodes.png', img)

    def draw_removed_cluster_nodes(self):
        """
        画出减少的聚类节点
        """

        img = cv2.imread(self.base_img_path)
        for node in self.base_complete_tree.main_xml_tree.leaf_nodes:
            for key in self.removed_cluster_id:
                if node.cluster_id == key:
                    x1, y1, x2, y2 = node.parse_bounds()
                    img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        path = self.output_path + '/' + 'cluster_nodes'

        if not os.path.exists(path):
            os.makedirs(path)

        cv2.imwrite(path + '/' + 'removed_cluster_nodes.png', img)

    def draw_changed_cluster_nodes(self):
        """
        画出变化的聚类节点
        """

        img = cv2.imread(self.base_img_path)
        for node in self.base_complete_tree.main_xml_tree.leaf_nodes:
            for key in self.changed_cluster_id:
                if node.cluster_id == key:
                    x1, y1, x2, y2 = node.parse_bounds()
                    img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        path = self.output_path + '/' + 'cluster_nodes'

        if not os.path.exists(path):
            os.makedirs(path)

        cv2.imwrite(path + '/' + 'changed_cluster_nodes.png', img)

    def draw_added_cluster_nodes(self):
        """
        画出新增的聚类节点
        """
        img = cv2.imread(self.updated_img_path)
        for node in self.updated_complete_tree.main_xml_tree.leaf_nodes:
            for key in self.added_cluster_id:
                if node.cluster_id == key:
                    x1, y1, x2, y2 = node.parse_bounds()
                    img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        path = self.output_path + '/' + 'cluster_nodes'
        if not os.path.exists(path):
            os.makedirs(path)

        cv2.imwrite(path + '/' + 'added_cluster_nodes.png', img)

    def draw_removed_list_style(self):
        """
        画出减少的列表样式
        """

        img = cv2.imread(self.base_img_path)

        for node in self.base_complete_tree.main_xml_tree.list_nodes:
            flag = False
            for descendant in node.descendants:
                for key in self.removed_cluster_id:
                    if descendant.cluster_id == key:
                        flag = True

            if flag:
                x1, y1, x2, y2 = node.parse_bounds()
                img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        path = self.output_path + '/' + 'list_style'
        if not os.path.exists(path):
            os.makedirs(path)

        cv2.imwrite(path + '/' + 'removed_list_style.png', img)

    def draw_added_list_style(self):
        """
        画出增加的列表样式
        """

        img = cv2.imread(self.updated_img_path)

        for node in self.updated_complete_tree.main_xml_tree.list_nodes:
            flag = False
            for descendant in node.descendants:
                for key in self.added_cluster_id:
                    if descendant.cluster_id == key:
                        flag = True

            if flag:
                x1, y1, x2, y2 = node.parse_bounds()
                img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        path = self.output_path + '/' + 'list_style'
        if not os.path.exists(path):
            os.makedirs(path)

        cv2.imwrite(path + '/' + 'added_list_style.png', img)

    def draw_meaningless_list_cluster_nodes(self):
        """
        在列表中找出layout节点和android.view.View节点
        对base_version和updated_version分别找出
        """

        # base_version
        img = cv2.imread(self.base_img_path)
        for key in self.base_complete_tree.list_clusters.keys():
            nodes = self.base_complete_tree.list_clusters[key]['nodes']
            for node in nodes:
                if node.attrib['class'] == 'android.view.View':
                    # if node.attrib['class'] == 'android.view.View' or 'layout' in node.attrib['class']:
                    x1, y1, x2, y2 = node.parse_bounds()
                    img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        cv2.imwrite(self.output_path + '/' + 'base_meaningless_list_clusters_nodes.png', img)

        # updated_version
        img = cv2.imread(self.updated_img_path)
        for key in self.updated_complete_tree.list_clusters.keys():
            nodes = self.updated_complete_tree.list_clusters[key]['nodes']
            for node in nodes:
                if node.attrib['class'] == 'android.view.View':
                    # if node.attrib['class'] == 'android.view.View' or 'layout' in node.attrib['class']:
                    x1, y1, x2, y2 = node.parse_bounds()
                    img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        cv2.imwrite(self.output_path + '/' + 'updated_meaningless_list_clusters_nodes.png', img)

    def print_result(self):
        """
        打印结果
        """

        # print('removed_nodes:')
        # for node in self.removed_nodes:
        #     print(node.attrib)
        #     print('----')

        # print('changed_nodes:')
        # for node in self.changed_nodes:
        #     print(node.attrib)
        #     print('****')
        #     print(node.real_changed_attrs)
        #     print('----')

        # print('added_nodes:')
        # for node in self.added_nodes:
        #     print(node.attrib)
        #     print('----')

        print('removed_cluster_id')
        for key in self.removed_cluster_id:
            print(key)
            node = self.base_complete_tree.list_clusters[key]['nodes'][0]
            print(node.attrib)

        print('changed_cluster_id')
        for key in self.changed_cluster_id:
            print(key)
            node = self.base_complete_tree.list_clusters[key]['nodes'][0]
            print(node.attrib)
            print(self.base_complete_tree.list_clusters[key]['changed_attrs'])

        print('added_cluster_id')
        for key in self.added_cluster_id:
            print(key)
            node = self.updated_complete_tree.list_clusters[key]['nodes'][0]
            print(node.attrib)


def is_same_cluster(x_node, y_node, x_common_attrs, y_common_attrs):
    """
    跨版本比较两个聚类是否相同
    """

    if x_node.attrib['class'] != y_node.attrib['class']:
        return False

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

    if x_node_id == y_node_id:
        return True
    else:
        return False

    # if len(x_node_id) != 0 and len(y_node_id) != 0 and \
    #         delete_num_in_str(x_node_id) == delete_num_in_str(y_node_id) and \
    #         x_common_attrs['resource-id'] == 1 and \
    #         y_common_attrs['resource-id'] == 1:
    #     return True
    #
    # if len(x_node_text) != 0 and len(y_node_text) != 0 and \
    #         x_node_text == y_node_text and \
    #         x_common_attrs['text'] == 1 and \
    #         y_common_attrs['text'] == 1:
    #     return True
    #
    # if len(x_node_content) != 0 and len(y_node_content) != 0 and \
    #         x_node_content == y_node_content and \
    #         x_common_attrs['content-desc'] == 1 and \
    #         y_common_attrs['content-desc'] == 1:
    #     return True
    #
    # if x_common_attrs['rel_location'] == 1 and y_common_attrs['rel_location'] == 1 and \
    #         is_rel_bounds_matched(x_node, y_node, x_common_attrs):
    #     return True

    return False
