# coding=utf-8
ji_ben_dict = {
    u'注册号': 'registrationno',
    u'名称': 'enterprisename',
    u'省份': 'province',
    u'法定代表人': 'legalrepresentative',
    u'类型': 'enterprisetype',
    u'注册日期': 'establishmentdate',
    u'成立日期': 'establishmentdate',
    u'注册资本': 'registeredcapital',
    u'注册资金': 'registeredcapital',
    u'住所': 'residenceaddress',
    u'营业期限自': 'validityfrom',
    u'营业期限至': 'validityto',
    u'经营期限自': 'validityfrom',
    u'经营期限至': 'validityto',
    u'经营范围': 'businessscope',
    u'登记机关': 'registrationinstitution',
    u'核准日期': 'approvaldate',
    u'登记状态': 'registrationstatus',
    u'负责人': 'principal',
    u'经营场所': 'businessplace',
    u'营业场所': 'businessplace',
    u'修改日期': 'lastupdatetime',
    u'吊销日期': 'revocationdate',
    u'投资人': 'investor',
    u'主要经营场所': 'mianbusinessplace',
    u'合伙期限自': 'partnershipfrom',
    u'合伙期限至': 'partnershipto',
    u'执行事务合伙人': 'executivepartner',
    u'组成形式': 'compositionform',
    u'经营者': 'operator',
    u'首席代表': 'chiefrepresentative',
    u'派出企业名称': 'enterpriseassigning',
    u'成员出资总额': 'totalcontributionofmembers',
    u'统一社会信用代码': 'tyshxy_code',
    u'省份': 'province',
    u'经营状态': 'entstatus'
}

tou_zi_ren_dict = {
    u'投资人类型': 'investor_type',
    u'投资人': 'investor_name',
    u'证照类型': 'investor_certificationtype',
    u'证照号码': 'investor_certificationno',
    u'详情': 'investor_details',
    u'股东': 'investor_name',
    u'认缴额（万元）': 'ivt_subscripted_capital',
    u'实缴额（万元）': 'ivt_actualpaid_capital',
    u'认缴出资方式': 'ivt_subscripted_method',
    u'认缴出资额（万元）': 'ivt_subscripted_amount',
    u'认缴出资日期': 'ivt_subscripted_time',
    u'实缴出资方式': 'ivt_actualpaid_method',
    u'实缴出资额（万元）': 'ivt_actualpaid_amount',
    u'实缴出资日期': 'ivt_actualpaid_time',
}
gu_dong_dict = {
    u'股东': 'shareholder_name',
    u'股东名称': 'shareholder_name',
    u'股东（发起人）名称': 'shareholder_name',  # 股东 股东(发起人)名称
    u'股东(发起人)名称': 'shareholder_name',  # 股东 股东(发起人)名称
    u'发起人名称': 'shareholder_name',
    u'发起人': 'shareholder_name',
    u'股东类型': 'shareholder_type',  # 股东类型
    u'发起人类型': 'shareholder_type',
    u'股东（发起人）': 'shareholder_name',  # 股东
    u'股东（发起人）类型': 'shareholder_type', # 股东类型
    u'证照/证件类型': 'shareholder_certificationtype',  # 证照/证件类型
    u'证照/证件号码': 'shareholder_certificationno',  # 证件号码
    u'认缴额（万元）': 'subscripted_capital',  # 认缴额
    u'实缴额（万元）': 'actualpaid_capital',  # 实缴额
    u'认缴出资方式': 'subscripted_method',  # 认缴出资方式
    u'认缴出资额（万元）': 'subscripted_amount',  # 认缴出资额（万元）
    u'认缴出资日期': 'subscripted_time',  # 认缴出资日期
    u'实缴出资方式': 'actualpaid_method',  # 实缴出资方式
    u'实缴出资额（万元）': 'actualpaid_amount',  # 实缴出资额（万元）
    u'实缴出资日期': 'actualpaid_time'  # 实缴出资日期
}

bian_geng_dict = {
    u'变更后内容': 'changedannouncement_after',  # 变更后
    u'变更前内容': 'changedannouncement_before',  # 变更前
    u'变更事项': 'changedannouncement_events',  # 变更事项
    u'变更日期': 'changedannouncement_date',  # 变更日期
}

zhu_yao_ren_yuan_dict = {
    u'姓名': 'keyperson_name',  # 姓名
    u'职务': 'keyperson_position',  # 职务
    u'序号': 'keyperson_no'
}

fen_zhi_ji_gou_dict = {
    u'名称': 'branch_registrationname',  # 名称
    u'注册号': 'branch_registrationno',  # 统一社会信用代码/注册号
    u'登记机关': 'branch_registrationinstitution',  # 登记机关
    u'序号': 'branch_no'
}

qing_suan_dict = {

}

dong_chan_di_ya_dict = {
    u'登记编号': 'chattelmortgage_registrationno',  # 登记编号
    u'登记日期': 'chattelmortgage_registrationdate',  # 登记日期
    u'登记机关': 'chattelmortgage_registrationinstitution',  # 登记机关
    u'被担保债权数额': 'chattelmortgage_guaranteedamount',  # 被担保债权数额
    u'状态': 'chattelmortgage_status',  # 状态
    u'序号': 'chattelmortgage_no',
    u'详情': 'chattelmortgage_details',
    #  'gstimeStr': 'chattelmortgage_announcedate'  # 公示时间
}

gu_quan_chu_zhi_dict = {
    u'序号': 'equitypledge_no',
    u'登记编号': 'equitypledge_registrationno',  # 登记编号
    u'出质人': 'equitypledge_pledgor',  # 出质人
    u'证照/证件号码(出质人)': 'equitypledge_pledgorid',  # 证照/证件号码(出质人)
    u'出质股权数额': 'equitypledge_amount',
    u'质权人': 'equitypledge_pawnee',  # 质权人
    u'证照/证件号码(质权人)': 'equitypledge_pawneeid',  # 证照/证件号码(质权人)
    u'股权出质设立登记日期': 'equitypledge_registrationdate',  # 股权出质设立登记日期
    u'状态': 'equitypledge_status',  # 状态
    u'详情': 'equitypledge_detail',  #
    u'变化情况': 'equitypledge_change'

}

xing_zheng_chu_fa_dict = {
    u'行政处罚决定书文号': 'penalty_code',  # 行政处罚决定书文号
    u'决定书文号':  'penalty_code',  # 行政处罚决定书文号
    u'违法行为类型': 'penalty_illegaltype',  # 违法行为类型
    u'行政处罚内容': 'penalty_decisioncontent',  # 行政处罚内容
    u'作出行政处罚决定机关名称': 'penalty_decisioninsititution',  # 作出行政处罚决定机关名称
    u'决定机关名称': 'penalty_decisioninsititution',  # 作出行政处罚决定机关名称
    u'作出行政处罚决定日期': 'penalty_decisiondate',  # 作出行政处罚决定日期
    u'处罚决定日期':  'penalty_decisiondate',  # 作出行政处罚决定日期
    u'详情': 'penalty_details',
    u'序号': 'penalty_no',
    u'公示日期': 'penalty_publicationdate',
    u'详情': 'penalty_details'

}

jing_ying_yi_chang_dict = {
    u'列入经营异常名录原因': 'abnormal_events',  # 列入经营异常名录原因
    u'列入日期': 'abnormal_datesin',  # 列入日期
    u'移出经营异常名录原因': 'abnormal_moveoutreason',  # 移出经营异常名录原因
    u'移出日期': 'abnormal_datesout',  # 移出日期
    u'作出决定机关': 'abnormal_decisioninstitution',  # 作出决定机关
    u'作出决定机关（列入）': 'abnormal_decisioninstitution',  # 作出决定机关
    u'序号': 'abnormal_no'
}

yan_zhong_wei_fa_dict = {
    u'列入严重违法企业名单原因': 'serious_events',  # 列入严重违法企业名单原因
    u'列入严重违法失信企业名单原因': 'serious_events',
    u'列入日期': 'serious_datesin',  # 列入日期
    u'移出严重违法企业名单原因': 'serious_moveoutreason',  # 移出严重违法企业名单原因
    u'移出严重违法失信企业名单原因': 'serious_moveoutreason',
    u'移出日期': 'serious_datesout',  # 移出日期
    u'作出决定机关': 'serious_decisioninstitution',  # 作出决定机关
    u'序号': 'serious_no'

}

chou_cha_jian_cha_dict = {
    u'序号': 'check_no',
    u'检查实施机关': 'check_institution',  # 检查实施机关
    u'类型': 'check_type',  # 类型
    u'日期': 'check_date',  # 日期
    u'结果': 'check_result',  # 结果
    u'备注': 'check_remark'  # 备注
}
