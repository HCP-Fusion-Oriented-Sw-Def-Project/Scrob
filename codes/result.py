from xml_tree import get_nodes_similar_score


class CompareResult(object):
    """
    结果类
    存储各个数据的路径
    输出路径
    以及变化的节点
    """

    def __init__(self, base_complete_tree, updated_complete_tree, width):
        # 基础版本数据 更新版本数据 以及输出 路径
        self.base_data_path = ''
        self.updated_data_path = ''
        self.output_path = ''

        # 待比较的screen路径
        self.base_img_path = ''
        self.updated_img_path = ''

        # 被移除的节点 变化的节点 新增的节点
        self.removed_nodes = []
        self.changed_nodes = []
        self.added_nodes = []

        # 对比屏幕的宽度设置
        self.width = width

        # 对比所需要的完全树
        self.base_complete_tree = base_complete_tree
        self.updated_complete_tree = updated_complete_tree

    def get_result(self):
        """
        获得最终对比的结果
        """

        self.cluster_nodes_compare()

    def cluster_nodes_compare(self):
        """
        聚类节点对比
        首先对比出增删的聚类节点
        之后将这些聚类找出
        """

        removed_cluster_nodes = []
        added_cluster_nodes = []

        x_cluster_nodes = self.base_complete_tree.list_cluster_nodes
        y_cluster_nodes = self.updated_complete_tree.list_cluster_nodes

        # 获取增删的聚类
        for node in x_cluster_nodes:
            if not is_cluster_existed(node, y_cluster_nodes):
                removed_cluster_nodes.append(node)

        for node in y_cluster_nodes:
            if not is_cluster_existed(node, x_cluster_nodes):
                added_cluster_nodes.append(node)

        # 找出实际GUI中的这些增删的聚类节点
        x_leaf_nodes = self.base_complete_tree.main_xml_tree.leaf_nodes
        y_leaf_nodes = self.updated_complete_tree.main_xml_tree.leaf_nodes

        # 找到删除的聚类节点
        # 存在问题 removed_cluster_nodes内部可能有重复 因为没有id的节点不能聚类在一起
        for node in x_leaf_nodes:
            flag = False
            for tmp_node in removed_cluster_nodes:
                if get_nodes_similar_score(node, tmp_node) >= 0.8:
                    flag = True
            if flag:
                self.removed_nodes.append(node)

        # 找到增加的聚类节点
        for node in y_leaf_nodes:
            flag = False
            for tmp_node in added_cluster_nodes:
                if get_nodes_similar_score(node, tmp_node) >= 0.8:
                    flag = True
            if flag:
                self.added_nodes.append(node)


def is_cluster_existed(node, compared_nodes):
    """
    判断聚类节点是否在另一个版本中存在
    """

    for tmp_node in compared_nodes:
        sim = get_nodes_similar_score(node, tmp_node)
        if sim >= 0.8:
            return True

    return False
