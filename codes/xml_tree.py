from tree_node import TreeNode


class XmlTree(object):
    """
    xml树 存储结点信息
    """

    def __init__(self, root_node):
        self.nodes = []
        self.root_node = root_node
        self.id = -1
        self.clusters = {}  # 聚类
        self.clusters_id = 1  # 聚类的id从1开始

    def dfs(self, node, parent):
        """
        深度优先 搜集节点
        """
        # 排除系统UI
        if 'package' in node.attrib and node.attrib['package'] == 'com.android.systemui':
            return

        node.parent = parent
        if parent is not None:
            node.ans_id = parent.id
        node.id = self.id
        node.get_size()
        self.nodes.append(node)
        self.id += 1

        children_xml_node = node.xml_node.getchildren()

        if len(children_xml_node) == 0:
            return

        # 记录结点的class_index 用于之后构造xpath使用
        class_count = {}
        # 构造子节点
        for xml_node in children_xml_node:
            child_node = TreeNode(xml_node, node.level + 1)
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

    def get_nodes_xpath(self, node):
        """
        构造节点的xpath
        """
        if node.parent is None:
            return "//"

        class_name = node.attrib['class']
        xpath_class_index = class_name + "[" + str(node.class_index) + "]"

        # 获得父节点xpath
        parent_node = node.parent

        parent_xpath = parent_node.xpath

        if parent_node.xpath == '':
            parent_xpath = self.get_nodes_xpath(parent_node)

        if parent_xpath != '//':
            xpath = parent_xpath + '/' + xpath_class_index
            node.xpath = xpath
            return xpath

        else:
            xpath = parent_xpath + xpath_class_index
            node.xpath = xpath
            return xpath

    def get_nodes(self):
        self.dfs(self.root_node, None)

        for node in self.nodes:
            self.get_nodes_xpath(node)
            node.get_descendants(node)

        self.nodes = self.nodes[1:]  # 第一个根节点无实际含义

        return self.nodes
