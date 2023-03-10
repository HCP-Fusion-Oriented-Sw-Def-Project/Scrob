import os

import cv2
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw

from codes.utility import *
from result import CompareResult
from xml_tree import parse_xml, CompleteTree


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
    """
    验证聚类效果
    """
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


def get_list_node_test():
    """
    验证寻找列表节点的根节点的效果
    """

    res = 'd13'

    xml1 = '../compare_test_resources/' + res + '/3.xml'
    xml2 = '../compare_test_resources/' + res + '/4.xml'
    png1 = '../compare_test_resources/' + res + '/3.png'
    png2 = '../compare_test_resources/' + res + '/4.png'

    xml_tree1, nodes1 = parse_xml(xml1, png1)
    xml_tree2, nodes2 = parse_xml(xml2, png2)

    # 进行节点标记
    get_nodes_tag(xml_tree1, xml_tree2)

    # 方法: 先找属性变化的节点 然后再判断其是否存在于某个聚类当中 然后再去找它的祖先节点
    # 找到属性变化的节点
    changed_nodes = []
    for node in nodes1:
        if node.children == [] and node.dynamic_changed_type != ChangedType.REMAIN:
            changed_nodes.append(node)

    # 判断其是否属于某个聚类当中
    list_parent_nodes = []
    for node in changed_nodes:
        # print(node.attrib)
        if node.cluster_id != -1 and node.cluster_id not in xml_tree1.attr_changed_clusters:  # 说明存在于某个聚类当中
            # print(node.attrib)
            idx_list = xml_tree1.clusters[node.cluster_id]
            xml_tree1.attr_changed_clusters.add(node.cluster_id)
            # 取出聚类中的两个节点
            node_i = nodes1[idx_list[0]]
            node_j = nodes1[idx_list[1]]

            # 如果两个节点不是兄弟节点
            if node_i.parent != node_j.parent:
                # 获得公共祖先节点
                common_ans = get_nodes_common_ans(node_i, node_j)
                if common_ans not in list_parent_nodes and common_ans.full_xpath != '//':
                    list_parent_nodes.append(common_ans)

    # 去重前先按照节点的层次对列表进行排序（与下面的去重算法实现有关)
    list_parent_nodes.sort(key=lambda node: node.layer)

    # 给list_parent_nodes去重
    tmp_list_parent_nodes = []
    for i in range(len(list_parent_nodes)):
        flag = True
        for j in range(i + 1, len(list_parent_nodes)):
            x_node = list_parent_nodes[i]
            y_node = list_parent_nodes[j]
            # layer数越大 说明在树中的层次越低
            if has_common_desc(x_node, y_node) and x_node.layer > y_node.layer:
                flag = False

        if flag and x_node not in tmp_list_parent_nodes:
            tmp_list_parent_nodes.append(x_node)

    list_parent_nodes = tmp_list_parent_nodes

    img = cv2.imread(png1)
    dir = '../get_list_nodes_results/' + res + '.2'

    if not os.path.exists(dir):
        os.makedirs(dir)

    count = 0
    for node in list_parent_nodes:
        flag = False
        n_img = img.copy()
        for child in node.children:
            if has_desc_in_changed_cls(child, xml_tree1):
                # print(child.attrib)
                flag = True
                x1, y1, x2, y2 = child.parse_bounds()
                n_img = cv2.rectangle(n_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        if flag:
            cv2.imwrite(dir + '/' + str(count) + '.png', n_img)
            count += 1

    # 画出nodes_list即公共祖先节点
    print(len(list_parent_nodes))
    for node in list_parent_nodes:
        print(node.attrib)
        x1, y1, x2, y2 = node.parse_bounds()
        n_img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

    cv2.imwrite(dir + '/' + 'list_parent.png', img)


def get_changed_image_test():
    """
    验证图片颜色变化检测的有效性
    """

    res = 'd2'

    xml1 = '../tag_resources/' + res + '/1.xml'
    xml2 = '../tag_resources/' + res + '/2.xml'
    png1 = '../tag_resources/' + res + '/1.png'
    png2 = '../tag_resources/' + res + '/2.png'

    xml_tree1, nodes1 = parse_xml(xml1, png1)
    xml_tree2, nodes2 = parse_xml(xml2, png2)

    # 进行节点标记
    get_nodes_tag(xml_tree1, xml_tree2)

    img = cv2.imread(png1)
    dir = '../get_changed_image_results'

    if not os.path.exists(dir):
        os.makedirs(dir)

    a = None
    b = None

    for node in nodes1:
        if 'image' in node.attrib['class'].lower() and node.dynamic_changed_attrs['color'] == 1:
            x1, y1, x2, y2 = node.parse_bounds()
            img = cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

    cv2.imwrite(dir + '/' + 'test_results.png', img)


def merge_cluster_test():
    """
    对聚类合并的结果进行检测
    """

    xml1 = '../tag_resources/d15/1.xml'
    xml2 = '../tag_resources/d15/2.xml'
    png1 = '../tag_resources/d15/1.png'
    png2 = '../tag_resources/d15/2.png'

    xml_tree1, nodes1 = parse_xml(xml1, png1)
    xml_tree2, nodes2 = parse_xml(xml2, png2)

    # 进行标记
    get_nodes_tag(xml_tree1, xml_tree2)

    xml_tree1.get_list_clusters()
    xml_tree2.get_list_clusters()

    xml_tree_list = [xml_tree1, xml_tree2]

    complete_tree = CompleteTree(xml_tree_list, xml_tree1)

    complete_tree.merge_cluster()

    tmp = []
    for node in complete_tree.list_cluster_nodes:
        tmp.append(node.attrib['resource-id'])

    print(tmp)


def get_added_single_nodes_test():
    """
    对补充的非列表叶子节点进行检测
    """

    for i in range(1, 16):
        path = '../tag_resources/d' + str(i)

        # xml1 = '../tag_resources/d14/1.xml'
        # xml2 = '../tag_resources/d14/2.xml'
        # png1 = '../tag_resources/d14/1.png'
        # png2 = '../tag_resources/d14/2.png'

        xml1 = path + '/' + '1.xml'
        xml2 = path + '/' + '2.xml'
        png1 = path + '/' + '1.png'
        png2 = path + '/' + '2.png'

        xml_tree1, nodes1 = parse_xml(xml1, png1)
        xml_tree2, nodes2 = parse_xml(xml2, png2)

        # 进行标记
        get_nodes_tag(xml_tree1, xml_tree2)

        xml_tree1.get_list_clusters()
        xml_tree2.get_list_clusters()

        xml_tree_list = [xml_tree1, xml_tree2]

        complete_tree = CompleteTree(xml_tree_list, xml_tree1)

        complete_tree.get_extra_single_nodes()

        if complete_tree.extra_single_nodes:
            print(i)
            for node in complete_tree.extra_single_nodes:
                print(node.attrib)


def clusters_nodes_compare_test():
    """
    对聚类节点的对比结果进行测试
    """

    path = '../compare_test_resources/d1'

    xml1 = path + '/' + '1.xml'
    xml2 = path + '/' + '2.xml'
    png1 = path + '/' + '1.png'
    png2 = path + '/' + '2.png'

    xml3 = path + '/' + '3.xml'
    xml4 = path + '/' + '4.xml'
    png3 = path + '/' + '3.png'
    png4 = path + '/' + '4.png'

    # base_version解析数据
    xml_tree1, nodes1 = parse_xml(xml1, png1)
    xml_tree2, nodes2 = parse_xml(xml2, png2)

    # 进行标记
    get_nodes_tag(xml_tree1, xml_tree2)

    xml_tree1.get_list_clusters()
    xml_tree2.get_list_clusters()

    xml_tree_list1 = [xml_tree1, xml_tree2]
    complete_tree1 = CompleteTree(xml_tree_list1, xml_tree1)

    complete_tree1.merge_cluster()
    complete_tree1.get_extra_single_nodes()

    # updated_version解析数据
    xml_tree3, nodes3 = parse_xml(xml3, png3)
    xml_tree4, nodes4 = parse_xml(xml4, png4)

    # 进行标记
    get_nodes_tag(xml_tree3, xml_tree4)

    xml_tree3.get_list_clusters()
    xml_tree4.get_list_clusters()

    xml_tree_list2 = [xml_tree3, xml_tree4]
    complete_tree2 = CompleteTree(xml_tree_list2, xml_tree3)

    complete_tree2.merge_cluster()
    complete_tree2.get_extra_single_nodes()

    re = CompareResult(complete_tree1, complete_tree2, 0)
    re.cluster_nodes_compare()

    for node in re.removed_single_nodes:
        print(node.attrib)

    print('-----------------')

    for node in re.added_single_nodes:
        print(node.attrib)


def single_nodes_compare_test():
    """
    对single_nodes的对比结果进行测试
    """

    path = '../compare_test_resources/d14'

    xml1 = path + '/' + '1.xml'
    xml2 = path + '/' + '2.xml'
    png1 = path + '/' + '1.png'
    png2 = path + '/' + '2.png'

    xml3 = path + '/' + '3.xml'
    xml4 = path + '/' + '4.xml'
    png3 = path + '/' + '3.png'
    png4 = path + '/' + '4.png'

    # base_version解析数据
    xml_tree1, nodes1 = parse_xml(xml1, png1)
    xml_tree2, nodes2 = parse_xml(xml2, png2)

    # 进行标记
    get_nodes_tag(xml_tree1, xml_tree2)

    xml_tree1.get_list_clusters()
    xml_tree2.get_list_clusters()
    xml_tree1.get_single_nodes()
    xml_tree2.get_single_nodes()

    xml_tree_list1 = [xml_tree1, xml_tree2]
    complete_tree1 = CompleteTree(xml_tree_list1, xml_tree1)

    complete_tree1.merge_cluster()
    complete_tree1.get_extra_single_nodes()

    # updated_version解析数据
    xml_tree3, nodes3 = parse_xml(xml3, png3)
    xml_tree4, nodes4 = parse_xml(xml4, png4)

    # 进行标记
    get_nodes_tag(xml_tree3, xml_tree4)

    xml_tree3.get_list_clusters()
    xml_tree4.get_list_clusters()
    xml_tree3.get_single_nodes()
    xml_tree4.get_single_nodes()

    xml_tree_list2 = [xml_tree3, xml_tree4]
    complete_tree2 = CompleteTree(xml_tree_list2, xml_tree3)

    complete_tree2.merge_cluster()
    complete_tree2.get_extra_single_nodes()

    re = CompareResult(complete_tree1, complete_tree2, 0)

    # re.cluster_nodes_compare()

    re.single_nodes_compare()

    for node in re.removed_single_nodes:
        print(node.attrib)

    print('-----------------')

    for node in re.added_single_nodes:
        print(node.attrib)


def compare_test():
    """
    尝试进行对比
    查缺补漏 补充函数
    """

    path = '../compare_test_resources/d13'

    xml1 = path + '/' + '1.xml'
    xml2 = path + '/' + '2.xml'
    png1 = path + '/' + '1.png'
    png2 = path + '/' + '2.png'

    xml3 = path + '/' + '3.xml'
    xml4 = path + '/' + '4.xml'
    png3 = path + '/' + '3.png'
    png4 = path + '/' + '4.png'

    # base_version解析数据
    xml_tree1, nodes1 = parse_xml(xml1, png1)
    xml_tree2, nodes2 = parse_xml(xml2, png2)

    # 进行标记
    get_nodes_tag(xml_tree1, xml_tree2)

    xml_tree1.get_list_clusters()

    # xml_tree2.get_list_clusters()
    # xml_tree1.get_single_nodes()
    # xml_tree2.get_single_nodes()
    #
    # xml_tree_list1 = [xml_tree1, xml_tree2]
    # complete_tree1 = CompleteTree(xml_tree_list1, xml_tree1)
    #
    # complete_tree1.merge_cluster()
    #
    # complete_tree1.get_added_single_nodes()
    #
    # # updated_version解析数据
    # xml_tree3, nodes3 = parse_xml(xml3, png3)
    # xml_tree4, nodes4 = parse_xml(xml4, png4)
    #
    # # 进行标记
    # get_nodes_tag(xml_tree3, xml_tree4)
    #
    # xml_tree3.get_list_clusters()
    # xml_tree4.get_list_clusters()
    # xml_tree3.get_single_nodes()
    # xml_tree4.get_single_nodes()
    #
    # xml_tree_list2 = [xml_tree3, xml_tree4]
    # complete_tree2 = CompleteTree(xml_tree_list2, xml_tree3)
    #
    # complete_tree2.merge_cluster()
    # complete_tree2.get_added_single_nodes()
    #
    # re = CompareResult(complete_tree1, complete_tree2, 540, path + '/result')
    #
    # re.get_result()


def new_cluster_strategy_test():
    """
    使用新的聚类策略对页面进行测试
    即不仅仅只用id,还加上长宽
    """

    path = '../compare_test_resources/d13'
    xml = path + '/' + '3.xml'
    png = path + '/' + '3.png'
    xml_tree, nodes = parse_xml(xml, png)

    dir = '../new_cluster_stategy_test/'

    if not os.path.exists(dir):
        os.makedirs(dir)

    img = cv2.imread(png)

    for key in xml_tree.clusters:
        idx_list = xml_tree.clusters[key]
        n_img = img.copy()
        is_leaf = True
        for idx in idx_list:
            node = xml_tree.nodes[idx]
            if not node.children:
                x1, y1, x2, y2 = node.parse_bounds()
                n_img = cv2.rectangle(n_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            else:
                is_leaf = False

        if is_leaf:
            cv2.imwrite(dir + '/' + str(key) + '.png', n_img)


def new_get_list_clusters_strategy_test():
    """
    对列表内的聚类情况进行验证
    对所有页面对进行验证
    """

    input_path = '../compare_test_resources/d'
    output_path = '../new_get_list_cluster_stategy_test/d'
    for i in range(1, 17):
        tmp_input_path = input_path + str(i)

        xml1 = tmp_input_path + '/' + '1.xml'
        png1 = tmp_input_path + '/' + '1.png'

        xml2 = tmp_input_path + '/' + '2.xml'
        png2 = tmp_input_path + '/' + '2.png'

        xml3 = tmp_input_path + '/' + '3.xml'
        png3 = tmp_input_path + '/' + '3.png'

        xml4 = tmp_input_path + '/' + '4.xml'
        png4 = tmp_input_path + '/' + '4.png'

        tmp_output_path = output_path + str(i)

        base_out_put_path = tmp_output_path + '/' + 'base'
        draw_list_cluster_nodes(xml1, png1, xml2, png2, base_out_put_path)

        updated_out_put_path = tmp_output_path + '/' + 'updated'
        draw_list_cluster_nodes(xml3, png3, xml4, png4, updated_out_put_path)

    # path = '../compare_test_resources/d13'
    # xml1 = path + '/' + '3.xml'
    # png1 = path + '/' + '3.png'
    # xml2 = path + '/' + '4.xml'
    # png2 = path + '/' + '4.png'
    #
    # xml_tree1, nodes1 = parse_xml(xml1, png1)
    # xml_tree2, nodes2 = parse_xml(xml2, png2)
    #
    # # 进行标记
    # get_nodes_tag(xml_tree1, xml_tree2)
    #
    # dir = '../new_get_list_cluster_stategy_test/'
    #
    # if not os.path.exists(dir):
    #     os.makedirs(dir)
    #
    # img = cv2.imread(png1)
    #
    # # 获取聚类
    # xml_tree1.get_list_clusters()
    #
    # count = 0
    # for key in xml_tree1.list_clusters:
    #     n_img = img.copy()
    #     nodes = xml_tree1.list_clusters[key]['nodes']
    #     for node in nodes:
    #         x1, y1, x2, y2 = node.parse_bounds()
    #         n_img = cv2.rectangle(n_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
    #
    #     cv2.imwrite(dir + '/' + str(key) + '.png', n_img)
    #     count += 1


def draw_list_cluster_nodes(xml1, png1, xml2, png2, dir):
    """
    配合上面那个函数进行画图使用
    """

    xml_tree1, nodes1 = parse_xml(xml1, png1)
    xml_tree2, nodes2 = parse_xml(xml2, png2)

    # 进行标记
    get_nodes_tag(xml_tree1, xml_tree2)

    img = cv2.imread(png1)

    # 获取聚类
    xml_tree1.get_list_clusters()

    if not os.path.exists(dir):
        os.makedirs(dir)

    count = 0
    for key in xml_tree1.list_clusters:
        n_img = img.copy()
        nodes = xml_tree1.list_clusters[key]['nodes']
        for node in nodes:
            x1, y1, x2, y2 = node.parse_bounds()
            n_img = cv2.rectangle(n_img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        cv2.imwrite(dir + '/' + str(key) + '.png', n_img)
        count += 1


def new_strategy_of_merge_cluster_test():
    """
    对新的合并聚类的方法进行测试
    """

    xml1 = '../tag_resources/d1/1.xml'
    xml2 = '../tag_resources/d1/2.xml'
    png1 = '../tag_resources/d1/1.png'
    png2 = '../tag_resources/d1/2.png'

    xml_tree1, nodes1 = parse_xml(xml1, png1)
    xml_tree2, nodes2 = parse_xml(xml2, png2)

    # 进行标记
    get_nodes_tag(xml_tree1, xml_tree2)

    xml_tree1.get_list_clusters()
    xml_tree2.get_list_clusters()

    xml_tree_list = [xml_tree1, xml_tree2]

    complete_tree = CompleteTree(xml_tree_list, xml_tree1)

    # print(len(complete_tree.list_clusters.keys()))
    #
    # for key in complete_tree.list_clusters.keys():
    #     print(complete_tree.list_clusters[key]['nodes'][0].attrib['resource-id'])
    #
    # complete_tree.merge_list_clusters()
    #
    # print('-------------------')
    #
    # # print(len(complete_tree.list_clusters.keys()))
    #
    # for key in complete_tree.list_clusters.keys():
    #     print(key)
    #     print(complete_tree.list_clusters[key]['nodes'][0].attrib['resource-id'])

    complete_tree.get_list_clusters_tag()

    for key in complete_tree.list_clusters:
        for node in complete_tree.list_clusters[key]['nodes']:
            print(node.attrib)
        print(complete_tree.list_clusters[key]['common_attrs'])


def new_strategy_of_cluster_compare_test():
    """
    对最新的聚类对比方法进行测试
    """

    for i in range(1, 17):

        path = '../compare_test_resources/d' + str(i)

        output_path = '../new_strategy_of_cluster_compare_test/d' + str(i)

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        xml1 = path + '/' + '1.xml'
        xml2 = path + '/' + '2.xml'
        png1 = path + '/' + '1.png'
        png2 = path + '/' + '2.png'

        xml3 = path + '/' + '3.xml'
        xml4 = path + '/' + '4.xml'
        png3 = path + '/' + '3.png'
        png4 = path + '/' + '4.png'

        # base_version解析数据
        xml_tree1, nodes1 = parse_xml(xml1, png1)
        xml_tree2, nodes2 = parse_xml(xml2, png2)

        xml_tree_list1 = [xml_tree1, xml_tree2]
        complete_tree1 = CompleteTree(xml_tree_list1, xml_tree1)
        complete_tree1.initialize()

        # updated_version解析数据
        xml_tree3, nodes3 = parse_xml(xml3, png3)
        xml_tree4, nodes4 = parse_xml(xml4, png4)

        xml_tree_list2 = [xml_tree3, xml_tree4]
        complete_tree2 = CompleteTree(xml_tree_list2, xml_tree3)
        complete_tree2.initialize()

        re = CompareResult(complete_tree1, complete_tree2, 540, output_path)

        re.get_result()


def cluster_correction_test():
    """
    对聚类的比对算法进行参数的调整和修复
    重新实验和判断
    """

    path = '../compare_test_resources/d' + str(1)
    output_path = '../cluster_compare_correction_result/d' + str(1)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    xml1 = path + '/' + '1.xml'
    xml2 = path + '/' + '2.xml'
    png1 = path + '/' + '1.png'
    png2 = path + '/' + '2.png'

    xml3 = path + '/' + '3.xml'
    xml4 = path + '/' + '4.xml'
    png3 = path + '/' + '3.png'
    png4 = path + '/' + '4.png'

    # base_version解析数据
    xml_tree1, nodes1 = parse_xml(xml1, png1)
    xml_tree2, nodes2 = parse_xml(xml2, png2)

    xml_tree_list1 = [xml_tree1, xml_tree2]
    complete_tree1 = CompleteTree(xml_tree_list1, xml_tree1)
    complete_tree1.initialize()

    # updated_version解析数据
    xml_tree3, nodes3 = parse_xml(xml3, png3)
    xml_tree4, nodes4 = parse_xml(xml4, png4)

    xml_tree_list2 = [xml_tree3, xml_tree4]
    complete_tree2 = CompleteTree(xml_tree_list2, xml_tree3)
    complete_tree2.initialize()

    re = CompareResult(complete_tree1, complete_tree2, 540, output_path)
    re.get_result()


def main():
    num_str = 'd5'
    xml1 = '../compare_resources/' + num_str + '/' + '1.xml'
    xml2 = '../compare_resources/' + num_str + '/' + '3.xml'
    png1 = '../compare_resources/' + num_str + '/' + '1.png'
    png2 = '../compare_resources/' + num_str + '/' + '3.png'

    xml_tree1, nodes1 = parse_xml(xml1)
    xml_tree2, nodes2 = parse_xml(xml2)

    # nodes_xpath_matching_validate(nodes1, nodes2, png1, png2, num_str)
    cluster_validate(xml_tree1.nodes, xml_tree1.clusters, png1, num_str)

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


# get_list_node_test()
# main()
# get_changed_image_test()
# merge_cluster_test()
# get_added_single_nodes_test()

# single_nodes_compare_test()

# compare_test()

# new_cluster_strategy_test()

# new_get_list_clusters_strategy_test()

# new_strategy_of_merge_cluster_test()

# new_strategy_of_cluster_compare_test()


