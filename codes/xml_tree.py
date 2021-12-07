import copy
import xml.etree.ElementTree as ET

from utility import *
from str_utility import delete_num_in_str
from tree_node import TreeNode
from cluster import TreeNodeCluster, get_nodes_similar_score, is_similar


# class CompleteTree(object):
#     """
#     版本树 将同版本多个xml的信息进行合并
#     合并 聚类 以及对非列表内部的节点进行补充
#     最终 对比将会使用到这个树 (discard)
#     """
#
#     def __init__(self, xml_tree_list, main_xml_tree):
#         # self.list_cluster_nodes = []  # 同版本多个xml文件节点聚类的集合 并且只存储列表节点下的聚类 每个节点就代表了一个聚类
#         # self.list_cluster_id = 1  # 重新对这些聚类进行编号
#         self.extra_single_nodes = []  # 从其它xml文件中获取的single_nodes 使用xpath来进行补充
#         self.xml_tree_list = xml_tree_list  # 存储各版本的xml_tree
#
#         #  初始化xml_tree_list的树编号
#         for i in range(len(xml_tree_list)):
#             for node in xml_tree_list[i].nodes:
#                 node.source_xml_id = i + 1
#
#         self.main_xml_tree = main_xml_tree  # 主要用于对比的xml树
#
#         # 直接复制 因为copy只能copy第一层 没用
#         self.list_clusters = self.main_xml_tree.list_clusters
#
#         # 沿用了已有id 自创了部分id 100之后的则是补充的
#         self.clusters_id = 100
#
#     def construct_extra_list_cluster(self, nodes, cluster_id):
#         """
#         构造列表中的聚类信息
#         """
#
#         self.list_clusters[cluster_id] = {}
#         self.list_clusters[cluster_id]['nodes'] = nodes
#         self.list_clusters[cluster_id]['common_attrs'] = {
#             'class': 1,
#             'resource-id': 1,
#             'text': 1,
#             'content-desc': 1,
#             'rel_location': 1,  # 相对于列表节点的坐标
#             'size': 1,
#             'color': 1
#         }
#
#         self.list_clusters[cluster_id]['changed_attrs'] = {
#             'class': 0,
#             'resource-id': 0,
#             'text': 0,
#             'content-desc': 0,
#             'rel_location': 0,  # 相对于列表节点的坐标
#             'size': 0,
#             'color': 0
#         }
#
#         # 匹配上的聚类
#         self.list_clusters[cluster_id]['matched_cluster_id'] = -1
#
#     def merge_list_clusters(self):
#         """
#         合并列表中的聚类
#         """
#
#         idx = 10000
#         # 遍历其它树
#         for xml_tree in self.xml_tree_list:
#             if xml_tree != self.main_xml_tree:
#                 for x_key in xml_tree.list_clusters:
#                     x_nodes = xml_tree.list_clusters[x_key]['nodes']
#                     central_node = x_nodes[0]
#                     flag = False
#                     for y_key in self.main_xml_tree.list_clusters:
#                         y_nodes = self.main_xml_tree.list_clusters[y_key]['nodes']
#                         node = y_nodes[0]
#                         sim = get_nodes_similar_score(central_node, node)
#                         if sim >= 0.8:
#                             flag = True
#                             # # 将其它xml文件内的聚类节点加入
#                             # for node in x_nodes:
#                             #     tmp_node = node.copy()
#                             #     tmp_node.idx = idx
#                             #     y_nodes.append(node)
#                             #     idx += 1
#
#                     if not flag:
#                         self.construct_extra_list_cluster(x_nodes, self.clusters_id)
#                         self.clusters_id += 1
#
#     def get_list_clusters_tag(self):
#         """
#         对列表内的聚类节点进行标记
#         找出是共性的属性
#         """
#
#         for key in self.list_clusters:
#             nodes = self.list_clusters[key]['nodes']
#
#             for i in range(len(nodes)):
#                 for j in range(i + 1, len(nodes)):
#                     x_node = nodes[i]
#                     y_node = nodes[j]
#                     if is_rel_location_changed(x_node, y_node, True):
#                         if self.list_clusters[key]['common_attrs']['rel_location'] == 1:
#                             self.list_clusters[key]['common_attrs']['rel_location'] = 0
#
#                     if is_size_changed(x_node, y_node, True):
#                         if self.list_clusters[key]['common_attrs']['size'] == 1:
#                             self.list_clusters[key]['common_attrs']['size'] = 0
#
#                     if x_node.attrib['text'] != y_node.attrib['text']:
#                         if self.list_clusters[key]['common_attrs']['text'] == 1:
#                             self.list_clusters[key]['common_attrs']['text'] = 0
#
#                     if x_node.attrib['content-desc'] != y_node.attrib['content-desc']:
#                         if self.list_clusters[key]['common_attrs']['content-desc'] == 1:
#                             self.list_clusters[key]['common_attrs']['content-desc'] = 0
#
#                     if 'image' in x_node.attrib['class'].lower() and \
#                             is_image_changed(x_node, y_node, self.main_xml_tree.img_path, self.main_xml_tree.img_path):
#                         if self.list_clusters[key]['common_attrs']['color'] == 1:
#                             self.list_clusters[key]['common_attrs']['color'] = 0
#
#     def get_extra_single_nodes(self):
#         """
#         非列表叶子节点合并
#         """
#
#         for xml_tree in self.xml_tree_list:
#             if xml_tree != self.main_xml_tree:
#                 single_nodes = xml_tree.single_nodes
#                 for x_node in single_nodes:
#                     flag = False
#                     for y_node in self.main_xml_tree.single_nodes:
#                         if x_node.full_xpath == y_node.full_xpath:
#                             flag = True
#
#                     if not flag:
#                         self.extra_single_nodes.append(x_node)
#
#     def initialize(self):
#         """
#         初始化complete_tree
#         """
#
#         # 首先进行标记
#         for i in range(len(self.xml_tree_list)):
#             for j in range(i, len(self.xml_tree_list)):
#                 get_nodes_tag(self.xml_tree_list[i], self.xml_tree_list[j])
#
#         # 进行节点划分
#         for xml_tree in self.xml_tree_list:
#             xml_tree.divide_nodes()
#
#         # 合并聚类
#         self.merge_list_clusters()
#         # 聚类标记
#         self.get_list_clusters_tag()
#
#         # 添加来自其它文件的single_nodes
#         self.get_extra_single_nodes()


class CompleteTree(object):
    """
    版本树 将同版本多个xml的信息进行合并
    合并 聚类 以及对非列表内部的节点进行补充
    最终 对比将会使用到这个树
    目前只使用动态节点进行聚类
    """

    def __init__(self, xml_tree_list, main_xml_tree):
        self.xml_tree_list = xml_tree_list  # 存储各版本的xml_tree

        # 静态节点的列表
        self.static_nodes = []

        #  初始化xml_tree_list的树编号
        for i in range(len(xml_tree_list)):
            for node in xml_tree_list[i].nodes:
                node.source_xml_id = i + 1

        self.main_xml_tree = main_xml_tree  # 主要用于对比的xml树

    def tag_for_nodes(self):
        """
        对所有树的节点的状态进行标记
        :return:
        """

        for i in range(len(self.xml_tree_list)):
            for j in range(i, len(self.xml_tree_list)):
                get_nodes_tag(self.xml_tree_list[i], self.xml_tree_list[j])

    def get_tree_list_nodes(self):
        """
        获取各个树的list_nodes
        :return:
        """

        for xml_tree in self.xml_tree_list:
            xml_tree.get_list_nodes()

    # def get_static_leaf_nodes(self):
    #     """
    #     获取静态叶子节点
    #     动态节点全部是以聚类的形式
    #     """
    #
    #     for node in self.main_xml_tree.leaf_nodes:
    #         if node.dynamic_changed_type == ChangedType.REMAIN:
    #             if not is_filter(node) and not node.is_in_combination:
    #                 self.static_nodes.append(node)

    # def get_static_leaf_nodes_in_combination(self):
    #     """
    #     获取元素组合中的静态节点
    #     :return:
    #     """
    #
    #     clusters_to_be_removed = []
    #
    #     for cluster_id in self.main_xml_tree.clusters:
    #         cluster = self.main_xml_tree.clusters[cluster_id]
    #         count = 0
    #         for node in cluster.nodes:
    #             if has_dynamic_desc(node):
    #                 count += 1
    #
    #         if count / len(cluster.nodes) < 0.5:
    #             self.extract_static_nodes_from_cluster(cluster_id)
    #             clusters_to_be_removed.append(cluster_id)
    #
    #     # 删除原静态节点的组合聚类
    #     for cluster_id in clusters_to_be_removed:
    #         del self.main_xml_tree.clusters[cluster_id]

    # def extract_static_nodes_from_cluster(self, cluster_id):
    #     """
    #     从组合聚类中提取静态节点
    #     :return:
    #     """
    #
    #     cluster = self.main_xml_tree.clusters[cluster_id]
    #
    #     for node in cluster.nodes:
    #         for desc in node.descendants:
    #             if not desc.children:
    #                 self.static_nodes.append(desc)

    def initialize(self):
        """
        初始化complete tree
        :return:
        """

        self.tag_for_nodes()
        # self.get_static_leaf_nodes()
        # self.get_static_leaf_nodes_in_combination()

    # def merge_cluster(self):
    #     """
    #     合并节点间的聚类
    #     主要是从其它的xml信息中获取新的聚类
    #     """
    #     pass


class XmlTree(object):
    """
    xml树 存储结点信息
    """

    def __init__(self, root_node, img_path):
        self.nodes = []  # 按照dfs搜集的节点 顺序为深度优先搜索
        self.root_node = root_node
        self.id = -1  # 深度优先搜索中节点的序号
        self.layers = {}  # 层次 用于搜集每一层的叶子节点

        self.clusters = {}  # 聚类 对所有节点进行
        self.cluster_id = 1  # 聚类的id从1开始

        # 叶子节点
        self.leaf_nodes = []
        # 分支节点
        self.branch_nodes = []

        # 以下变量用于统计叶子各个属性的数量 用于构造xpath
        self.leaf_resource_id_count = {}
        self.leaf_text_count = {}
        self.leaf_content_count = {}

        # 用于统计分支节点的各个属性的数量 用于构造xpath
        self.branch_resource_id_count = {}
        self.branch_text_count = {}
        self.branch_content_count = {}

        # 对应图片的路径信息
        self.img_path = img_path

        # 动态列表的根节点
        self.list_root_nodes = []

        # 动态列表节点
        self.list_nodes = []

    def dfs(self, node, parent):
        """
        深度优先 搜集节点
        """
        # 排除系统UI
        if 'package' in node.attrib and node.attrib['package'] == 'com.android.systemui':
            return

        node.parent = parent

        node.idx = self.id
        node.get_bounds()
        self.nodes.append(node)
        self.id += 1

        if node.layer not in self.layers:
            self.layers[node.layer] = [node.idx]  # 更新为直接存储节点
        else:
            self.layers[node.layer].append(node.idx)

        children_xml_node = node.xml_node.getchildren()

        if len(children_xml_node) == 0:
            return

        # 记录结点的class_index 用于之后构造full_xpath使用
        class_count = {}
        # 构造子节点
        for xml_node in children_xml_node:

            if 'package' in xml_node.attrib and xml_node.attrib['package'] == 'com.android.systemui':
                continue

            child_node = TreeNode(xml_node, node.layer + 1)
            class_name = child_node.attrib['class']

            if class_name not in class_count.keys():
                class_count[class_name] = 1
                child_node.class_index = 1
                class_count[class_name] += 1
            else:
                child_node.class_index = class_count[class_name]
                class_count[class_name] += 1

            node.children.append(child_node)

        for child_node in node.children:
            self.dfs(child_node, node)

    def get_nodes_full_xpath(self, node):
        """
        构造节点的full_xpath
        """
        if node.parent is None:
            node.full_xpath = '//'
            return "//"

        class_name = node.attrib['class']
        xpath_class_index = class_name + "[" + str(node.class_index) + "]"

        # 获得父节点xpath
        parent_node = node.parent

        parent_full_xpath = parent_node.full_xpath

        if parent_node.full_xpath == '':
            parent_full_xpath = self.get_nodes_full_xpath(parent_node)

        if parent_full_xpath != '//':
            full_xpath = parent_full_xpath + '/' + xpath_class_index
            node.full_xpath = full_xpath
            return full_xpath

        else:
            full_xpath = parent_full_xpath + xpath_class_index
            node.full_xpath = full_xpath
            return full_xpath

    def get_nodes_stat(self):
        """
        统计节点属性的数目 叶子节点与叶间节点分开统计
        """
        # 叶子节点 resource-id text content-desc
        for node in self.leaf_nodes:
            resource_id = node.attrib['resource-id']
            text = node.attrib['text']
            content = node.attrib['content-desc']

            if resource_id not in self.leaf_resource_id_count:
                self.leaf_resource_id_count[resource_id] = 1
            else:
                self.leaf_resource_id_count[resource_id] += 1

            if text not in self.leaf_text_count:
                self.leaf_text_count[text] = 1
            else:
                self.leaf_text_count[text] += 1

            if content not in self.leaf_content_count:
                self.leaf_content_count[content] = 1
            else:
                self.leaf_content_count[content] += 1

        # 分支节点 resource-id text content-desc
        for node in self.branch_nodes:
            if node.full_xpath == '//':
                continue
            resource_id = node.attrib['resource-id']
            text = node.attrib['text']
            content = node.attrib['content-desc']

            if resource_id not in self.branch_resource_id_count:
                self.branch_resource_id_count[resource_id] = 1
            else:
                self.branch_resource_id_count[resource_id] += 1

            if text not in self.branch_text_count:
                self.branch_text_count[text] = 1
            else:
                self.branch_text_count[text] += 1

            if content not in self.branch_content_count:
                self.branch_content_count[content] = 1
            else:
                self.branch_content_count[content] += 1

    def get_nodes_ans(self, node):
        """
        获取能够唯一用xpath定位的祖先节点
        """

        # 根节点
        if node.full_xpath == '//':
            return None

        # 说明不仅仅有full_xpath一个
        if len(node.xpath) > 1:
            return node
        else:
            return self.get_nodes_ans(node.parent)

    def get_nodes_xpath_by_ans(self, cur_node):
        """
        使用祖先节点的xpath来构造节点的xpath
        """
        ans_node = self.get_nodes_ans(cur_node.parent)

        if ans_node is None:
            return ''

        node_class_name = cur_node.attrib['class']
        node_resource_id = cur_node.attrib['resource-id']
        node_text = cur_node.attrib['text']
        node_content = cur_node.attrib['content-desc']

        resource_id_count = {}
        text_count = {}
        content_count = {}

        # 统计子孙节点中节点的属性
        if cur_node.children:
            for node in ans_node.descendants:
                if node.children:
                    resource_id = node.attrib['resource-id']
                    text = node.attrib['text']
                    content = node.attrib['content-desc']

                    if resource_id not in resource_id_count:
                        resource_id_count[resource_id] = 1
                    else:
                        resource_id_count[resource_id] += 1

                    if text not in text_count:
                        text_count[text] = 1
                    else:
                        text_count[text] += 1

                    if content not in content_count:
                        content_count[content] = 1
                    else:
                        content_count[content] += 1
        else:
            for node in ans_node.descendants:
                if not node.children:
                    resource_id = node.attrib['resource-id']
                    text = node.attrib['text']
                    content = node.attrib['content-desc']

                    if resource_id not in resource_id_count:
                        resource_id_count[resource_id] = 1
                    else:
                        resource_id_count[resource_id] += 1

                    if text not in text_count:
                        text_count[text] = 1
                    else:
                        text_count[text] += 1

                    if content not in content_count:
                        content_count[content] = 1
                    else:
                        content_count[content] += 1

        if node_resource_id in resource_id_count and \
                resource_id_count[node_resource_id] == 1:
            xpath = ans_node.xpath[1] + '/' + node_class_name + '[' + '@resource-id=' + '"' + resource_id + '"' + ']'
            return xpath

        if node_text in text_count and \
                text_count[node_text] == 1:
            xpath = ans_node.xpath[1] + '/' + node_class_name + '[' + '@text=' + '"' + text + '"' + ']'
            return xpath

        if node_content in content_count and \
                content_count[node_content] == 1:
            xpath = ans_node.xpath[1] + '/' + node_class_name + '[' + '@content=' + '"' + text + '"' + ']'
            return xpath

        return ''

    def get_branch_nodes_xpath(self):
        """
        构造分支节点的xpath用于定位
        """

        # 先对分支节点按照层次排序
        self.branch_nodes.sort(key=lambda x: x.layer)

        for node in self.branch_nodes:

            node.xpath.append(node.full_xpath)

            if node.full_xpath == '//':
                continue

            class_name = node.attrib['class']
            resource_id = node.attrib['resource-id']
            text = node.attrib['text']
            content = node.attrib['content-desc']

            # 分支节点只需要一个非full_xpath的xpath即可 所以使用的是continue
            if resource_id in self.branch_resource_id_count and self.branch_resource_id_count[resource_id] == 1:
                xpath = '//' + class_name + '[' + '@resource-id=' + '"' + resource_id + '"' + ']'
                node.xpath.append(xpath)
                continue

            if text in self.branch_text_count and self.branch_text_count[text] == 1:
                xpath = '//' + class_name + '[' + '@text=' + '"' + text + '"' + ']'
                node.xpath.append(xpath)
                continue

            if content in self.branch_content_count and self.branch_content_count[content] == 1:
                xpath = '//' + class_name + '[' + '@content=' + '"' + text + '"' + ']'
                node.xpath.append(xpath)
                continue

            id_text_count = 0
            id_content_count = 0
            text_content_count = 0
            id_text_content_count = 0

            for tmp_node in self.branch_nodes:
                if tmp_node.full_xpath == '//':
                    continue
                if tmp_node.attrib['resource-id'] == resource_id and \
                        tmp_node.attrib['text'] == text:
                    id_text_count += 1

                if tmp_node.attrib['resource-id'] == resource_id and \
                        tmp_node.attrib['content-desc'] == content:
                    id_content_count += 1

                if tmp_node.attrib['text'] == text and \
                        tmp_node.attrib['content-desc'] == content:
                    text_content_count += 1

                if tmp_node.attrib['resource-id'] == resource_id and \
                        tmp_node.attrib['text'] == text and \
                        tmp_node.attrib['content-desc'] == content:
                    id_text_content_count += 1

            if id_text_count == 1:
                xpath = ('//' + class_name + '[' +
                         '@resource-id=' + '"' + resource_id + '"' +
                         '&&' + '@text=' + '"' + text + '"' + ']')
                node.xpath.append(xpath)
                continue

            if id_content_count == 1:
                xpath = ('//' + class_name + '[' +
                         '@resource-id=' + '"' + resource_id + '"' +
                         '&&' + '@content-desc=' + '"' + content + '"' + ']')
                node.xpath.append(xpath)
                continue

            if text_content_count == 1:
                xpath = ('//' + class_name + '[' +
                         '@text=' + '"' + text + '"' +
                         '&&' + '@content-desc=' + '"' + content + '"' + ']')
                node.xpath.append(xpath)
                continue

            if id_text_content_count == 1:
                xpath = ('//' + class_name + '[' +
                         '@resource-id=' + '"' + resource_id + '"' +
                         '&&' + '@text=' + '"' + text + '"' +
                         '&&' + '@content-desc=' + '"' + content + '"' + ']')
                node.xpath.append(xpath)
                continue

            # 再次用祖先节点进行xpath构造
            xpath = self.get_nodes_xpath_by_ans(node)
            if xpath != '':
                node.xpath.append(xpath)

    def get_leaf_nodes_xpath(self):
        """
        构造叶子节点的xpath用于定位
        """

        for node in self.leaf_nodes:

            # 如果全部不满足 那就等于full_xpath
            # node.xpath = node.full_xpath
            node.xpath.append(node.full_xpath)

            class_name = node.attrib['class']
            resource_id = node.attrib['resource-id']
            text = node.attrib['text']
            content = node.attrib['content-desc']

            if resource_id in self.leaf_resource_id_count and self.leaf_resource_id_count[resource_id] == 1:
                xpath = '//' + class_name + '[' + '@resource-id=' + '"' + resource_id + '"' + ']'
                node.xpath.append(xpath)

            if text in self.leaf_text_count and self.leaf_text_count[text] == 1:
                xpath = '//' + class_name + '[' + '@text=' + '"' + text + '"' + ']'
                node.xpath.append(xpath)

            if content in self.leaf_content_count and self.leaf_content_count[content] == 1:
                xpath = '//' + class_name + '[' + '@content=' + '"' + text + '"' + ']'
                node.xpath.append(xpath)

            id_text_count = 0
            id_content_count = 0
            text_content_count = 0
            id_text_content_count = 0

            for tmp_node in self.leaf_nodes:
                if tmp_node.attrib['resource-id'] == resource_id and \
                        tmp_node.attrib['text'] == text:
                    id_text_count += 1

                if tmp_node.attrib['resource-id'] == resource_id and \
                        tmp_node.attrib['content-desc'] == content:
                    id_content_count += 1

                if tmp_node.attrib['text'] == text and \
                        tmp_node.attrib['content-desc'] == content:
                    text_content_count += 1

                if tmp_node.attrib['resource-id'] == resource_id and \
                        tmp_node.attrib['text'] == text and \
                        tmp_node.attrib['content-desc'] == content:
                    id_text_content_count += 1

            if id_text_count == 1:
                xpath = ('//' + class_name + '[' +
                         '@resource-id=' + '"' + resource_id + '"' +
                         '&&' + '@text=' + '"' + text + '"' + ']')
                node.xpath.append(xpath)

            if id_content_count == 1:
                xpath = ('//' + class_name + '[' +
                         '@resource-id=' + '"' + resource_id + '"' +
                         '&&' + '@content-desc=' + '"' + content + '"' + ']')
                node.xpath.append(xpath)

            if text_content_count == 1:
                xpath = ('//' + class_name + '[' +
                         '@text=' + '"' + text + '"' +
                         '&&' + '@content-desc=' + '"' + content + '"' + ']')
                node.xpath.append(xpath)

            if id_text_content_count == 1:
                xpath = ('//' + class_name + '[' +
                         '@resource-id=' + '"' + resource_id + '"' +
                         '&&' + '@text=' + '"' + text + '"' +
                         '&&' + '@content-desc=' + '"' + content + '"' + ']')
                node.xpath.append(xpath)

            # 如果只有full_xpath
            if len(node.xpath) == 1:
                # 再次用祖先节点进行xpath构造
                xpath = self.get_nodes_xpath_by_ans(node)
                if xpath != '':
                    node.xpath.append(xpath)

    def get_nodes_xpath(self):
        """
        获取所有节点的xpath属性
        如果节点依靠自身属性无法唯一定位
        则直接追溯到可以唯一定位的祖先节点
        """
        self.get_branch_nodes_xpath()
        self.get_leaf_nodes_xpath()

    def parse_nodes(self):
        self.dfs(self.root_node, None)

        for node in self.nodes:
            self.get_nodes_full_xpath(node)
            node.get_descendants(node)
            if not node.children:
                self.leaf_nodes.append(node)
            else:
                self.branch_nodes.append(node)

        for node in self.nodes[1:]:
            # 去除字符串的空格
            node.attrib['text'] = node.attrib['text'].replace(' ', '')
            node.attrib['content-desc'] = node.attrib['content-desc'].replace(' ', '')

        self.get_nodes_stat()
        self.get_nodes_xpath()

        self.nodes = self.nodes[1:]  # 第一个根节点无实际含义

        self.get_clusters_from_top_down()  # 必须放在 self.nodes = self.nodes[1:] 的后面

        self.get_remaining_leaf_cluster()
        self.divide_cluster()
        self.get_cluster_correction()

        self.get_rid_of_nested_cluster()
        self.get_list_root_nodes()

        # 必须要在tag完之后使用
        # self.get_list_nodes()

        # self.divide_nodes()

        return self.nodes

    def get_clusters_from_top_down(self):
        """
        自顶向下获取元素聚类
        """
        for level in self.layers:
            nodes_idx = self.layers[level]

            for i in range(len(nodes_idx)):
                for j in range(i + 1, len(nodes_idx)):
                    x_node_idx = nodes_idx[i]
                    y_node_idx = nodes_idx[j]

                    x_node = self.nodes[x_node_idx]
                    y_node = self.nodes[y_node_idx]

                    sim = get_nodes_similar_score(x_node, y_node)
                    if sim >= 0.8:
                        # x_node已经属于某个聚类
                        if x_node.cluster_id != -1 and y_node.cluster_id == -1:
                            if y_node not in self.clusters[x_node.cluster_id].nodes:
                                self.clusters[x_node.cluster_id].nodes.append(y_node)
                            y_node.cluster_id = x_node.cluster_id
                        # y_node 已经属于某个聚类
                        elif y_node.cluster_id != -1 and x_node.cluster_id == -1:
                            if x_node not in self.clusters[y_node.cluster_id].nodes:
                                self.clusters[y_node.cluster_id].nodes.append(x_node)
                            x_node.cluster_id = y_node.cluster_id
                        # x_node 和 y_node 暂时都不属于任何聚类
                        elif x_node.cluster_id == -1 and y_node.cluster_id == -1:
                            cluster = TreeNodeCluster(self.cluster_id)
                            cluster.layer = x_node.layer
                            cluster.nodes.append(x_node)
                            cluster.nodes.append(y_node)
                            x_node.cluster_id = self.cluster_id
                            y_node.cluster_id = self.cluster_id
                            self.clusters[self.cluster_id] = cluster
                            self.cluster_id += 1

    def get_remaining_leaf_cluster(self):
        """
        获取剩余的聚类
        即将自定向下聚类失败的元素进行聚类
        这些聚类都是以叶子节点的形式
        """

        for node in self.leaf_nodes:
            if node.cluster_id == -1:
                cluster = TreeNodeCluster(self.cluster_id)
                cluster.nodes.append(node)
                node.cluster_id = self.cluster_id
                self.clusters[self.cluster_id] = cluster
                self.cluster_id += 1

    def get_cluster_correction(self):
        """
        聚类修正
        自上而下进行聚类会导致某些分支节点聚类错误
        故可依据其子孙节点的相似性来进行修正
        """

        # # 先深拷贝一份clusters
        # tmp_clusters = copy.deepcopy(self.clusters)

        tmp_clusters = self.clusters.copy()

        for cluster_id in tmp_clusters:
            cluster = tmp_clusters[cluster_id]
            if not cluster.is_leaf:
                nodes = cluster.nodes
                has_id_used = False
                # 将cluster_id恢复初始化
                for node in nodes:
                    node.cluster_id = -1

                # 将原版置空
                self.clusters[cluster_id].nodes = []

                for i in range(len(nodes)):
                    for j in range(i + 1, len(nodes)):
                        x_node = nodes[i]
                        y_node = nodes[j]

                        if is_similar(x_node, y_node):
                            # x_node已经属于某个聚类
                            if x_node.cluster_id != -1 and y_node.cluster_id == -1:
                                if y_node not in self.clusters[x_node.cluster_id].nodes:
                                    self.clusters[x_node.cluster_id].nodes.append(y_node)
                                y_node.cluster_id = x_node.cluster_id
                            # y_node 已经属于某个聚类
                            elif y_node.cluster_id != -1 and x_node.cluster_id == -1:
                                if x_node not in self.clusters[y_node.cluster_id].nodes:
                                    self.clusters[y_node.cluster_id].nodes.append(x_node)
                                x_node.cluster_id = y_node.cluster_id
                            # x_node 和 y_node 暂时都不属于任何聚类
                            elif x_node.cluster_id == -1 and y_node.cluster_id == -1:

                                if not has_id_used:
                                    has_id_used = True
                                    self.clusters[cluster_id].nodes.append(x_node)
                                    self.clusters[cluster_id].nodes.append(y_node)
                                    x_node.cluster_id = cluster_id
                                    y_node.cluster_id = cluster_id
                                else:
                                    tmp_cluster = TreeNodeCluster(self.cluster_id)
                                    tmp_cluster.later = x_node.layer
                                    tmp_cluster.nodes.append(x_node)
                                    tmp_cluster.nodes.append(y_node)
                                    x_node.cluster_id = self.cluster_id
                                    y_node.cluster_id = self.cluster_id
                                    self.clusters[self.cluster_id] = tmp_cluster
                                    self.cluster_id += 1

        # 去除空的聚类
        tmp_clusters = {}
        for cluster_id in self.clusters:
            cluster = self.clusters[cluster_id]
            nodes = cluster.nodes
            if len(nodes) != 0:
                tmp_clusters[cluster_id] = cluster

        self.clusters = tmp_clusters

    def get_rid_of_nested_cluster(self):
        """
        去除非叶子节点间聚类的嵌套
        如不同的聚类间有公共的子孙节点
        则只保留层次较高的那个聚类
        """

        tmp_clusters = {}
        # 首先要对self.clusters 按照层级进行排序
        result = sorted(self.clusters.items(), key=lambda x: x[1].layer, reverse=True)  # 返回tuple类型的数组

        for tup in result:
            cluster_id = tup[0]
            cluster = tup[1]
            tmp_clusters[cluster_id] = cluster

        self.clusters = tmp_clusters

        tmp_clusters = {}
        # cluster_id 是按照层级排序的结果
        for x_cluster_id in self.clusters:
            flag = True
            for y_cluster_id in self.clusters:
                x_nodes = self.clusters[x_cluster_id].nodes
                y_nodes = self.clusters[y_cluster_id].nodes
                for x_node in x_nodes:
                    for y_node in y_nodes:
                        if has_common_desc(x_node, y_node) and y_cluster_id < x_cluster_id:
                            flag = False

            if flag:
                tmp_clusters[x_cluster_id] = self.clusters[x_cluster_id]

        self.clusters = tmp_clusters

    def get_list_root_nodes(self):
        """
        找到列表节点的根节点
        """

        for cluster_id in self.clusters:
            cluster = self.clusters[cluster_id]
            # 不是叶子节点的聚类
            if not cluster.nodes[0].children:
                for i in range(len(cluster.nodes)):
                    for j in range(i + 1, len(cluster.nodes)):
                        x_node = cluster.nodes[i]
                        y_node = cluster.nodes[j]
                        common_ans = get_nodes_common_ans(x_node, y_node)
                        if common_ans is not None and common_ans not in self.list_root_nodes:
                            self.list_root_nodes.append(common_ans)

        # print(len(self.list_root_nodes))
        # 对list_root_nodes 进行去重处理
        # 首先按照层级排序 从大到小排序
        self.list_root_nodes.sort(key=lambda node: node.layer, reverse=True)

        # for node in self.list_root_nodes:
        #     print(node.attrib)
        #     print(node.layer)
        #
        # print('---------------')

        if len(self.list_root_nodes) > 1:
            tmp_list_root_nodes = []
            for i in range(len(self.list_root_nodes)):
                flag = True
                for j in range(i + 1, len(self.list_root_nodes)):
                    x_node = self.list_root_nodes[i]
                    y_node = self.list_root_nodes[j]

                    # layer数越大 说明在树中的层次越低
                    if has_common_desc(x_node, y_node) and x_node.layer > y_node.layer:
                        flag = False

                if flag and x_node not in tmp_list_root_nodes:
                    tmp_list_root_nodes.append(x_node)

            # 最后一个是一定要加入的
            tmp_list_root_nodes.append(self.list_root_nodes[-1])

            self.list_root_nodes = tmp_list_root_nodes

        # for node in self.list_root_nodes:
        #     print(node.attrib)
        #
        # print('-------------')

    def get_list_nodes(self):
        """
        获取动态的列表节点
        需要在tag_nodes之后使用
        """

        # 首先找到有动态元素且属于聚类中的节点
        for node in self.list_root_nodes:
            for child in node.children:
                if has_dynamic_desc(child) and child.cluster_id != -1:
                    self.list_nodes.append(child)

        # 进行一次补丁
        for node in self.list_root_nodes:
            for k in range(len(node.children)):
                if node.children[k] not in self.list_nodes and node.children[k].cluster_id != -1:
                    cluster = self.clusters[node.children[k].cluster_id]
                    count = 0
                    for tmp_node in cluster.nodes:
                        if tmp_node in self.list_nodes:
                            count += 1
                    if count / len(cluster.nodes) >= 0.5:
                        self.list_nodes.append(node.children[k])

                if node.children[k] not in self.list_nodes:
                    flag_left = False
                    # flag_right = False
                    for j in range(0, k):
                        if node.children[j] in self.list_nodes:
                            flag_left = True
                            break

                    # for j in range(k + 1, len(node.children)):
                    #     if node.children[j] in self.list_nodes:
                    #         flag_right = True
                    #         break

                    if flag_left :
                        self.list_nodes.append(node.children[k])

        # 进行一次过滤
        tmp_list_nodes = []
        for node in self.list_nodes:
            if not is_filter_list_node(node, self.clusters):
                tmp_list_nodes.append(node)

        self.list_nodes = tmp_list_nodes

    def divide_cluster(self):
        """
        过滤聚类
        去除'layout'节点 暂时保留android.view.View
        也就是给cluster一个tag
        暂时弃用
        """

        for cluster_id in self.clusters:
            cluster = self.clusters[cluster_id]
            # if 'layout' in cluster.nodes[0].attrib['class']:
            #     cluster.filter = True

            # if cluster.nodes[0].attrib['class'] == 'android.view.View':
            #     cluster.filter = True

            if not cluster.nodes[0].children:
                cluster.is_leaf = True

    def divide_nodes(self):
        """
        给叶子节点做标记
        标记它们是否处于某一组合中
        """

        for cluster_id in self.clusters:
            cluster = self.clusters[cluster_id]
            if not cluster.is_leaf:
                for node in cluster.nodes:
                    for desc in node.descendants:
                        desc.is_in_combination = True

    # def construct_list_cluster(self, node):
    #     """
    #     构造列表中的聚类信息 (discard)
    #     """
    #
    #     self.list_clusters[node.cluster_id] = {}
    #     self.list_clusters[node.cluster_id]['nodes'] = [node]
    #     self.list_clusters[node.cluster_id]['common_attrs'] = {
    #         'class': 1,
    #         'resource-id': 1,
    #         'text': 1,
    #         'content-desc': 1,
    #         'rel_location': 1,  # 相对于列表节点的坐标
    #         'size': 1,
    #         'color': 1
    #     }
    #
    #     self.list_clusters[node.cluster_id]['changed_attrs'] = {
    #         'class': 0,
    #         'resource-id': 0,
    #         'text': 0,
    #         'content-desc': 0,
    #         'rel_location': 0,  # 相对于列表节点的坐标
    #         'size': 0,
    #         'color': 0
    #     }
    #
    #     self.list_clusters[node.cluster_id]['matched_cluster_id'] = -1

    # def get_list_clusters(self):
    #     """
    #     获取所有列表下的聚类编号 (discard)
    #     需在tag之后进行调用
    #     """
    #
    #     # 找到属性变化的节点
    #     changed_nodes = []
    #
    #     for node in self.leaf_nodes:
    #         if node.dynamic_changed_type != ChangedType.REMAIN:
    #             changed_nodes.append(node)
    #
    #     # 用于存储列表节点父节点的列表
    #     list_parent_nodes = []
    #
    #     for node in changed_nodes:
    #         if node.cluster_id != -1 and node.cluster_id not in self.attr_changed_clusters:
    #             id_list = self.clusters[node.cluster_id]
    #             self.attr_changed_clusters.add(node.cluster_id)
    #             node_i = self.nodes[id_list[0]]
    #             node_j = self.nodes[id_list[1]]
    #
    #             if node_i.parent != node_j.parent:
    #                 common_ans = get_nodes_common_ans(node_i, node_j)
    #
    #                 if common_ans not in list_parent_nodes and common_ans.full_xpath != '//':
    #                     list_parent_nodes.append(common_ans)
    #
    #     # 去重前先按照节点的层次对列表进行排序（与下面的去重算法实现有关)
    #     list_parent_nodes.sort(key=lambda node: node.layer)
    #
    #     # 给list_parent_nodes去重
    #     if len(list_parent_nodes) > 1:
    #         tmp_list_parent_nodes = []
    #         for i in range(len(list_parent_nodes)):
    #             flag = True
    #             for j in range(i + 1, len(list_parent_nodes)):
    #                 x_node = list_parent_nodes[i]
    #                 y_node = list_parent_nodes[j]
    #                 # layer数越大 说明在树中的层次越低
    #                 if has_common_desc(x_node, y_node) and x_node.layer > y_node.layer:
    #                     flag = False
    #
    #             if flag and x_node not in tmp_list_parent_nodes:
    #                 tmp_list_parent_nodes.append(x_node)
    #
    #         list_parent_nodes = tmp_list_parent_nodes
    #
    #     self.list_parent_nodes = list_parent_nodes
    #
    #     changed_list_nodes = []
    #
    #     # 找到列表根节点下的每一个包含变化子孙节点的列表节点 一般情况下 倘若能找到正常的列表节点根节点 则这一步没必要
    #     # 不行 这样有的没变化的列表就找不出来
    #     for node in list_parent_nodes:
    #         for child in node.children:
    #             if has_desc_in_changed_cls(child, self):
    #                 changed_list_nodes.append(child)
    #
    #     # 在这里含有变化的节点被视为是列表节点
    #     self.list_nodes = changed_list_nodes
    #
    #     # 遍历列表节点 将它们的子孙节点的聚类找出
    #     for node in changed_list_nodes:
    #         for descendant in node.descendants:
    #             if not descendant.children:
    #                 descendant.is_in_list = True
    #                 descendant.list_ans = node
    #                 descendant.construct_rel_bounds(node)
    #                 if descendant.cluster_id != -1:
    #                     if descendant.cluster_id not in self.list_clusters.keys():
    #                         self.construct_list_cluster(descendant)
    #                     else:
    #                         self.list_clusters[descendant.cluster_id]['nodes'].append(descendant)
    #                 else:
    #                     # 有的列表内部节点无法聚类 那么对它们更新创建聚类 一个节点为一类
    #                     descendant.cluster_id = self.clusters_id
    #                     self.clusters[self.clusters_id] = [descendant]
    #                     self.construct_list_cluster(descendant)
    #                     self.clusters_id += 1

    # def get_single_nodes(self):
    #     """
    #     获取非列表下的叶子节点 (discard)
    #     """
    #
    #     for node in self.leaf_nodes:
    #         if not node.is_in_list:
    #             self.single_nodes.append(node)
    #
    #     return self.single_nodes

    # def divide_nodes(self):
    #     """
    #     节点划分
    #     将节点划分为cluster_nodes以及single_nodes (discard)
    #     """
    #
    #     self.get_list_clusters()
    #     self.get_single_nodes()


def parse_xml(xml_path, img_path):
    """
    解析xml文件 返回一个树和树中所有的节点
    """
    tree = ET.ElementTree(file=xml_path)
    xml_root = tree.getroot()
    root_node = TreeNode(xml_root, 0)
    xml_tree = XmlTree(root_node, img_path)
    nodes = xml_tree.parse_nodes()
    return xml_tree, nodes
