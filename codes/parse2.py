import os

import cv2
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw

from codes.utility import *

from xml_tree import parse_xml


def nodes_xpath_matching_validate(x_nodes, y_nodes, x_png, y_png, num_str):
    """
    验证使用构造的xpath去进行元素匹配的效果
    """
    matched_nodes = {}
    leaf_nodes_count = 0
    for node in x_nodes:
        leaf_nodes_count += 1
        if not node.children:
            for match_node in y_nodes:
                if is_xpath_matched(node, match_node):
                    matched_nodes[node.idx] = match_node.idx
    # 读取图片
    x_img = cv2.imread(x_png)
    y_img = cv2.imread(y_png)

    dir = '../nodes_xpath_matching_results/' + num_str

    if not os.path.exists(dir):
        os.makedirs(dir)

    for key, value in matched_nodes.items():
        x_node = x_nodes[key]
        y_node = y_nodes[value]

        x1, y1, x2, y2 = x_node.parse_bounds()
        cropped_x_img = x_img[y1:y2, x1:x2]

        x3, y3, x4, y4 = y_node.parse_bounds()
        cropped_y_img = y_img[y3:y4, x3:x4]

        cv2.imwrite(dir + '/' + str(x_node.idx) + '.png', cropped_x_img)
        cv2.imwrite(dir + '/' + str(x_node.idx) + 'matched.png', cropped_y_img)


def is_xpath_similar(x_node, y_node):
    """
    判断两个xpath的部分后缀是否相同
    如果相同 可以认为是匹配上的
    """
    x_xpath_list = x_node.full_xpath[2:].split('/')
    y_xpath_list = y_node.full_xpath[2:].split('/')

    common_item_num = 0

    x_index = len(x_xpath_list) - 1
    y_index = len(y_xpath_list) - 1

    while x_index >= 0 and y_index >= 0:
        if x_xpath_list[x_index] == y_xpath_list[y_index]:
            x_index -= 1
            y_index -= 1
            common_item_num += 1
        else:
            break

    if common_item_num >= 4:
        return True

    return False


def nodes_matching_validate(x_nodes, y_nodes, x_png, y_png, num_str):
    """
    验证使用xpath后缀方法进行元素匹配的效果
    """
    matched_nodes = {}
    leaf_nodes_count = 0
    for node in x_nodes:
        leaf_nodes_count += 1
        if not node.children:
            for match_node in y_nodes:
                if is_xpath_similar(node, match_node):
                    matched_nodes[node.idx] = match_node.idx

    print(len(matched_nodes) / leaf_nodes_count)

    # 读取图片
    x_img = cv2.imread(x_png)
    y_img = cv2.imread(y_png)

    dir = '../nodes_matching_results/' + num_str

    if not os.path.exists(dir):
        os.makedirs(dir)

    for key, value in matched_nodes.items():
        x_node = x_nodes[key]
        y_node = y_nodes[value]

        x1, y1, x2, y2 = x_node.parse_bounds()
        cropped_x_img = x_img[y1:y2, x1:x2]

        x3, y3, x4, y4 = y_node.parse_bounds()
        cropped_y_img = y_img[y3:y4, x3:x4]

        cv2.imwrite(dir + '/' + str(x_node.idx) + '.png', cropped_x_img)
        cv2.imwrite(dir + '/' + str(x_node.idx) + 'matched.png', cropped_y_img)


def cluster_validate(nodes, clusters, png, num_str):
    img = cv2.imread(png)
    dir = '../cluster_results/' + num_str

    if not os.path.exists(dir):
        os.makedirs(dir)

    for key in clusters:
        idx_list = clusters[key]
        n_img = img.copy()
        is_leaf = True
        for idx in idx_list:
            node = nodes[idx]
            if not node.children:
                x1, y1, x2, y2 = node.parse_bounds()
                n_img = cv2.rectangle(n_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            else:
                is_leaf = False

        if is_leaf:
            cv2.imwrite(dir + '/' + str(key) + '.png', n_img)


def nodes_tag_test():
    xml1 = '../tag_resources/d1/1.xml'
    xml2 = '../tag_resources/d1/2.xml'

    xml_tree1, nodes1 = parse_xml(xml1)
    xml_tree2, nodes2 = parse_xml(xml2)


def main():
    num_str = 'd13'
    xml1 = '../compare_resources/' + num_str + '/' + '1.xml'
    xml2 = '../compare_resources/' + num_str + '/' + '3.xml'
    png1 = '../compare_resources/' + num_str + '/' + '1.png'
    png2 = '../compare_resources/' + num_str + '/' + '3.png'

    xml_tree1, nodes1 = parse_xml(xml1)
    xml_tree2, nodes2 = parse_xml(xml2)

    for node in nodes1:
        print(node.xpath)

    # nodes_xpath_matching_validate(nodes1, nodes2, png1, png2, num_str)
    # cluster_validate(xml_tree2.nodes, xml_tree2.clusters, png2, num_str)

    # print(xml_tree1.clusters)

    # nodes_matching_validate(nodes1, nodes2, png1, png2, num_str)

    # tree = ET.ElementTree(file=xml1)
    # xml_root = tree.getroot()
    # root_node = TreeNode(xml_root, 0)
    # xml_tree = XmlTree(root_node)
    # nodes = xml_tree.get_nodes()  # 只有调用这个函数之后 才进行了深度优先搜索
    #
    # xml_tree.get_clusters_from_top_down()
    # print(xml_tree.clusters)

    # for node in xml_tree.leaf_nodes:
    #      print(node.xpath)

    # print(xml_tree.branch_resource_id_count)
    # print(xml_tree.branch_text_count)
    # print(xml_tree.branch_content_count)

    # print(nodes[0].full_xpath)


nodes_tag_test()
