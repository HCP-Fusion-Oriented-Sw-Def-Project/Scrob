import os

import cv2
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw

from cluster import get_nodes_similar_score
from utility import *
from result import CompareResult
from xml_tree import parse_xml, CompleteTree


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

    for i in range(1, 16):

        if i < 20:
            input_path = '../compare_test_resources/d' + str(i)

            output_path = '../branch_cluster_test_12_7/d' + str(i)

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


def bug_test():
    """
    专测各种bug
    :return:
    """

    input_path = '../compare_test_resources/d' + str(1)
    xml1 = input_path + '/' + '1.xml'
    png1 = input_path + '/' + '1.png'
    xml_tree1, nodes1 = parse_xml(xml1, png1)

    for cluster_id in xml_tree1.clusters:
        cluster = xml_tree1.clusters[cluster_id]
        # if not cluster.is_leaf:
        # tmp_node = cluster.nodes[0]
        # parent_node = tmp_node.parent
        # num_of_child = len(parent_node.children)
        #
        # if len(cluster.nodes) / num_of_child >= 0.5:
        #     for child in parent_node.children:
        #         if child not in cluster.nodes:
        #             print(child.attrib)

        if cluster_id == 8:
            tmp_node = cluster.nodes[0]
            parent_node = tmp_node.parent
            for child in parent_node.children:
                print(child.attrib)
                if child.attrib['index'] == '14':
                    a = child
                    print(a in cluster.nodes)

            print(len(cluster.nodes) / len(parent_node.children))


def get_static_nodes_test():
    """
    获取静态节点测试
    """

    for i in range(1, 17):

        if i == 1:
            input_path = '../compare_test_resources/d' + str(i)

            output_path = '../get_static_nodes_test/d' + str(i)

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

            xml_tree_list1 = [xml_tree1, xml_tree2]
            complete_tree1 = CompleteTree(xml_tree_list1, xml_tree1)

            # updated_version解析数据
            xml_tree3, nodes3 = parse_xml(xml3, png3)
            xml_tree4, nodes4 = parse_xml(xml4, png4)
            xml_tree_list2 = [xml_tree3, xml_tree4]
            complete_tree2 = CompleteTree(xml_tree_list2, xml_tree3)

            # base_version 画图
            base_out_path = output_path + '/' + 'base'
            img = cv2.imread(png1)

            complete_tree1.initialize()

            for node in complete_tree1.static_nodes:
                x1, y1, x2, y2 = node.parse_bounds()
                img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

            base_out_path_1 = base_out_path + '/' + '1'
            if not os.path.exists(base_out_path_1):
                os.makedirs(base_out_path_1)

            cv2.imwrite(base_out_path_1 + '/' + 'static' + '.png', img)

            # updated_version 画图
            updated_out_path = output_path + '/' + 'updated'
            img = cv2.imread(png3)

            complete_tree2.initialize()

            for node in complete_tree2.static_nodes:
                x1, y1, x2, y2 = node.parse_bounds()
                img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

            updated_out_path_3 = updated_out_path + '/' + '3'

            if not os.path.exists(updated_out_path_3):
                os.makedirs(updated_out_path_3)

            cv2.imwrite(updated_out_path_3 + '/' + 'static' + '.png', img)


def get_list_root_nodes_test():
    """
    对于获取列表节点的父节点进行测试
    :return:
    """

    for i in range(1, 17):

        if i < 20:
            input_path = '../compare_test_resources/d' + str(i)

            output_path = '../get_list_root_nodes_test/d' + str(i)

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

            for node in xml_tree1.list_root_nodes:
                x1, y1, x2, y2 = node.parse_bounds()
                img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

                for child in node.children:
                    x1, y1, x2, y2 = child.parse_bounds()
                    img = cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)

                base_out_path_1 = base_out_path + '/' + '1'

                if not os.path.exists(base_out_path_1):
                    os.makedirs(base_out_path_1)

            cv2.imwrite(base_out_path_1 + '/' + 'list_root_nodes' + '.png', img)

            img = cv2.imread(png2)
            for node in xml_tree2.list_root_nodes:
                x1, y1, x2, y2 = node.parse_bounds()
                img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

                for child in node.children:
                    x1, y1, x2, y2 = child.parse_bounds()
                    img = cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)

                base_out_path_2 = base_out_path + '/' + '2'

                if not os.path.exists(base_out_path_2):
                    os.makedirs(base_out_path_2)

            cv2.imwrite(base_out_path_2 + '/' + 'list_root_nodes' + '.png', img)

            # updated_version 画图
            updated_out_path = output_path + '/' + 'updated'
            img = cv2.imread(png3)

            for node in xml_tree3.list_root_nodes:
                x1, y1, x2, y2 = child.parse_bounds()
                img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                updated_out_path_3 = updated_out_path + '/' + '3'

                for child in node.children:
                    x1, y1, x2, y2 = child.parse_bounds()
                    img = cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)

                if not os.path.exists(updated_out_path_3):
                    os.makedirs(updated_out_path_3)

            cv2.imwrite(updated_out_path_3 + '/' + 'list_root_nodes' + '.png', img)

            img = cv2.imread(png4)
            updated_out_path = output_path + '/' + 'updated'
            for node in xml_tree4.list_root_nodes:
                x1, y1, x2, y2 = node.parse_bounds()
                img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                updated_out_path_4 = updated_out_path + '/' + '4'

                for child in node.children:
                    x1, y1, x2, y2 = child.parse_bounds()
                    img = cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)

                if not os.path.exists(updated_out_path_4):
                    os.makedirs(updated_out_path_4)

            cv2.imwrite(updated_out_path_4 + '/' + 'list_root_nodes' + '.png', img)


def get_dynamic_list_nodes_test():
    """
    专门获取含有动态节点的列表测试
    :return:
    """

    for i in range(1, 16):

        if i < 20:
            input_path = '../compare_test_resources/d' + str(i)

            # output_path = '../get_dynamic_list_nodes_test/d' + str(i)

            # # 加上了找回列表节点的补丁
            # output_path = '../get_dynamic_list_nodes_test2/d' + str(i)

            # 再一次过滤了列表节点 把伪列表给过滤了
            output_path = '../get_dynamic_list_nodes_test3/d' + str(i)

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

            complete_tree1 = CompleteTree([xml_tree1, xml_tree2], xml_tree1)

            # updated_version解析数据
            xml_tree3, nodes3 = parse_xml(xml3, png3)
            xml_tree4, nodes4 = parse_xml(xml4, png4)

            complete_tree2 = CompleteTree([xml_tree3, xml_tree4], xml_tree3)

            complete_tree1.tag_for_nodes()
            complete_tree2.tag_for_nodes()

            # base_version 画图
            base_out_path = output_path + '/' + 'base'
            img = cv2.imread(png1)
            #######################################################
            list_nodes = []
            for node in xml_tree1.list_root_nodes:
                # x1, y1, x2, y2 = node.parse_bounds()
                # img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

                for child in node.children:
                    if has_dynamic_desc(child) and child.cluster_id != -1:
                        list_nodes.append(child)
                        # x1, y1, x2, y2 = child.parse_bounds()
                        # img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

                base_out_path_1 = base_out_path + '/' + '1'

                if not os.path.exists(base_out_path_1):
                    os.makedirs(base_out_path_1)

            # 再进行一次补丁
            for node in xml_tree1.list_root_nodes:
                for k in range(len(node.children)):

                    # 如果聚类中的大多数节点都在列表中
                    if node.children[k] not in list_nodes and node.children[k].cluster_id != -1:
                        cluster = xml_tree1.clusters[node.children[k].cluster_id]
                        count = 0
                        for tmp_node in cluster.nodes:
                            if tmp_node in list_nodes:
                                count += 1
                        if count / len(cluster.nodes) >= 0.5:
                            list_nodes.append(node.children[k])

                    # if node.children[k] not in list_nodes and 0 < k < len(node.children) - 1:
                    #     if node.children[k - 1] in list_nodes and node.children[k + 1] in list_nodes:
                    #         list_nodes.append(node.children[k])

                    # 如果这个节点的前面的有兄弟节点以及后面也有兄弟节点在列表中
                    if node.children[k] not in list_nodes:
                        flag_left = False
                        flag_right = False
                        for j in range(0, k):
                            if node.children[j] in list_nodes:
                                flag_left = True
                                break

                        for j in range(k + 1, len(node.children)):
                            if node.children[j] in list_nodes:
                                flag_right = True
                                break

                        if flag_left and flag_right:
                            list_nodes.append(node.children[k])

            for node in list_nodes:
                if not is_filter_list_node(node, xml_tree1.clusters):
                    x1, y1, x2, y2 = node.parse_bounds()
                    img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

            cv2.imwrite(base_out_path_1 + '/' + 'list_nodes' + '.png', img)

            ############################################
            list_nodes = []
            img = cv2.imread(png2)
            for node in xml_tree2.list_root_nodes:
                # x1, y1, x2, y2 = node.parse_bounds()
                # img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

                for child in node.children:
                    if has_dynamic_desc(child) and child.cluster_id != -1:
                        # x1, y1, x2, y2 = child.parse_bounds()
                        # img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        list_nodes.append(child)

                base_out_path_2 = base_out_path + '/' + '2'

                if not os.path.exists(base_out_path_2):
                    os.makedirs(base_out_path_2)

            # 再进行一次补丁
            for node in xml_tree2.list_root_nodes:
                for k in range(len(node.children)):

                    if node.children[k] not in list_nodes and node.children[k].cluster_id != -1:
                        cluster = xml_tree2.clusters[node.children[k].cluster_id]
                        count = 0
                        for tmp_node in cluster.nodes:
                            if tmp_node in list_nodes:
                                count += 1
                        if count / len(cluster.nodes) >= 0.5:
                            list_nodes.append(node.children[k])

                    # if node.children[k] not in list_nodes and 0 < k < len(node.children) - 1:
                    #     if node.children[k - 1] in list_nodes and node.children[k + 1] in list_nodes:
                    #         list_nodes.append(node.children[k])

                    if node.children[k] not in list_nodes:
                        flag_left = False
                        flag_right = False
                        for j in range(0, k):
                            if node.children[j] in list_nodes:
                                flag_left = True
                                break

                        for j in range(k + 1, len(node.children)):
                            if node.children[j] in list_nodes:
                                flag_right = True
                                break

                        if flag_left and flag_right:
                            list_nodes.append(node.children[k])

            for node in list_nodes:
                if not is_filter_list_node(node, xml_tree2.clusters):
                    x1, y1, x2, y2 = node.parse_bounds()
                    img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

            cv2.imwrite(base_out_path_2 + '/' + 'list_nodes' + '.png', img)

            ##############################################
            list_nodes = []
            # updated_version 画图
            updated_out_path = output_path + '/' + 'updated'
            img = cv2.imread(png3)

            for node in xml_tree3.list_root_nodes:
                # x1, y1, x2, y2 = child.parse_bounds()
                # img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                updated_out_path_3 = updated_out_path + '/' + '3'

                for child in node.children:
                    if has_dynamic_desc(child) and child.cluster_id != -1:
                        # x1, y1, x2, y2 = child.parse_bounds()
                        # img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        list_nodes.append(child)

                if not os.path.exists(updated_out_path_3):
                    os.makedirs(updated_out_path_3)

            # 再进行一次补丁
            for node in xml_tree3.list_root_nodes:
                for k in range(len(node.children)):

                    if node.children[k] not in list_nodes and node.children[k].cluster_id != -1:
                        cluster = xml_tree3.clusters[node.children[k].cluster_id]
                        count = 0
                        for tmp_node in cluster.nodes:
                            if tmp_node in list_nodes:
                                count += 1
                        if count / len(cluster.nodes) >= 0.5:
                            list_nodes.append(node.children[k])

                    # if node.children[k] not in list_nodes and 0 < k < len(node.children) - 1:
                    #     if node.children[k - 1] in list_nodes and node.children[k + 1] in list_nodes:
                    #         list_nodes.append(node.children[k])

                    if node.children[k] not in list_nodes:
                        flag_left = False
                        flag_right = False
                        for j in range(0, k):
                            if node.children[j] in list_nodes:
                                flag_left = True
                                break

                        for j in range(k + 1, len(node.children)):
                            if node.children[j] in list_nodes:
                                flag_right = True
                                break

                        if flag_left and flag_right:
                            list_nodes.append(node.children[k])

            for node in list_nodes:
                if not is_filter_list_node(node, xml_tree3.clusters):
                    x1, y1, x2, y2 = node.parse_bounds()
                    img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

            cv2.imwrite(updated_out_path_3 + '/' + 'list_nodes' + '.png', img)

            ###############################################
            list_nodes = []
            img = cv2.imread(png4)
            updated_out_path = output_path + '/' + 'updated'
            for node in xml_tree4.list_root_nodes:
                # x1, y1, x2, y2 = node.parse_bounds()
                # img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                updated_out_path_4 = updated_out_path + '/' + '4'

                for child in node.children:
                    if has_dynamic_desc(child) and child.cluster_id != -1:
                        # x1, y1, x2, y2 = child.parse_bounds()
                        # img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        list_nodes.append(child)

                if not os.path.exists(updated_out_path_4):
                    os.makedirs(updated_out_path_4)

            # 再进行一次补丁
            for node in xml_tree4.list_root_nodes:
                for k in range(len(node.children)):

                    if node.children[k] not in list_nodes and node.children[k].cluster_id != -1:
                        cluster = xml_tree4.clusters[node.children[k].cluster_id]
                        count = 0
                        for tmp_node in cluster.nodes:
                            if tmp_node in list_nodes:
                                count += 1
                        if count / len(cluster.nodes) >= 0.5:
                            list_nodes.append(node.children[k])

                    # if node.children[k] not in list_nodes and 0 < k < len(node.children) - 1:
                    #     if node.children[k - 1] in list_nodes and node.children[k + 1] in list_nodes:
                    #         list_nodes.append(node.children[k])

                    if node.children[k] not in list_nodes:
                        flag_left = False
                        flag_right = False
                        for j in range(0, k):
                            if node.children[j] in list_nodes:
                                flag_left = True
                                break

                        for j in range(k + 1, len(node.children)):
                            if node.children[j] in list_nodes:
                                flag_right = True
                                break

                        if flag_left and flag_right:
                            list_nodes.append(node.children[k])

            for node in list_nodes:
                if not is_filter_list_node(node, xml_tree4.clusters):
                    x1, y1, x2, y2 = node.parse_bounds()
                    img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

            cv2.imwrite(updated_out_path_4 + '/' + 'list_root_nodes' + '.png', img)


def is_filter_list_node(node, clusters):
    """
    过滤掉那些不太像是组合的含有动态元素的列表
    :return:
    """

    count_desc = 0

    for desc in node.descendants:
        if not desc.children:
            count_desc += 1

    if count_desc <= 1:
        return True

    if node.cluster_id != -1 and node.cluster_id in clusters.keys():
        dynamic_list_nodes_count = 0
        cluster = clusters[node.cluster_id]

        for tmp_node in cluster.nodes:
            if has_dynamic_desc(tmp_node):
                dynamic_list_nodes_count += 1

        if dynamic_list_nodes_count / len(clusters[node.cluster_id].nodes) < 0.5:
            return True

    return False


def get_dynamic_list_nodes_test_2():
    """
    调用面向对象中的方法进行实验
    实现其实是类似于上面那个get_dynamic_list_nodes_test来实现的
    所以结果应该要一样才符合要求
    :return:
    """

    for i in range(1, 16):

        if i < 20:
            input_path = '../compare_test_resources/d' + str(i)

            output_path = '../get_dynamic_list_nodes_test4/d' + str(i)

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

            complete_tree1 = CompleteTree([xml_tree1, xml_tree2], xml_tree1)

            # updated_version解析数据
            xml_tree3, nodes3 = parse_xml(xml3, png3)
            xml_tree4, nodes4 = parse_xml(xml4, png4)

            complete_tree2 = CompleteTree([xml_tree3, xml_tree4], xml_tree3)

            complete_tree1.tag_for_nodes()
            complete_tree2.tag_for_nodes()
            complete_tree1.get_tree_list_nodes()
            complete_tree2.get_tree_list_nodes()

            # base_version 画图
            base_out_path = output_path + '/' + 'base'

            img = cv2.imread(png1)

            base_out_path_1 = base_out_path + '/' + '1'
            if not os.path.exists(base_out_path_1):
                os.makedirs(base_out_path_1)

            for node in xml_tree1.list_nodes:
                x1, y1, x2, y2 = node.parse_bounds()
                img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)


            cv2.imwrite(base_out_path_1 + '/' + 'list_nodes' + '.png', img)

            img = cv2.imread(png2)
            base_out_path_2 = base_out_path + '/' + '2'
            if not os.path.exists(base_out_path_2):
                os.makedirs(base_out_path_2)

            for node in xml_tree2.list_nodes:
                x1, y1, x2, y2 = node.parse_bounds()
                img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

            cv2.imwrite(base_out_path_2 + '/' + 'list_nodes' + '.png', img)

            # updated_version 画图
            updated_out_path = output_path + '/' + 'updated'
            img = cv2.imread(png3)

            updated_out_path_3 = updated_out_path + '/' + '3'
            if not os.path.exists(updated_out_path_3):
                os.makedirs(updated_out_path_3)
            for node in xml_tree3.list_nodes:
                x1, y1, x2, y2 = node.parse_bounds()
                img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)


            cv2.imwrite(updated_out_path_3 + '/' + 'list_nodes' + '.png', img)

            updated_out_path_4 = updated_out_path + '/' + '4'
            if not os.path.exists(updated_out_path_4):
                os.makedirs(updated_out_path_4)
            img = cv2.imread(png4)
            for node in xml_tree4.list_nodes:
                x1, y1, x2, y2 = node.parse_bounds()
                img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)


            cv2.imwrite(updated_out_path_4 + '/' + 'list_nodes' + '.png', img)

# cluster_correction_test()
# new_strategy_of_cluster_compare_test()

# leaf_cluster_test()
# branch_cluster_test()

# merge_cluster_test()

# bug_test()

# get_static_nodes_test()

# get_list_root_nodes_test()

# get_dynamic_list_nodes_test()

get_dynamic_list_nodes_test_2()
