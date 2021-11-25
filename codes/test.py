import os

import cv2
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw

from cluster import get_nodes_similar_score
from utility import *
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


def leaf_cluster_test():
    """
    测试叶子节点聚类效果
    """

    for i in range(1, 17):

        input_path = '../compare_test_resources/d' + str(i)

        output_path = '../leaf_cluster_test/d' + str(i)

        xml1 = input_path + '/' + '1.xml'
        xml2 = input_path + '/' + '2.xml'
        png1 = input_path + '/' + '1.png'
        png2 = input_path + '/' + '2.png'

        xml3 = input_path + '/' + '3.xml'
        xml4 = input_path + '/' + '4.xml'
        png3 = input_path + '/' + '3.png'
        png4 = input_path + '/' + '4.png'

        # base_version解析数据
        xml_tree1, nodes1 = parse_xml(xml1, png1)
        xml_tree2, nodes2 = parse_xml(xml2, png2)

        # updated_version解析数据
        xml_tree3, nodes3 = parse_xml(xml3, png3)
        xml_tree4, nodes4 = parse_xml(xml4, png4)

        # base_version 画图
        base_out_path = output_path + '/' + 'base'
        img = cv2.imread(png1)
        for cluster_id in xml_tree1.clusters:
            tmp_img = img.copy()
            cluster = xml_tree1.clusters[cluster_id]
            if cluster.is_leaf:
                nodes = cluster.nodes
                for node in nodes:
                    x1, y1, x2, y2 = node.parse_bounds()
                    tmp_img = cv2.rectangle(tmp_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

                base_out_path_1 = base_out_path + '/' + '1'

                if not os.path.exists(base_out_path_1):
                    os.makedirs(base_out_path_1)

                cv2.imwrite(base_out_path_1 + '/' + str(cluster_id) + '.png', tmp_img)

        img = cv2.imread(png2)
        for cluster_id in xml_tree2.clusters:
            tmp_img = img.copy()
            cluster = xml_tree2.clusters[cluster_id]
            if cluster.is_leaf:
                nodes = cluster.nodes
                for node in nodes:
                    x1, y1, x2, y2 = node.parse_bounds()
                    tmp_img = cv2.rectangle(tmp_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

                base_out_path_2 = base_out_path + '/' + '2'

                if not os.path.exists(base_out_path_2):
                    os.makedirs(base_out_path_2)

                cv2.imwrite(base_out_path_2 + '/' + str(cluster_id) + '.png', tmp_img)

        # updated_version 画图
        updated_out_path = output_path + '/' + 'updated'
        img = cv2.imread(png3)
        for cluster_id in xml_tree3.clusters:
            tmp_img = img.copy()
            cluster = xml_tree3.clusters[cluster_id]
            if cluster.is_leaf:
                nodes = cluster.nodes
                for node in nodes:
                    x1, y1, x2, y2 = node.parse_bounds()
                    tmp_img = cv2.rectangle(tmp_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

                updated_out_path_3 = updated_out_path + '/' + '3'

                if not os.path.exists(updated_out_path_3):
                    os.makedirs(updated_out_path_3)

                cv2.imwrite(updated_out_path_3 + '/' + str(cluster_id) + '.png', tmp_img)

        img = cv2.imread(png4)
        updated_out_path = output_path + '/' + 'updated'
        for cluster_id in xml_tree4.clusters:
            tmp_img = img.copy()
            cluster = xml_tree4.clusters[cluster_id]
            if cluster.is_leaf:
                nodes = cluster.nodes
                for node in nodes:
                    x1, y1, x2, y2 = node.parse_bounds()
                    tmp_img = cv2.rectangle(tmp_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

                updated_out_path_4 = updated_out_path + '/' + '4'

                if not os.path.exists(updated_out_path_4):
                    os.makedirs(updated_out_path_4)

                cv2.imwrite(updated_out_path_4 + '/' + str(cluster_id) + '.png', tmp_img)


def branch_cluster_test():
    """
    测试非叶子节点的聚类效果
    """

    for i in range(1, 17):

        if i < 20:
            input_path = '../compare_test_resources/d' + str(i)

            output_path = '../branch_cluster_test/d' + str(i)

            xml1 = input_path + '/' + '1.xml'
            xml2 = input_path + '/' + '2.xml'
            png1 = input_path + '/' + '1.png'
            png2 = input_path + '/' + '2.png'

            xml3 = input_path + '/' + '3.xml'
            xml4 = input_path + '/' + '4.xml'
            png3 = input_path + '/' + '3.png'
            png4 = input_path + '/' + '4.png'

            # base_version解析数据
            xml_tree1, nodes1 = parse_xml(xml1, png1)
            xml_tree2, nodes2 = parse_xml(xml2, png2)

            # updated_version解析数据
            xml_tree3, nodes3 = parse_xml(xml3, png3)
            xml_tree4, nodes4 = parse_xml(xml4, png4)

            # base_version 画图
            base_out_path = output_path + '/' + 'base'
            img = cv2.imread(png1)
            for cluster_id in xml_tree1.clusters:
                tmp_img = img.copy()
                cluster = xml_tree1.clusters[cluster_id]
                if not cluster.is_leaf:
                    nodes = cluster.nodes
                    for node in nodes:
                        x1, y1, x2, y2 = node.parse_bounds()
                        tmp_img = cv2.rectangle(tmp_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

                    base_out_path_1 = base_out_path + '/' + '1'

                    if not os.path.exists(base_out_path_1):
                        os.makedirs(base_out_path_1)

                    cv2.imwrite(base_out_path_1 + '/' + str(cluster_id) + '.png', tmp_img)

            img = cv2.imread(png2)
            for cluster_id in xml_tree2.clusters:
                tmp_img = img.copy()
                cluster = xml_tree2.clusters[cluster_id]
                if not cluster.is_leaf:
                    nodes = cluster.nodes
                    for node in nodes:
                        x1, y1, x2, y2 = node.parse_bounds()
                        tmp_img = cv2.rectangle(tmp_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

                    base_out_path_2 = base_out_path + '/' + '2'

                    if not os.path.exists(base_out_path_2):
                        os.makedirs(base_out_path_2)

                    cv2.imwrite(base_out_path_2 + '/' + str(cluster_id) + '.png', tmp_img)

            # updated_version 画图
            updated_out_path = output_path + '/' + 'updated'
            img = cv2.imread(png3)
            for cluster_id in xml_tree3.clusters:
                tmp_img = img.copy()
                cluster = xml_tree3.clusters[cluster_id]
                if not cluster.is_leaf:
                    nodes = cluster.nodes
                    for node in nodes:
                        x1, y1, x2, y2 = node.parse_bounds()
                        tmp_img = cv2.rectangle(tmp_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

                    updated_out_path_3 = updated_out_path + '/' + '3'

                    if not os.path.exists(updated_out_path_3):
                        os.makedirs(updated_out_path_3)

                    cv2.imwrite(updated_out_path_3 + '/' + str(cluster_id) + '.png', tmp_img)

            img = cv2.imread(png4)
            updated_out_path = output_path + '/' + 'updated'
            for cluster_id in xml_tree4.clusters:
                tmp_img = img.copy()
                cluster = xml_tree4.clusters[cluster_id]
                if not cluster.is_leaf:
                    nodes = cluster.nodes
                    for node in nodes:
                        x1, y1, x2, y2 = node.parse_bounds()
                        tmp_img = cv2.rectangle(tmp_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

                    updated_out_path_4 = updated_out_path + '/' + '4'

                    if not os.path.exists(updated_out_path_4):
                        os.makedirs(updated_out_path_4)

                    cv2.imwrite(updated_out_path_4 + '/' + str(cluster_id) + '.png', tmp_img)


def merge_cluster_test():
    for i in range(1, 17):

        if i == 1:

            input_path = '../compare_test_resources/d' + str(i)
            output_path = '../merge_cluster_test/d' + str(i)

            xml1 = input_path + '/' + '1.xml'
            xml2 = input_path + '/' + '2.xml'
            png1 = input_path + '/' + '1.png'
            png2 = input_path + '/' + '2.png'

            xml3 = input_path + '/' + '3.xml'
            xml4 = input_path + '/' + '4.xml'
            png3 = input_path + '/' + '3.png'
            png4 = input_path + '/' + '4.png'

            # base_version解析数据
            xml_tree1, nodes1 = parse_xml(xml1, png1)
            xml_tree2, nodes2 = parse_xml(xml2, png2)

            for x_cluster_id in xml_tree1.clusters:
                x_cluster = xml_tree1.clusters[x_cluster_id]
                # print('begin')
                tmp_list = []
                for y_cluster_id in xml_tree2.clusters:
                    y_cluster = xml_tree2.clusters[y_cluster_id]
                    sim = get_nodes_similar_score(x_cluster.nodes[0], y_cluster.nodes[0])
                    if sim >= 0.8:
                        # print('1')
                        tmp_list.append(y_cluster)

                if len(tmp_list) > 1:
                    print(x_cluster.nodes[0].attrib)
                    print(x_cluster.nodes[0].layer)
                    print(tmp_list[0].nodes[0].attrib)
                    print(tmp_list[0].nodes[0].layer)
                    print(tmp_list[1].nodes[0].attrib)
                    print(tmp_list[1].nodes[0].layer)
                    print('------------------------------')


            # for x_cluster_id in xml_tree1.clusters:
            #     x_cluster = xml_tree1.clusters[x_cluster_id]
            #     for y_cluster_id in xml_tree2.clusters:
            #         y_cluster = xml_tree2.clusters[y_cluster_id]
            #
            #         sim = get_nodes_similar_score(x_cluster.nodes[0], y_cluster.nodes[0])
            #         if sim >= 0.8:
            #             x_cluster.is_common = True
            #             y_cluster.is_common = True
            #
            # # 画图 xml1 中仅有的聚类节点
            # print('xml1')
            # img = cv2.imread(png1)
            # for cluster_id in xml_tree1.clusters:
            #     cluster = xml_tree1.clusters[cluster_id]
            #     if not cluster.is_common:
            #         for node in cluster.nodes:
            #             print(node.attrib)
            #             x1, y1, x2, y2 = node.parse_bounds()
            #             img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            #
            # if not os.path.exists(output_path):
            #     os.makedirs(output_path)
            #
            # cv2.imwrite(output_path + '/' + 'cluster_only_in_xml1.png', img)
            #
            # # 画图 xml2 中仅有的聚类节点
            # print('xml2')
            # img = cv2.imread(png2)
            # for cluster_id in xml_tree2.clusters:
            #     cluster = xml_tree2.clusters[cluster_id]
            #     if not cluster.is_common:
            #         for node in cluster.nodes:
            #             print(node.attrib)
            #             x1, y1, x2, y2 = node.parse_bounds()
            #             img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            #
            # cv2.imwrite(output_path + '/' + 'cluster_only_in_xml2.png', img)


# cluster_correction_test()
# new_strategy_of_cluster_compare_test()

# leaf_cluster_test()
# branch_cluster_test()

merge_cluster_test()
