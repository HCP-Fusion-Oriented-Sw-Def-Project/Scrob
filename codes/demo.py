import pickle
from xml_tree import parse_xml, CompleteTree
from result2 import CompareResult


def read_ground_truth(file_path):
    """
    读取 Scrob UI Viewer 保存的信息
    :return:
    """

    # 读取标记数据
    base_visible_path = file_path + '/base_invisible'
    f = open(base_visible_path + '/base_invisible_nodes', 'rb')
    base_visible_nodes = pickle.load(f)

    for node in base_visible_nodes:
        if not hasattr(node, 'matched_node_idx'):
            node.matched_node_idx = node.matched_node_no

    updated_visible_path = file_path + '/updated_invisible'
    f = open(updated_visible_path + '/updated_invisible_nodes', 'rb')
    updated_visible_nodes = pickle.load(f)

    removed_path = file_path + '/removed'
    f = open(removed_path + '/removed_nodes', 'rb')
    removed_nodes = pickle.load(f)

    changed_path = file_path + '/changed'
    f = open(changed_path + '/changed_nodes', 'rb')
    changed_nodes = pickle.load(f)

    added_path = file_path + '/added'
    f = open(added_path + '/added_nodes', 'rb')
    added_nodes = pickle.load(f)

    matched_path = file_path + '/matched'
    f = open(matched_path + '/matched_nodes', 'rb')
    matched_nodes = pickle.load(f)

    base_xml_tree_path = file_path + '/res'
    f = open(base_xml_tree_path + '/base_xml_tree', 'rb')
    base_xml_tree = pickle.load(f)

    updated_xml_tree_path = file_path + '/res'
    f = open(updated_xml_tree_path + '/updated_xml_tree', 'rb')
    updated_xml_tree = pickle.load(f)

    result = [base_visible_nodes, updated_visible_nodes,
              removed_nodes, changed_nodes,
              added_nodes, matched_nodes]

    for node_list in result:
        for node in node_list:
            if not hasattr(node, 'matched_node_idx'):
                node.matched_node_idx = node.matched_node_no

    return result


def get_scrob_result(file_path, is_static):
    """
    使用scrob进行比较 并出结果
    :param is_static:
    :param file_path:
    :return:
    """

    # 可以修改为 在file_path中对文件进行搜索 然后将路径下的所有GUI data 作为输入
    if is_static:
        # 进行对比判断
        xml1 = file_path + '/' + '1.xml'
        png1 = file_path + '/' + '1.png'
        xml2 = file_path + '/' + '1.xml'
        png2 = file_path + '/' + '1.png'

        xml3 = file_path + '/' + '3.xml'
        png3 = file_path + '/' + '3.png'
        xml4 = file_path + '/' + '3.xml'
        png4 = file_path + '/' + '3.png'

    else:
        # 进行对比判断
        xml1 = file_path + '/' + '1.xml'
        png1 = file_path + '/' + '1.png'
        xml2 = file_path + '/' + '2.xml'
        png2 = file_path + '/' + '2.png'

        xml3 = file_path + '/' + '3.xml'
        png3 = file_path + '/' + '3.png'
        xml4 = file_path + '/' + '4.xml'
        png4 = file_path + '/' + '4.png'

    xml_tree1, nodes1 = parse_xml(xml1, png1)
    xml_tree2, nodes2 = parse_xml(xml2, png2)

    # 这个构造函数可以接受更多的xml_tree作为参数 也即多次遍历所得结果
    complete_tree = CompleteTree([xml_tree1, xml_tree2], xml_tree1)
    complete_tree.initialize()
    xml_tree3, nodes3 = parse_xml(xml3, png3)
    xml_tree4, nodes4 = parse_xml(xml4, png4)
    complete_tree2 = CompleteTree([xml_tree3, xml_tree4], xml_tree3)
    complete_tree2.initialize()

    re = CompareResult(complete_tree, complete_tree2, '')

    # 非列表元素对比结果
    # removed_nodes, changed_nodes, added_nodes = re.get_single_nodes_result()

    # 保存结果图
    # re.save_single_result()

    # 列表元素对比结果
    removed_nodes, changed_nodes, added_nodes = re.get_list_nodes_result()

    # 保存结果图
    re.save_list_result()

    return [removed_nodes, changed_nodes, added_nodes]
