# coding=utf-8

ying_ye_zhi_zhao_dict = {
    u'注册号/统一社会信用代码': 'registrationno',
    u'统一社会信用代码/注册号': 'registrationno',
    u'统一社会信用代码': 'tyshxy_code',
    u'注册号': 'zch',
    u'企业名称': 'enterprisename',
    u'类型': 'enterprisetype',
    u'法定代表人': 'legalrepresentative',
    u'法人代表': 'legalrepresentative',
    u'注册资本': 'registeredcapital',
    u'成立日期': 'establishmentdate',
    u'营业期限自': 'validityfrom',
    u'营业期限至': 'validityto',
    u'登记机关': 'registrationinstitution',
    u'核准日期': 'approvaldate',
    u'登记状态': 'registrationstatus',
    u'住所': 'residenceaddress',
    u'经营范围': 'businessscope',
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
    u'省份': 'province',
    u'迁入地工商局': 'qrdgsj',
    u'业务范围': 'businessscope',
    u'名称': 'enterprisename',
    u'注册日期': 'establishmentdate',
    u'注册资金': 'registeredcapital',
    u'经营期限自': 'validityfrom',
    u'经营期限至': 'validityto',
    u'地址': 'businessplace',
}

bian_geng_dict = {
    u'变更前内容': 'changedannouncement_before',  # 变更前
    u'变更后内容': 'changedannouncement_after',  # 变更后
    u'变更事项': 'changedannouncement_events',  # 变更事项
    u'变更日期': 'changedannouncement_date',  # 变更日期
}

gu_dong_dict = {
    u'证照/证件号码': 'shareholder_certificationno',  # 证照/证件号码
    u'股东名称': 'shareholder_name',  # 股东名称
    u'证照/证件类型': 'shareholder_certificationtype',  # 证照/证件类型
    u'股东类型': 'shareholder_type',  # 股东类型
    u'认缴出资额': 'subscripted_capital',  # 认缴出资额
    u'实缴出资额': 'actualpaid_capital',  # 实缴出资额
    u'认缴出资方式': 'subscripted_method',  # 认缴出资方式
    u'实缴出资方式': 'actualpaid_method',  # 实缴出资方式
    u'认缴出资日期': 'subscripted_time',  # 认缴出资日期
    u'实缴出资日期': 'actualpaid_time',  # 实缴出资日期
    u'认缴出资额(万元)': 'subscripted_amount',  # 认缴出资额（万元）
    u'实缴出资额(万元)': 'actualpaid_amount',  # 实缴出资额（万元）
    u'认缴明细': 'rjmx',  # 认缴明细json数组
    u'实缴明细': 'sjmx',  # 实缴明细json数组
}

qing_suan_dict = {
    u'清算组负责人': 'liquidation_pic',  # 清算组负责人
    u'清算组成员': 'liquidation_member',  # 清算组成员
}

gu_quan_chu_zhi_dict = {
    # "altDate": "",  # 变更日期
    # "canDate": '',
    # "cancelDate": '',
    # "cancelRea": "",
    # "equPleCanRea": "",
    u"股权出质设立登记日期": 'equitypledge_registrationdate',  # 股权出质设立登记日期
    u"登记编号": 'equitypledge_registrationno',  # 登记编号
    u"出质股权数额": 'equitypledge_amount',  # 出质股权数额
    u"质权人": 'equitypledge_pawnee',  # 质权人
    u"质权人证照/证件号码": 'equitypledge_pawneeid',  # 质权人证件号码
    # "impOrgBLicType_CN": "",
    # "impOrgCerNo": "",
    # "impOrgCerType_CN": "",
    # "impOrgId": "ff808081529c41fb0152b0556c883de5",
    # "pledAmUnit": "",
    u"出质人证照/证件号码": "equitypledge_pledgorid",  # 出质人证件号码
    # "pledBLicType_CN": "",
    # "pledCerNo": "",
    # "pledCerType_CN": "",
    u"出质人": 'equitypledge_pledgor',  # 出质人
    u"公示日期": 'equitypledge_announcedate',  # 公示日期
    # "regCapCur_CN": "",  # 出质股权币种单位
    u"状态": "equitypledge_status",  # 状态
    # "type_CN": "",
    # "vStakQualitInfoAlt": ''
}

dong_chan_di_ya_dict = {
    # "canDate": null,
    # "morCanRea_CN": "",
    u"登记编号": "chattelmortgage_registrationno",  # 登记编号
    # "morReg_Id": "PROVINCENODENUM130000a0a0e3984ee39312014f6e223a051bc3",  # id
    u"被担保债权数额": 'chattelmortgage_guaranteedamount',  # 被担保债权数额
    u"公示日期": 'chattelmortgage_announcedate',  # 公示日期
    # "regCapCur_Cn": "人民币",  # 被担保数额币种
    u"登记机关": "chattelmortgage_registrationinstitution",  # 登记机关
    u"登记日期": 'chattelmortgage_registrationdate',  # 登记日期
    u"状态": "chattelmortgage_status",  # 状态
    # "type_CN": ""，
}

jing_ying_yi_chang_dict = {
    u"作出决定机关(列入)": "abnormal_decisioninstitution_in",  # 作出决定机关(列入)
    u"作出决定机关(移出)": "abnormal_decisioninstitution_out",  # 作出决定机关(移出)
    u"作出决定机关（列入）": "abnormal_decisioninstitution_in",  # 作出决定机关(列入)
    u"作出决定机关（移出）": "abnormal_decisioninstitution_out",  # 作出决定机关(移出)
    u"移出经营异常名录原因": "abnormal_moveoutreason",  # 移出经营异常名录原因
    u"列入经营异常名录原因": "abnormal_events",  # 列入经营异常名录原因
    u"列入日期": "abnormal_datesin",  # 列入日期
    u"移出日期": "abnormal_datesout",  # 移出日期
}

chou_cha_jian_cha_dict = {
    u'检查实施机关': 'check_institution',  # 检查实施机关
    u'结果': 'check_result',  # 结果
    u'日期': 'check_date',  # 日期
    u'备注': 'check_remark',  # 备注
    u'类型': 'check_type',  # 类型
}

xing_zheng_chu_fa_dict = {
    # u"illegActType": "penalty_illegaltype",  # 违法行为类型
    # u"penAuth_CN": "penalty_decisioninsititution",  # 决定机关名称
    # u"penContent": "penalty_decisioncontent",  # 行政处罚内容
    # u"penDecIssDate": 'penalty_decisiondate',  # 处罚决定日期
    # u"行政处罚决定书文号": "penalty_code",  # 决定书文号
    # u"publicDate": 'penalty_announcedate',  # 公示日期
    # u"处罚名称": '',
    # u"处罚事由": 'penalty_illegaltype',
    # u"处罚依据": '',
    # u"处罚结果": '',
    u"公示日期": 'penalty_announcedate',  # 公示日期
    u"决定机关名称": "penalty_decisioninsititution",  # 决定机关名称
    u"行政处罚内容": "penalty_decisioncontent",  # 行政处罚内容
    u"违法行为类型": "penalty_illegaltype",  # 违法行为类型
    u"行政处罚决定书文号": 'penalty_code',
    u"决定书文号": 'penalty_code',
    u"处罚名称": 'penalty_name',  # 新添加
    u"处罚事由": 'penalty_illegaltype',
    u"处罚依据": 'penbasis',  #
    u"处罚结果": 'penalty_decisioncontent',
    u"处罚决定日期": 'penalty_decisiondate',
}
