# coding=utf-8
ji_ben_dict = {
    'uniscid': 'registrationno',
    'entname': 'enterprisename',      #企业名称
    'traname': 'enterprisename',      #企业名称
    'province': 'province',
    'lerep': 'legalrepresentative',   # 法人代表
    'enttype': 'enterprisetype',     # 企业类型
    'estdate': 'establishmentdate',      # 成立日期
    'regcap': 'registeredcapital',      # 注册资本
    'opername': 'operator',           # 经营者
    'dom': 'residenceaddress',         # 地址
    'opfrom': 'validityfrom',          # 营业日期自
    'opto': 'validityto',            # 营业日期至
    'opscope': 'businessscope',        # 经营范围
    'compform': 'compositionform',        # 组成形式
    'regorg': 'registrationinstitution',   # 登记机构
    'apprdate': 'approvaldate',           # 核准日期
    'regstate': 'registrationstatus',  # 状态
    'pril': 'principal',
    'oploc': 'businessplace',           # 经营场所
    'revdate': 'revocationdate',
    'pripid': 'pripid',                 # 唯一id
    # 'entcat' : 'entcat',               # 未知字段名
    # 'localadmin': 'localadmin',         # 未知字段名
    'regno' : 'zch',                   # 注册号
   'tyshxy_code': 'tyshxy_code',       # 统一社会信用代码
    # 'xzqh' : 'xzqh',                    # 未知字段名
}


gu_dong_dict = {
    'invtype': 'shareholder_type',  # 股东类型
    'inv': 'shareholder_name',  # 股东
    'blictype': 'shareholder_certificationtype',  # 证照/证件类型
    'blicno': 'shareholder_certificationno',  # 证件号码
    'lisubconam': 'subscripted_capital',  # 认缴额
    'liacconam': 'actualpaid_capital',  # 实缴额
    'subconform': 'subscripted_method',  # 认缴出资方式modify by guan
    'subconam': 'subscripted_amount',  # 认缴出资额（万元）modify by guan
#     'condate': 'subscripted_time',  # 认缴出资日期  山东
    'subtime': 'subscripted_time',  # 认缴出资日期 modify by guan
    'actconform': 'actualpaid_method',  # 实缴出资方式 modify by guan
    'actconam': 'actualpaid_amount',  # 实缴出资额（万元）
    'acttime': 'actualpaid_time'  # 实缴出资日期 modify by guan
}

bian_geng_dict = {
    'altaf': 'changedannouncement_after',  # 变更后
    'altbe': 'changedannouncement_before',  # 变更前
    'altitem': 'changedannouncement_events',  # 变更事项
    'altdate': 'changedannouncement_date',  # 变更日期
}

zhu_yao_ren_yuan_dict = {
    'name': 'keyperson_name',  # 姓名
    'position': 'keyperson_position',  # 职务
}

DICInfo_column_dict = { 'invtype': 'DIC_Info:dic_sponsortype',  #出资人类型
                        'inv': 'DIC_Info:dic_sponsorname',   # 出资人
                        'blictype':'DIC_Info:dic_idtype',    # 证照/证件类型
                        'blicno': 'DIC_Info:dic_idno',       # 证照/证件号码
                        }

fen_zhi_ji_gou_dict = {
    'brname': 'branch_registrationname',  # 名称
    'regno': 'branch_registrationno',  # 统一社会信用代码/注册号
    'regorg': 'branch_registrationinstitution'  # 登记机关
    
}

qing_suan_dict = {

}

dong_chan_di_ya_dict = {
    'morregcno': 'chattelmortgage_registrationno',  # 登记编号
    'regidate': 'chattelmortgage_registrationdate',  # 登记日期
    'regorg': 'chattelmortgage_registrationinstitution',  # 登记机关
    'priclasecam': 'chattelmortgage_guaranteedamount',  # 被担保债权数额
    'type': 'chattelmortgage_status',  # 状态
    'pefperform': 'chattelmortgage_announcedate'  # 公示时间
}


dcdydj_column_dict = {u'登记编号':'dcdyzx:dcdy_djbh',
                      u'登记日期':'dcdyzx:dcdy_djrq',
                      u'登记机关':'dcdyzx:dcdy_djjg',
                      u'被担保债权种类':'dcdyzx:dcdy_bdbzqzl',
                      u'被担保债权数额':'dcdyzx:dcdy_bdbzqsl',
                      u'债务人履行债务的期限':'dcdyzx:dcdy_lxqx',
                      u'担保范围':'dcdyzx:dcdy_dbfw',
                      u'备注':'dcdyzx:dcdy_bz'}

bdbzqgk_column_dict = {u'种类':'bdbzqgk:dbzq_zl',
                      u'数额':'bdbzqgk:dbzq_sl',
                      u'担保的范围':'bdbzqgk:dbzq_fw',
                      u'债务人履行债务的期限':'bdbzqgk:dbzq_qx',
                      u'备注':'bdbzqgk:dbzq_bz'}

dyqrgk_column_dict = {u'抵押权人名称':'dyqrgk:dyqr_mc',
                      u'抵押权人证照/证件类型':'dyqrgk:dyqr_zzlx',
                      u'证照/证件号码':'dyqrgk:dyqr_zzhm'}

dywgk_column_dict = {u'名称':'dywgk:dyw_mc',
                      u'所有权归属':'dywgk:dyw_gs',
                      u'数量、质量、状况、所在地等情况':'dywgk:dyw_xq',
                      u'备注':'dywgk:dyw_bz'}

dcdybg_column_dict = {u'变更日期':'dcdybg:dcdy_bgrq',
                      u'变更内容':'dcdybg:dcdy_bgnr'}

gqczzx_biangeng_dict = {u'变更日期':'gqczzx:gqcz_bgrq',
                      u'变更内容':'gqczzx:gqcz_bgnr'}

gu_quan_chu_zhi_dict = {
    'equityno': 'equitypledge_registrationno',  # 登记编号
    'pledgor': 'equitypledge_pledgor',  # 出质人
    'blicno': 'equitypledge_pledgorid',  # 证照/证件号码(出质人)
    'impam': 'equitypledge_amount',  # 出质股权数额 modify by guan  
    'imporg': 'equitypledge_pawnee',  # 质权人
    'impmorblicno': 'equitypledge_pawneeid',  # 证照/证件号码(质权人)
    'equpledate': 'equitypledge_registrationdate',  # 股权出质设立登记日期
    'type': 'equitypledge_status',  # 状态 modify by guan  1 代表【有效】
    'gstimeStr': 'equitypledge_announcedate',  # 公示时间

}

xing_zheng_chu_fa_dict = {
    'pendecno': 'penalty_code',  # 行政处罚决定书文号
    'illegacttype': 'penalty_illegaltype',  # 违法行为类型
    'penam': 'penalty_decisioncontent',  # 行政处罚内容
    'penauthName': 'penalty_decisioninsititution',  # 作出行政处罚决定机关名称
    'pendecissdateStr': 'penalty_decisiondate',  # 作出行政处罚决定日期
}

jing_ying_yi_chang_dict = {
    'specause': 'abnormal_events',  # 列入经营异常名录原因
    'abntime': 'abnormal_datesin',  # 列入日期
    'remexcpres': 'abnormal_moveoutreason',  # 移出经营异常名录原因
    'remdate': 'abnormal_datesout',  # 移出日期
    'decorg': 'abnormal_decisioninstitution'  # 作出决定机关
}

yan_zhong_wei_fa_dict = {
    'serillreaName': 'serious_events',  # 列入严重违法企业名单原因
    'abntimeStr': 'serious_datesin',  # 列入日期
    'remexcpresName': 'serious_moveoutreason',  # 移出严重违法企业名单原因
    'remdateStr': 'serious_datesout',  # 移出日期
    'decorgName': 'serious_decisioninstitution'  # 作出决定机关

}

chou_cha_jian_cha_dict = {
    'insauthname': 'check_institution',  # 检查实施机关
    'instype': 'check_type',  # 类型
    'insdate': 'check_date',  # 日期
    'insres': 'check_result',  # 结果
}
