import xml.etree.ElementTree as ET

from codes.utility import *
from str_utility import delete_num_in_str
from tree_node import TreeNode


class CompleteTree(object):
    """
    版本树 将同版本多个xml的信息进行合并
    合并 聚类 以及对非列表内部的节点进行补充
    最终 对比将会使用到这个树
    """

    def __init__(self, xml_tree_list, main_xml_tree):
        self.list_clusters_nodes = []  # 同版本多个xml文件节点聚类的集合 并且只存储列表节点下的聚类 每个节点就代表了一个聚类
        self.list_cluster_id = 1  # 重新对这些聚类进行编号
        self.added_single_nodes = []  # 从其它xml文件中获取的single_nodes 使用xpath来进行补充

        self.xml_tree_list = xml_tree_list  # 存储各版本的xml_tree

        self.main_xml_tree = main_xml_tree  # 主要用于对比的xml树

    def merge_cluster(self):
        """
        聚类合并
        """

        main_nodes = self.main_xml_tree.nodes
        #  首先以main_xml_tree的聚类为基准
        for cluster_id in self.main_xml_tree.list_clusters_id:
            idx_list = self.main_xml_tree.clusters[cluster_id]

            # 只用一个节点表示一个聚类 (比较不合理 之后需更改)
            self.list_clusters_nodes.append(main_nodes[idx_list[0]])

        # print(len(self.list_clusters_nodes))

        # 遍历其它树
        for xml_tree in self.xml_tree_list:
            if xml_tree != self.main_xml_tree:
                for cluster_id in xml_tree.list_clusters_id:
                    idx_list = xml_tree.clusters[cluster_id]
                    central_node = xml_tree.nodes[idx_list[0]]
                    flag = False
                    for node in self.list_clusters_nodes:
                        sim = get_nodes_similar_score(central_node, node)
                        if sim >= 0.8:
                            flag = True
                    if not flag:
                        self.list_clusters_nodes.append(central_node)

        # print(len(self.list_clusters_nodes))

    def get_added_single_nodes(self):
        """
        非列表叶子节点合并
        """

        for xml_tree in self.xml_tree_list:
            if xml_tree != self.main_xml_tree:
                single_nodes = xml_tree.get_single_nodes()
                for x_node in single_nodes:
                    flag = False
                    for y_node in self.main_xml_tree.get_single_nodes():
                        if x_node.full_xpath == y_node.full_xpath:
                            flag = True

                    if not flag:
                        self.added_single_nodes.append(x_node)





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
        self.clusters_id = 1  # 聚类的id从1开始
        self.attr_changed_clusters = set()  # 内部中存在元素会变化的聚类的id集合

        # 列表节点中的聚类编号
        self.list_clusters_id = set()

        # 叶子节点
        self.leaf_nodes = []
        # 分支节点
        self.branch_nodes = []
        # 非列表内部节点
        self.single_nodes = []

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
            self.layers[node.layer] = [node.idx]
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
                        if x_node.cluster_id != -1:
                            if y_node.idx not in self.clusters[x_node.cluster_id]:
                                self.clusters[x_node.cluster_id].append(y_node_idx)
                            y_node.cluster_id = x_node.cluster_id
                        # y_node 已经属于某个聚类
                        elif y_node.cluster_id != -1:
                            if x_node.idx not in self.clusters[y_node.cluster_id]:
                                self.clusters[y_node.cluster_id].append(x_node.idx)
                            x_node.cluster_id = y_node.cluster_id
                        # x_node 和 y_node 暂时都不属于任何聚类
                        else:
                            self.clusters[self.clusters_id] = []
                            self.clusters[self.clusters_id].append(x_node.idx)
                            self.clusters[self.clusters_id].append(y_node.idx)
                            x_node.cluster_id = self.clusters_id
                            y_node.cluster_id = self.clusters_id
                            self.clusters_id += 1

    def get_list_clusters(self):
        """
        获取所有列表下的聚类编号
        需在tag之后进行调用
        """

        # 找到属性变化的节点
        attr_changed_nodes = []

        for node in self.leaf_nodes:
            if node.changed_type != ChangedType.REMAIN:
                attr_changed_nodes.append(node)

        # 用于存储列表节点根节点的列表
        nodes_list = []

        for node in attr_changed_nodes:
            if node.cluster_id != -1 and node.cluster_id not in self.attr_changed_clusters:
                id_list = self.clusters[node.cluster_id]
                self.attr_changed_clusters.add(node.cluster_id)
                node_i = self.nodes[id_list[0]]
                node_j = self.nodes[id_list[1]]
                common_ans = get_nodes_common_ans(node_i, node_j)

                if common_ans not in nodes_list and common_ans.full_xpath != '//':
                    nodes_list.append(common_ans)

        # 遍历这些列表根节点的子孙节点 将它们的子孙节点的聚类找出
        for node in nodes_list:
            for descendant in node.descendants:
                if descendant.children == [] and descendant.cluster_id != -1:
                    descendant.is_in_list = True
                    self.list_clusters_id.add(descendant.cluster_id)

    def get_single_nodes(self):
        """
        获取非列表下的叶子节点
        """

        for node in self.leaf_nodes:
            if node.is_in_list is False:
                self.single_nodes.append(node)

        return self.single_nodes


def get_nodes_similar_score(x_node, y_node):
    """
    在同层次聚类的过程中判断两个叶子节点是否相似
    需要更改这种计算方式
    """
    x_node_id = x_node.attrib['resource-id']
    y_node_id = y_node.attrib['resource-id']

    flag = False
    id_sim = 0

    if len(x_node_id) == 0 or len(y_node_id) == 0:
        flag = True

    if x_node_id.find('/') != -1:
        x_node_id = x_node_id.split('/')[1]

    if y_node_id.find('/') != -1:
        y_node_id = y_node_id.split('/')[1]

    if delete_num_in_str(x_node_id) == delete_num_in_str(y_node_id) and not flag:
        return 1

    if x_node.width == y_node.width or x_node.height == y_node.height:
        return (0.8 + id_sim) / 2
    else:
        return 0


def parse_xml(file_name, img_path):
    """
    解析xml文件 返回一个树和树中所有的节点
    """
    tree = ET.ElementTree(file=file_name)
    xml_root = tree.getroot()
    root_node = TreeNode(xml_root, 0)
    xml_tree = XmlTree(root_node, img_path)
    nodes = xml_tree.parse_nodes()
    return xml_tree, nodes
