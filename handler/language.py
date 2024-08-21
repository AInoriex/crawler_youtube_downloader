def GetLanguageCloudSavePath(src_path:str, lang_key:str)->str:
    ''' 根据数据记录语言生成云端存储路径
    @Exp.Paras  src_path: /DATA/{LANGUAGE}/youtube/ db_lang: vt
    @Return     /DATA/Vietnam/youtube/
    '''
    ret_path = str("")   
    LANGUAGE_PATH_DICT = {
        "vi": "Vietnam", # 越南语
        "yue": "Yueyu", # 粤语
        "nan": "Minnanyu", # 闽南语
        "th": "Taiyu", # 泰语
        "id": "Yinniyu", # 印尼语
        "ms": "Malaiyu", # 马来语
        "fil": "Feilvbinyu", # 菲律宾语
    }
    if "{LANGUAGE}" in src_path:
        ret_path = src_path.format(LANGUAGE=LANGUAGE_PATH_DICT.get(lang_key, "Unclassify"))
    else:
        ret_path = src_path
    return ret_path