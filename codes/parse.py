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
        self.ans_id = -1  # 去除layout之后的祖先结点的id
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
        self.ans_bind = {}  # 绑定去除layout后 祖先节点与子孙节点 用于之后的聚类
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

    def delete_layout_level(self):
        """
        删除layout节点层
        获取新的祖先节点与其后代节点的绑定
        """
        ans_id_to = {}
        for node in self.nodes[1:]:
            if 'Layout' in node.attrib['class']:
                ans_id_to[node.id] = node.ans_id

        for node in self.nodes[1:]:
            ans_id = node.ans_id
            ans = self.to_ans(ans_id, ans_id_to)
            # 更新去除layout后的祖先节点
            node.ans_id = ans
            if ans in self.ans_bind and ans != -1:
                self.ans_bind[ans].append(node.id)
            else:
                self.ans_bind.update({ans: [node.id]})

    def to_ans(self, ans_id, ans_id_to):
        """
        找到去除layout后的祖先节点
        """
        if ans_id not in ans_id_to or ans_id == 0:
            return ans_id
        else:
            return self.to_ans(ans_id_to[ans_id], ans_id_to)

    def nodes_similar(self, node_1, node_2):
        """
        判断两个节点是否可以聚为一类
        """
        # if node_1.children == [] or node_2.children == []: # 只对非叶子节点进行聚类
        #     return False

        is_res_id_empty = False
        res_id_1 = node_1.attrib['resource-id']
        res_id_2 = node_2.attrib['resource-id']

        if res_id_1 == '' or res_id_2 == '':
            is_res_id_empty = True

        if res_id_1.find('/') != -1:
            res_id_1 = res_id_1.split('/')[1]

        if res_id_2.find('/') != -1:
            res_id_2 = res_id_2.split('/')[1]

        if delete_str_num(res_id_1) == delete_str_num(res_id_2) and not is_res_id_empty:
            return 1

        descendants_id_1 = []
        descendants_id_2 = []

        # for des in node_1.descendants:
        #     descendants_id_1.append(des.id)
        #
        # for des in node_2.descendants:
        #     descendants_id_2.append(des.id)

        if node_1.id in self.ans_bind:
            descendants_id_1 = self.ans_bind[node_1.id]

        if node_2.id in self.ans_bind:
            descendants_id_2 = self.ans_bind[node_2.id]

        descendant_sim = self.descendants_similar(descendants_id_1, descendants_id_2)

        if node_1.width == node_2.width or node_1.height == node_2.height:
            return (0.8 + descendant_sim) / 2
        else:
            return 0

    def descendants_similar(self, descendants_id_1, descendants_id_2):
        """
        计算节点后代的相似度
        """
        if descendants_id_1 == [] and descendants_id_2 == []:
            return 0
        else:
            descendants_class_sim = self.descendants_class_similar(descendants_id_1, descendants_id_2)
            return descendants_class_sim

    def descendants_class_similar(self, descendants_id_1, descendants_id_2):
        """
        判断后代class的相似度
        """
        classes_1 = []
        classes_2 = []

        for node_id in descendants_id_1:
            classes_1.append(self.nodes[node_id].attrib['class'])

        classes_1.sort()

        for node_id in descendants_id_2:
            classes_2.append(self.nodes[node_id].attrib['class'])

        classes_2.sort()

        counter = 0
        total = len(classes_1) + len(classes_2)

        for i in range(len(classes_1)):
            for j in range(len(classes_2)):
                if classes_1[i] == classes_2[j] and classes_1[i] != '-1' and classes_2[j] != '-1':
                    counter += 2
                    classes_1[i] = '-1'
                    classes_2[j] = '-1'

        return counter / total

    def is_ans(self, node_1, node_2):
        """
        判断两个节点是否是子孙关系
        """

        flag = False

        node_1_ans = node_1.parent

        while node_1_ans != node_2:
            if node_1_ans.id == 0:
                break
            node_1_ans = node_1_ans.parent

        if node_1_ans.id != 0:
            flag = True

        node_2_ans = node_2.parent

        while node_2_ans != node_1:
            if node_2_ans.id == 0:
                break
            node_2_ans = node_2_ans.parent

        if node_2_ans.id != 0:
            flag = True

        return flag

        # node_1_x1, node_1_y1, node_1_x2, node_1_y2 = node_1.parse_bounds()
        # node_2_x1, node_2_y1, node_2_x2, node_2_y2 = node_1.parse_bounds()
        #
        # flag = False
        #
        # if node_1_x1 <= node_2_x1 and \
        #         node_1_y1 <= node_2_y1 and \
        #         node_1_x2 >= node_2_x2 and \
        #         node_1_y2 >= node_2_y2:
        #     flag = True
        #
        # if node_2_x1 <= node_1_x1 and \
        #         node_2_y1 <= node_1_y1 and \
        #         node_2_x2 >= node_1_x2 and \
        #         node_2_y2 >= node_1_y2:
        #     flag = True
        #
        # return flag

    def get_node_clusters(self):
        """
        获得节点的聚类
        """
        self.delete_layout_level()

        for node_id in self.ans_bind:
            descendant_nodes_id = self.ans_bind[node_id]
            do_cluster = True
            # 如果节点都是'Layout'节点 则不做集群
            for decen_id in descendant_nodes_id:
                if 'Layout' in self.nodes[decen_id].attrib['class']:
                    do_cluster = False
                    break

            if not do_cluster:
                pass

            # 节点依次与自己的节点相比较
            if len(descendant_nodes_id) > 1:
                for i in range(len(descendant_nodes_id) - 1):
                    for j in range(i + 1, len(descendant_nodes_id)):
                        sim = self.nodes_similar(self.nodes[descendant_nodes_id[i]], self.nodes[descendant_nodes_id[j]])
                        if sim >= 0.8:
                            if self.nodes[descendant_nodes_id[i]].cluster_id != -1:
                                self.nodes[descendant_nodes_id[j]].cluster_id = self.nodes[
                                    descendant_nodes_id[i]].cluster_id
                            elif self.nodes[descendant_nodes_id[j]].cluster_id != -1:
                                self.nodes[descendant_nodes_id[i]].cluster_id = self.nodes[
                                    descendant_nodes_id[j]].cluster_id
                            else:
                                self.nodes[descendant_nodes_id[i]].cluster_id = self.clusters_id
                                self.nodes[descendant_nodes_id[j]].cluster_id = self.clusters_id
                                self.clusters_id += 1

        for node in self.nodes[1:]:
            if node.cluster_id != -1:
                if node.cluster_id not in self.clusters:
                    self.clusters[node.cluster_id] = [node.id]
                else:
                    self.clusters[node.cluster_id].append(node.id)

    def filter_clusters(self):
        """
        去除底层一些节点的聚类
        """

        filter_cluster_id = set()
        filter_information = {}
        for i in range(1, len(self.clusters)):
            cluster_1 = self.clusters[i]
            for j in range(i + 1, len(self.clusters) + 1):
                cluster_2 = self.clusters[j]
                for node_id_1 in cluster_1:
                    for node_id_2 in cluster_2:
                        node_1 = self.nodes[node_id_1]
                        node_2 = self.nodes[node_id_2]
                        if self.is_ans(node_1, node_2):
                            if node_1.layer < node_2.layer:
                                filter_cluster_id.add(j)
                                filter_information[j] = i
                            else:
                                filter_cluster_id.add(i)
                                filter_information[i] = j

        # print(filter_cluster_id)
        # print(filter_information)

        for c_id in filter_cluster_id:
            self.clusters.pop(c_id)


def delete_str_num(str):
    """
    删除字符串中的数字
    """
    new_str = ''
    for word in str:
        try:
            int(word)
        except:
            new_str += word

    return new_str


def drawer(x1, y1, x2, y2, img):
    """
    绘制图片
    """
    draw = ImageDraw.Draw(img)
    draw.rectangle((x1, y1, x2, y2), fill=None, outline='red', width=2)


def cluster_test():
    for i in range(1, 16):
        tree = ET.ElementTree(file='../resources/d{}.xml'.format(i))
        img = Image.open('../resources/d{}.png'.format(i))
        xml_root = tree.getroot()
        root_node = TreeNode(xml_root, 0)
        xml_tree = XmlTree(root_node)
        nodes = xml_tree.get_nodes()
        xml_tree.get_node_clusters()
        xml_tree.filter_clusters()
        for cluster_id in xml_tree.clusters:
            tmp_img = img.copy()
            for node in nodes:
                if node.cluster_id != -1 and node.cluster_id == cluster_id:
                    x1, y1, x2, y2 = node.parse_bounds()
                    drawer(x1, y1, x2, y2, tmp_img)
            if not os.path.exists('../tmp/{}'.format(i)):
                os.makedirs('../tmp/{}'.format(i))
            tmp_img.save('../tmp/{}/{}.png'.format(i, cluster_id))


def main():
    tree = ET.ElementTree(file='../resources/d3.xml')
    img = Image.open('../resources/d3.png')
    xml_root = tree.getroot()
    root_node = TreeNode(xml_root, 0)
    xml_tree = XmlTree(root_node)

    nodes = xml_tree.get_nodes()



    xml_tree.get_node_clusters()

    xml_tree.filter_clusters()

    print(xml_tree.clusters)

    for cluster_id in xml_tree.clusters:
        tmp_img = img.copy()
        for node in nodes:
            if node.cluster_id != -1 and node.cluster_id == cluster_id:
                x1, y1, x2, y2 = node.parse_bounds()
                drawer(x1, y1, x2, y2, tmp_img)

        tmp_img.save('../tmp/{}.png'.format(cluster_id))

    #
    # xml_tree.filter_clusters()

    # print(xml_tree.nodes[25].attrib)
    # print(xml_tree.nodes[42].attrib)
    #
    # print(xml_tree.nodes_similar(xml_tree.nodes[25], xml_tree.nodes[42],))

    # for cluster_id in xml_tree.clusters:
    #     tmp_img = img.copy()
    #     for node in nodes:
    #         if node.cluster_id != -1 and node.cluster_id == cluster_id:
    #             x1, y1, x2, y2 = node.parse_bounds()
    #             drawer(x1, y1, x2, y2, tmp_img)
    #
    #     tmp_img.save('../result/{}.png'.format(cluster_id))

    # print(xml_tree.clusters)

    # a = None
    # b = None
    # for node in nodes:
    #     if node.attrib['bounds'] == '[0,93][540,444]':
    #         a = node
    #     if node.attrib['bounds'] == '[0,444][540,795]':
    #         b = node
    #
    # print(a.attrib)
    # print(b.attrib)
    #
    # print(xml_tree.nodes_similar(a, b))

#main()

cluster_test()
