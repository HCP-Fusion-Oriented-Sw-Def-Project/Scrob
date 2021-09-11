import os
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw


class TreeNode():
    """
    xml树节点
    """
    def __init__(self, xml_node, level):
        self.xml_node = xml_node
        self.attrib = {}
        for key, value in xml_node.attrib.items():
            self.attrib[key] = xml_node.attrib[key]
        self.parent = None
        self.children = []
        self.descendants = []  # 节点的子孙节点
        self.changed_attributes = []
        self.is_changed = False
        self.id = -1  # 在结点数组中的id
        self.level = level  # 层级
        self.class_index = -1
        self.xpath = ''
        self.width = -1
        self.height = -1
        self.cluster_id = -1  # 所属集群id

    def parse_bounds(self):
        """
        解析bounds 获取节点坐标范围
        """
        bounds = self.attrib['bounds']
        str_1 = bounds.split(']')[0] + ']'
        x1 = str_1.split(',')[0]
        x1 = int(x1[1:])

        y1 = str_1.split(',')[1]
        y1 = int(y1[:-1])

        str_2 = bounds.split(']')[1] + ']'
        x2 = str_2.split(',')[0]
        x2 = int(x2[1:])

        y2 = str_2.split(',')[1]
        y2 = int(y2[:-1])

        # 返回元素左上角和右下角坐标
        return x1, y1, x2, y2

    def get_size(self):
        """
        获取节点的长和宽
        """
        if 'bounds' in self.attrib:
            x1, y1, x2, y2 = self.parse_bounds()
            self.width = x2 - x1
            self.height = y2 - y1

    def get_descendants(self, node):
        """
        获取所有子孙节点 dfs
        """
        if not node.children:
            return

        for child_node in node.children:
            self.descendants.append(child_node)
            self.get_descendants(child_node)


class XmlTree():
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
        if "package" in node.attrib and node.attrib["package"] == "com.android.systemui":
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
            xpath = parent_xpath + '/' + xpath_class_index
            node.xpath = xpath
            return xpath

    def get_nodes(self):
        self.dfs(self.root_node, None)

        for node in self.nodes:
            self.get_nodes_xpath(node)
            node.get_descendants(node)

        self.nodes = self.nodes[1:]  # 第一个根节点无实际含义

        return self.nodes


def main():
    tree = ET.ElementTree(file='../resources/d3.xml')
    img = Image.open('../resources/d3.png')
    xml_root = tree.getroot()
    root_node = TreeNode(xml_root, 0)
    xml_tree = XmlTree(root_node)
    nodes = xml_tree.get_nodes()

    print(nodes[0].attrib)


main()
