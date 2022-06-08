class TreeNodeCluster(object):
    """
    xml树节点聚类
    """

    def __init__(self, id):
        # 聚类节点
        self.nodes = []

        # self.num_of_nodes = 0

        # # 判断聚类节点数量是否发生变化
        # self.has_num_changed = False

        # 聚类id
        self.id = id

        # # 是否被过滤 目前暂时只过滤layout的节点
        # self.filter = False

        # 是否是叶子节点的聚类
        self.is_leaf = False

        # 记录聚类的层次
        self.layer = -1

        # # 记录该聚类是否在同版本不同的xml文件中共有
        # self.is_common = False


def get_nodes_similar_score(x_node, y_node):
    """
    聚类的过程中判断两个节点是否相似
    """

    if x_node.attrib['class'] != y_node.attrib['class']:
        return 0

    x_node_id = x_node.attrib['resource-id']
    y_node_id = y_node.attrib['resource-id']

    x_node_text = x_node.attrib['text']
    y_node_text = y_node.attrib['text']
    x_node_content = x_node.attrib['content-desc']
    y_node_content = y_node.attrib['content-desc']

    if x_node_id.find('/') != -1:
        x_node_id = x_node_id.split('/')[1]

    if y_node_id.find('/') != -1:
        y_node_id = y_node_id.split('/')[1]

    # id 不为空
    if len(x_node_id) != 0 or len(y_node_id) != 0:
        if x_node_id == y_node_id:
            return 1
        return 0

    else:
        # 如果 横/纵 坐标  以及 长/宽 有两者占 则表示是同类 即 横坐标和长度 纵坐标和宽度 一共4种组合
        # 这种方法只对一个页面上的没有id的同类元素有效
        score = 0

        if len(x_node_text) != 0 or len(y_node_text) != 0:
            if x_node_text == y_node_text:
                score += 0.4

        if len(x_node_content) != 0 or len(y_node_content) != 0:
            if x_node_content == y_node_content:
                score += 0.4

        if x_node.x_loc == y_node.x_loc or x_node.y_loc == y_node.y_loc:
            score += 0.4

        if x_node.width == y_node.width or x_node.height == y_node.height:
            score += 0.4

        return score


def is_similar(x_node, y_node):
    """
    判断两个非叶子节点是否可以聚类一类
    根据其子孙叶子节点聚类的相似度
    """

    x_clusters = []

    for desc in x_node.descendants:
        if desc.cluster_id != -1:
            x_clusters.append(desc.cluster_id)

    y_clusters = []

    for desc in y_node.descendants:
        if desc.cluster_id != -1:
            y_clusters.append(desc.cluster_id)

    counter = 0
    for x_cluster_id in x_clusters:
        for y_cluster_id in y_clusters:
            if x_cluster_id == y_cluster_id:
                counter += 2

    if len(x_clusters) + len(y_clusters) != 0 and counter / (len(x_clusters) + len(y_clusters)) >= 0.5:
        return True
    else:
        return False
