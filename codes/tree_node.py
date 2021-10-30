from codes.utility import ChangedType


class TreeNode(object):
    """
    xml树节点
    """

    def __init__(self, xml_node, layer):
        self.xml_node = xml_node
        self.attrib = {}
        for key, value in xml_node.attrib.items():
            self.attrib[key] = xml_node.attrib[key]

        # 添加一个attrib 即列表内部节点相对于列表左上角的位置
        self.attrib['rel_bounds'] = ''

        self.parent = None
        self.children = []
        self.descendants = []  # 节点的子孙节点

        self.list_ans = None  # 倘若节点在列表内部 那么记录其祖先节点 这个祖先节点就是这个列表

        self.dynamic_changed_type = ChangedType.REMAIN

        # 判断是否存在于列表中
        self.is_in_list = False

        # 用map来存储属性的变化状态
        self.dynamic_changed_attrs = {
            'class': 0,
            'resource-id': 0,
            'text': 0,
            'content-desc': 0,
            'location': 0,
            'size': 0,
            'color': 0
        }

        # 对比后发生变化的属性
        self.real_changed_attrs = {
            'class': 0,
            'resource-id': 0,
            'text': 0,
            'content-desc': 0,
            'location': 0,
            'size': 0,
            'color': 0
        }

        self.idx = -1  # 在结点数组中的序号
        self.layer = layer  # 层级
        self.class_index = -1

        self.full_xpath = ''  # 绝对路径
        self.xpath = []  # 所有有效的相对路径

        self.width = -1
        self.height = -1

        # 节点左上角坐标
        self.x_loc = -1
        self.y_loc = -1

        self.cluster_id = -1  # 所属聚类id

        # 用于对比时判断该节点是否已有匹配对象
        self.matched_node = None
        # 判断该节点跨版本对比时是否发生变化
        self.has_changed = False

        # 记录节点来源于哪个xml文件 编号从1开始
        self.source_xml_id = -1

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

    def get_bounds(self):
        """
        获取节点的长和宽，坐标
        """
        if 'bounds' in self.attrib:
            x1, y1, x2, y2 = self.parse_bounds()
            self.x_loc = x1
            self.y_loc = y1
            self.width = x2 - x1
            self.height = y2 - y1

    def construct_rel_bounds(self, list_node):
        """
        构造列表节点中的节点相对于列表的位置
        """

        x1, y1, x2, y2 = self.parse_bounds()

        rel_x1 = x1 - list_node.x_loc
        rel_y1 = y1 - list_node.y_loc
        rel_x2 = x2 - list_node.x_loc
        rel_y2 = y2 - list_node.y_loc

        rel_bounds = '[' + str(rel_x1) + ',' + str(rel_y1) + ']' + '[' + str(rel_x2) + ',' + str(rel_y2) + ']'

        self.attrib['rel_bounds'] = rel_bounds

    def parse_rel_bounds(self):
        """
        解析rel_bounds
        """

        bounds = self.attrib['rel_bounds']
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

        # 返回元素相对于列表节点左上角和右下角坐标
        return x1, y1, x2, y2

    def get_descendants(self, node):
        """
        获取所有子孙节点 dfs
        """
        if not node.children:
            return

        for child_node in node.children:
            self.descendants.append(child_node)
            self.get_descendants(child_node)
