import os

import cv2
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw

from tree_node import TreeNode
from xml_tree import XmlTree


def parse_xml(file_name):
    tree = ET.ElementTree(file=file_name)
    xml_root = tree.getroot()
    root_node = TreeNode(xml_root, 0)
    xml_tree = XmlTree(root_node)
    nodes = xml_tree.get_nodes()
    return nodes


def is_xpath_similar(x_node, y_node):
    """
    判断两个xpath的部分后缀是否相同
    如果相同 可以认为是匹配上的
    """
    x_xpath_list = x_node.xpath[2:].split('/')
    y_xpath_list = y_node.xpath[2:].split('/')

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
        if node.children == []:
            for match_node in y_nodes:
                if is_xpath_similar(node, match_node):
                    matched_nodes[node.id] = match_node.id
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

        cv2.imwrite(dir + '/' + str(x_node.id) + '.png', cropped_x_img)
        cv2.imwrite(dir + '/' + str(x_node.id) + 'matched.png', cropped_y_img)


def main():
    num_str = 'd13'
    xml1 = '../compare_resources/' + num_str + '/' + '1.xml'
    xml2 = '../compare_resources/' + num_str + '/' + '3.xml'
    png1 = '../compare_resources/' + num_str + '/' + '1.png'
    png2 = '../compare_resources/' + num_str + '/' + '3.png'

    nodes1 = parse_xml(xml1)
    nodes2 = parse_xml(xml2)

    # nodes_matching_validate(nodes1, nodes2, png1, png2, num_str)

    for node in nodes1:
        print(node.layer)


main()
