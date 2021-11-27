from ltp import LTP


class LtpParser:
    def __init__(self):
        self.ltp = LTP()

    def format_labelrole(self, hidden):
        """
        由：
            [[[], [('A0', 0, 0), ('A1', 2, 7)], [], [('A0', 7, 7)], [], [('A0', 7, 7)], [], []]]
        得到：
            {1: {'A0': ('A0', 0, 0), 'A1': ('A1', 2, 7)}, 3: {'A0': ('A0', 7, 7)}, 5: {'A0': ('A0', 7, 7)}}
        字典的值是索引
        :param hidden:
        :return:
        """
        srl = self.ltp.srl(hidden)  # 语义角色标注
        roles_dict = {}
        for i, tmp in enumerate(srl[0]):
            if len(tmp) != 0:
                roles_dict[i] = {arg[0]: arg for arg in tmp}
        return roles_dict

    """为句子中的每个词语维护一个保存依存儿子节点的字典"""

    def build_parse_child_dict(self, segment, pos, dep):
        """
        :param segment:
        :param pos:
        :param dep: [[(1, 2, 'SBV'), (2, 0, 'HED'), (3, 8, 'ATT'), (4, 8, 'ATT'), (5, 6, 'WP'), (6, 4, 'COO'), (7, 4, 'RAD'), (8, 2, 'VOB')]]
        :return:
        """
        dep = dep[0]
        segment = segment[0]
        pos = pos[0]
        child_dict_list = []
        format_parse_list = []
        # [2, 0, 8, 8, 6, 4, 4, 2]
        rely_id = [d[1] for d in dep]  # 依存父节点id
        # print(rely_id)
        # ['SBV', 'HED', 'ATT', 'ATT', 'WP', 'COO', 'RAD', 'VOB']
        relation = [d[2] for d in dep]  # 获取依存关系
        # print(relation)
        heads = ['Root' if id == 0 else segment[id - 1] for id in rely_id]  # 匹配依存父节点词语
        for index in range(len(segment)):
            child_dict = {}
            for dep_index in range(len(dep)):
                if dep[dep_index][1] == index + 1:  # 如果依存父节点是当前词index+1
                    if dep[dep_index][2] in child_dict:
                        child_dict[dep[dep_index][2]].append(dep_index)
                    else:
                        child_dict[dep[dep_index][2]] = []
                        child_dict[dep[dep_index][2]].append(dep_index)
            child_dict_list.append(child_dict)
        for i in range(len(segment)):
            a = [relation[i], segment[i], i, pos[i], heads[i], rely_id[i] - 1, pos[rely_id[i] - 1]]
            format_parse_list.append(a)
        # child_dict_list
        # 索引是每个词，里面的值表示和当前词的依存关系以及词索引位置
        # [{}, {'SBV': [0], 'VOB': [7]}, {}, {'COO': [5], 'RAD': [6]}, {}, {'WP': [4]}, {}, {'ATT': [2, 3]}]
        # format_parse_list
        # 每个子列表的含义：[依存关系,词1,词1位置,词1词性,词2,词2位置,词2词性]
        # [['SBV', '中国', 0, 'ns', '是', 1, 'v'], ['HED', '是', 1, 'v', 'Root', -1, 'n'], ['ATT', '一个', 2, 'm', '国家', 7, 'n'], ['ATT', '和平', 3, 'a', '国家', 7, 'n'], ['WP', '、', 4, 'wp', '自由', 5, 'a'], ['COO', '自由', 5, 'a', '和平', 3, 'a'], ['RAD', '的', 6, 'u', '和平', 3, 'a'], ['VOB', '国家', 7, 'n', '是', 1, 'v']]
        return child_dict_list, format_parse_list

    def parser_main(self, sentence):
        segment, hidden = self.ltp.seg([sentence])  # 分词
        pos = self.ltp.pos(hidden)  # 词性标注
        ner = self.ltp.ner(hidden)  # 命名实体识别
        # srl = self.ltp.srl(hidden)  # 语义角色标注
        roles_dict = self.format_labelrole(hidden)
        dep = self.ltp.dep(hidden)  # 依存句法分析
        # sdp = self.ltp.sdp(hidden)  # 语义依存分析
        # print(srl)
        # print(roles_dict)
        # print(dep)
        child_dict_list, format_parse_list = self.build_parse_child_dict(
            segment,
            pos,
            dep
        )
        # print(child_dict_list)
        # print(format_parse_list)
        return segment[0], pos[0], child_dict_list, roles_dict, format_parse_list


if __name__ == '__main__':
    ltpParser = LtpParser()
    # sentence = '昨日，在伊拉克发生了恐怖袭击。据悉，此次袭击造成3人死亡'
    sentence = "中国是一个和平、自由的国家"
    words, postags, child_dict_list, roles_dict, arcs = ltpParser.parser_main(sentence)
    print("分词结果：", words)
    print("词性标注结果：", postags)
    print("child_dict_list：", child_dict_list)
    print("roles_dict：", roles_dict)
    print("arcs：", arcs)
