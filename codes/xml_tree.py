import xml.etree.ElementTree as ET

from cluster import TreeNodeCluster, get_nodes_similar_score, is_similar
from glist import GList
from tree_node import TreeNode
from utility import *


class CompleteTree(object):
    """
    版本树 将同版本多个xml的信息进行合并
    合并 聚类 (只对列表内部的元素)
    最终 对比将会使用到这个树
    目前只使用动态节点进行聚类
    """

    def __init__(self, xml_tree_list, main_xml_tree):
        self.xml_tree_list = xml_tree_list  # 存储各版本的xml_tree

        #  初始化xml_tree_list的树编号
        for i in range(len(xml_tree_list)):
            for node in xml_tree_list[i].nodes:
                node.source_xml_id = i + 1

        self.main_xml_tree = main_xml_tree  # 主要用于对比的xml树

        self.glists = []

        # 不在列表中的节点
        self.single_nodes = []

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
        获取各个树的list_nodes 这个函数要在动态元素标记之后进行
        :return:
        """

        for xml_tree in self.xml_tree_list:
            xml_tree.get_list_nodes()

    def divide_list_nodes(self):
        """
        对list nodes 按照父节点进行划分
        :return:
        """

        for node in self.main_xml_tree.list_nodes:
            parent_node = node.parent
            flag = False
            for glist in self.glists:
                if parent_node.xpath[0] == glist.root.xpath[0]:
                    flag = True
                    glist.nodes.append(node)

            # 不断地创建列表节点的集合 glists
            if not flag:
                glist = GList(parent_node)
                glist.nodes.append(node)
                self.glists.append(glist)

        # 然后将同版本其他xml树中的列表节点加入 相当于列表的合并
        for xml_tree in self.xml_tree_list:
            if xml_tree != self.main_xml_tree:
                for node in xml_tree.list_nodes:
                    parent_node = node.parent
                    flag = False
                    for glist in self.glists:
                        # if parent_node.xpath[0] == glist.root.xpath[0]:
                        if parent_node.attrib['bounds'] == glist.root.attrib['bounds']:
                            flag = True
                            glist.nodes.append(node)
                    if not flag:
                        glist = GList(parent_node)
                        glist.nodes.append(node)
                        self.glists.append(glist)

    def collect_leaf_nodes_in_list(self):
        """
        搜集各个列表中的叶子节点
        并对它们的特性进行统计分析 如在单版本内的大小 尺寸如何
        :return:
        """

        for glist in self.glists:
            for node in glist.nodes:
                for desc in node.descendants:
                    if not desc.children:
                        desc.is_in_list = True
                        # 构造节点的相对坐标
                        desc.construct_rel_bounds(node)
                        desc.construct_rel_xpath(node)
                        glist.leaf_desc.append(desc)

    def group_glist_leaf_desc(self):
        """
        将glist中的叶子节点进行分组
        :return:
        """

        for glist in self.glists:
            glist.group_leaf_desc()

    def address_list_nodes(self):
        """
        对列表节点进行处理
        :return:
        """

        self.get_tree_list_nodes()
        self.divide_list_nodes()
        self.collect_leaf_nodes_in_list()
        self.group_glist_leaf_desc()

    def get_single_nodes(self):
        """
        获得不在列表中的叶子节点
        :return:
        """

        for node in self.main_xml_tree.leaf_nodes:
            if not node.is_in_list:
                self.single_nodes.append(node)

    def initialize(self):
        """
        初始化complete tree
        :return:
        """

        self.tag_for_nodes()
        self.address_list_nodes()
        self.get_single_nodes()


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
            # 记录节点的图片信息
            node.img_path = self.img_path
            self.get_nodes_full_xpath(node)
            node.get_descendants(node)
            if not node.children:
                self.leaf_nodes.append(node)
            else:
                if 'roation' not in node.attrib.keys():
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
        即将自顶向下聚类失败的元素进行聚类
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

        tmp_clusters = self.clusters.copy()

        for cluster_id in tmp_clusters:
            cluster = tmp_clusters[cluster_id]
            if not cluster.is_leaf:
                nodes = cluster.nodes
                # has_id_used = False
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

                                # 修改后不对之前的cluster_id进行重用
                                tmp_cluster = TreeNodeCluster(self.cluster_id)
                                tmp_cluster.layer = x_node.layer
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
                        if has_common_desc(x_node, y_node) and y_nodes[0].layer < x_nodes[0].layer:
                            flag = False

            if flag:
                tmp_clusters[x_cluster_id] = self.clusters[x_cluster_id]
            else:
                # 將原cluster中的元素cluster_id置為-1
                for node in self.clusters[x_cluster_id].nodes:
                    node.cluster_id = -1

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

        # 对list_root_nodes 进行去重处理
        # 首先按照层级排序 从大到小排序
        self.list_root_nodes.sort(key=lambda node: node.layer, reverse=True)

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
                    # cluster = self.clusters[node.children[k].cluster_id]
                    try:
                        cluster = self.clusters[node.children[k].cluster_id]
                    except Exception as e:
                        print(node.children[k - 1].cluster_id)
                        print(node.children[k].cluster_id)
                        print(self.clusters)
                        # print(e)
                        # print(node.children[k].attrib)
                        # print(node.attrib)

                    count = 0
                    for tmp_node in cluster.nodes:
                        # 看看该聚类中动态元素列表的数量是否大于0.5
                        if tmp_node in self.list_nodes:
                            count += 1
                    if count / len(cluster.nodes) >= 0.5:
                        self.list_nodes.append(node.children[k])

                # 如果其左边兄弟节点为动态列表节点 那么其自身也该如此
                if node.children[k] not in self.list_nodes:
                    flag_left = False
                    for j in range(0, k):
                        if node.children[j] in self.list_nodes:
                            flag_left = True
                            break

                    if flag_left:
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

            if not cluster.nodes[0].children:
                cluster.is_leaf = True


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
