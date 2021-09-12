class TreeNode(object):
    """
    xml树节点
    """

    def __init__(self, xml_node, level):
        self.xml_node = xml_node
        self.attrib = {}
        for key, value in xml_node.attrib.items():
            self.attrib[key] = xml_node.attrib[key]
        self.parent = None
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
