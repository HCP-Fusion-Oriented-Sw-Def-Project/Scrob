import os

import cv2
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw

from codes.utility import *
from result import CompareResult
from xml_tree import parse_xml


# def new_strategy_of_cluster_compare_test():
#     """
#     对最新的聚类对比方法进行测试
#     """
#
#     for i in range(1, 17):
#
#         path = '../compare_test_resources/d' + str(i)
#
#         output_path = '../new_strategy_of_cluster_compare_test/d' + str(i)
#
#         if not os.path.exists(output_path):
#             os.makedirs(output_path)
#
#         xml1 = path + '/' + '1.xml'
#         xml2 = path + '/' + '2.xml'
#         png1 = path + '/' + '1.png'
#         png2 = path + '/' + '2.png'
#
#         xml3 = path + '/' + '3.xml'
#         xml4 = path + '/' + '4.xml'
#         png3 = path + '/' + '3.png'
#         png4 = path + '/' + '4.png'
#
#         # base_version解析数据
#         xml_tree1, nodes1 = parse_xml(xml1, png1)
#         xml_tree2, nodes2 = parse_xml(xml2, png2)
#
#         xml_tree_list1 = [xml_tree1, xml_tree2]
#         complete_tree1 = CompleteTree(xml_tree_list1, xml_tree1)
#         complete_tree1.initialize()
#
#         # updated_version解析数据
#         xml_tree3, nodes3 = parse_xml(xml3, png3)
#         xml_tree4, nodes4 = parse_xml(xml4, png4)
#
#         xml_tree_list2 = [xml_tree3, xml_tree4]
#         complete_tree2 = CompleteTree(xml_tree_list2, xml_tree3)
#         complete_tree2.initialize()
#
#         re = CompareResult(complete_tree1, complete_tree2, 540, output_path)
#
#         re.get_result()
#
#
# def cluster_correction_test():
#     """
#     对聚类的比对算法进行参数的调整和修复
#     重新实验和判断
#     """
#
#     path = '../compare_test_resources/d' + str(1)
#     output_path = '../cluster_compare_correction_result/d' + str(1)
#
#     if not os.path.exists(output_path):
#         os.makedirs(output_path)
#
#     xml1 = path + '/' + '1.xml'
#     xml2 = path + '/' + '2.xml'
#     png1 = path + '/' + '1.png'
#     png2 = path + '/' + '2.png'
#
#     xml3 = path + '/' + '3.xml'
#     xml4 = path + '/' + '4.xml'
#     png3 = path + '/' + '3.png'
#     png4 = path + '/' + '4.png'
#
#     # base_version解析数据
#     xml_tree1, nodes1 = parse_xml(xml1, png1)
#     xml_tree2, nodes2 = parse_xml(xml2, png2)
#
#     xml_tree_list1 = [xml_tree1, xml_tree2]
#     complete_tree1 = CompleteTree(xml_tree_list1, xml_tree1)
#     complete_tree1.initialize()
#
#     # updated_version解析数据
#     xml_tree3, nodes3 = parse_xml(xml3, png3)
#     xml_tree4, nodes4 = parse_xml(xml4, png4)
#
#     xml_tree_list2 = [xml_tree3, xml_tree4]
#     complete_tree2 = CompleteTree(xml_tree_list2, xml_tree3)
#     complete_tree2.initialize()
#
#     re = CompareResult(complete_tree1, complete_tree2, 540, output_path)
#     re.get_result()


def cluster_test():
    """
    测试聚类效果
    """
    path = '../compare_test_resources/d' + str(1)
    xml1 = path + '/' + '1.xml'
    xml2 = path + '/' + '2.xml'
    png1 = path + '/' + '1.png'
    png2 = path + '/' + '2.png'

    xml_tree, nodes = parse_xml(xml1, png1)

    for cluster_id in xml_tree.clusters:
        cluster = xml_tree.clusters[cluster_id]
        print('*********************')
        for node in cluster.nodes:
            print(node.attrib)


# cluster_correction_test()
# new_strategy_of_cluster_compare_test()

cluster_test()
