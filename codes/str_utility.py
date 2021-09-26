def delete_num_in_str(str):
    """
    删除字符串中的数字
    """
    new_str = ''

    for s in str:
        try:
            int(s)
        except:
            new_str += s
    return new_str
