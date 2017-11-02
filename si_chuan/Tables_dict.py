# coding=utf-8

jiben_column_dict = {u'统一社会信用代码/注册号': 'Registered_Info:registrationno',
            u'注册号/统一社会信用代码': 'Registered_Info:registrationno',             # modified by jing
            u'注册号': 'Registered_Info:registrationno',     
            u'统一社会信用代码': 'Registered_Info:registrationno',                  # modified by jing
            u'名称': 'Registered_Info:enterprisename',
            u'企业名称': 'Registered_Info:enterprisename',        # new in 20161220 v4
            u'省份': 'Registered_Info:province',
            u'法定代表人': 'Registered_Info:legalrepresentative',
            u'经营者': 'Registered_Info:operator',                              # modified by jing
            u'类型': 'Registered_Info:enterprisetype',
            u'组成形式': 'Registered_Info:compositionform',                       # modified by jing
            u'成立日期': 'Registered_Info:establishmentdate',
            u'注册日期': 'Registered_Info:establishmentdate',                    # modified by jing
            u'注册资本': 'Registered_Info:registeredcapital', 
            u'注册资金': 'Registered_Info:registeredcapital',                    # modified by jing
            u'住所': 'Registered_Info:residenceaddress',
            u'营业期限自': 'Registered_Info:validityfrom',
            u'营业期限至': 'Registered_Info:validityto',
            u'经营期限自': 'Registered_Info:validityfrom',
            u'经营期限至': 'Registered_Info:validityto',
            u'经营范围': 'Registered_Info:businessscope',
            u'业务范围': 'Registered_Info:businessscope',
            u'登记机关': 'Registered_Info:registrationinstitution',
            u'核准日期': 'Registered_Info:approvaldate',
            u'登记状态': 'Registered_Info:registrationstatus',
            u'负责人': 'Registered_Info:principal',
            u'营业场所': 'Registered_Info:businessplace',
            u'经营场所': 'Registered_Info:businessplace',                        # modified by jing
            u'注销日期': 'Registered_Info:revocationdate',                    # modified @20170223
            u'吊销时间': 'Registered_Info:revocationdate',
            u'投资人': 'Registered_Info:investor',
            u'执行事务合伙人': 'Registered_Info:executivepartner',
            u'主要经营场所': 'Registered_Info:mianbusinessplace',
            u'合伙期限自': 'Registered_Info:partnershipfrom',
            u'合伙期限至': 'Registered_Info:partnershipto',
            u'吊销日期': 'Registered_Info:dxrq',
            u'成员出资总额': 'Registered_Info:totalcontributionofmembers',
            u'详情页url': 'Registered_Info:detailpageurl'}                               # modified by jing

gudong_column_dict = {u'股东类型': 'Shareholder_Info:shareholder_type',
                      u'合伙人类型': 'Shareholder_Info:shareholder_type',  # 1108 new in 肥西合宴福酒店（普通合伙）
                      u'股东（发起人）类型':'Shareholder_Info:shareholder_type',
                      u'发起人名称':'Shareholder_Info:shareholder_name',  # new in 20170425
                      u'主管部门名称':'Shareholder_Info:shareholder_name',  # new in 20170227
                      u'主管部门类型':'Shareholder_Info:shareholder_type', # new in 20170227
                      u'发起人类型':'Shareholder_Info:shareholder_type',
                       u'股东': 'Shareholder_Info:shareholder_name',
                      u'姓名':  'Shareholder_Info:shareholder_name',  # new in 20170227
                       u'合伙人':'Shareholder_Info:shareholder_name',  # 1108 new in 肥西合宴福酒店（普通合伙）
                       u'发起人':'Shareholder_Info:shareholder_name',
                       u'股东名称':'Shareholder_Info:shareholder_name',
                       u'股东（发起人）':'Shareholder_Info:shareholder_name',
                       u'证照/证件类型':'Shareholder_Info:shareholder_certificationtype',
                       u'证照/证件号码':'Shareholder_Info:shareholder_certificationno',
                      u'证照/证件编号':'Shareholder_Info:shareholder_certificationno',  # new in 20170227
                       u'详情':'Shareholder_Info:shareholder_details',
                       u'认缴明细':'Shareholder_Info:rjmx',
                       u'实缴明细':'Shareholder_Info:sjmx',
                       u'认缴额（万元）':'Shareholder_Info:subscripted_capital',
                       u'实缴额（万元）':'Shareholder_Info:actualpaid_capital',
                       u'认缴出资方式':'Shareholder_Info:subscripted_method',
                      u'出资方式':'Shareholder_Info:subscripted_method', # new in 20170227
                       u'认缴出资额（万元）':'Shareholder_Info:subscripted_amount',
                       u'认缴出资日期':'Shareholder_Info:subscripted_time',
                       u'实缴出资方式':'Shareholder_Info:actualpaid_method',
                       u'实缴出资额（万元）':'Shareholder_Info:actualpaid_amount',
                       u'实缴出资日期':'Shareholder_Info:actualpaid_time',
                      u'公示日期': 'Shareholder_Info:actualpaid_time', # new in 20170227
                      u'序号':'Equity_Pledge:equitypledge_no',}

touziren_column_dict ={u'序号': 'Investor_Info:investor_number',
                       u'姓名': 'Investor_Info:investor_name',
                       u'出资方式': 'Investor_Info:investment_method'}

hehuoren_column_dict = {u'合伙人类型': 'Partner_Info:partner_type',
                        u'合伙人信息': 'Partner_Info:partner_name',
                        u'证照/证件类型': 'Partner_Info:partner_certificationtype',
                        u'证照/证件号码': 'Partner_Info:partner_certificationno',
                        u'注册号': 'Partner_Info:registrationno'}

zhuguanbumen_column_dict = {
    u'出资人类型': 'Shareholder_Info:shareholder_type',
    u'出资人': 'Shareholder_Info:shareholder_name',
    u'证照/证件类型': 'Shareholder_Info:shareholder_certificationtype',
    u'证照/证件号码': 'Shareholder_Info:shareholder_certificationno',
}

DICInfo_column_dict = {u'序号': 'DIC_Info:dic_no',
                        u'出资人类型': 'DIC_Info:dic_sponsortype',
                        u'出资人': 'DIC_Info:dic_sponsorname',
                        u'证照/证件类型': 'DIC_Info:dic_idtype',
                        u'证照/证件号码': 'DIC_Info:dic_idno',
                        u'注册号': 'DIC_Info:registrationno'}

biangeng_column_dict = {u'变更事项': 'Changed_Announcement:changedannouncement_events',
                         u'变更前内容': 'Changed_Announcement:changedannouncement_before',
                         u'变更后内容': 'Changed_Announcement:changedannouncement_after',
                         u'变更日期': 'Changed_Announcement:changedannouncement_date',
                         u'注册号': 'Changed_Announcement:registrationno',
                         u'详细': 'Changed_Announcement:changedannouncement_details',
                         u'序号':'Changed_Announcement:changedannouncement_no',
                         }

zhuyaorenyuan_column_dict={u'序号': 'KeyPerson_Info:keyperson_no',
                           u'姓名': 'KeyPerson_Info:keyperson_name',
                           u'职务': 'KeyPerson_Info:keyperson_position'}

jiatingchengyuan_column_dict = {u'序号': 'Family_Info:familymember_no',
                                u'姓名': 'Family_Info:familymember_name',
                                u'职务': 'Family_Info:familymember_position'}

chengyuanmingce_column_dict = {u'序号': 'Members_Info:members_no',
                               u'姓名': 'Members_Info:members_name',
                               u'姓名（名称）': 'Members_Info:members_name'}

fenzhijigou_column_dict = {u'序号': 'Branches:branch_no',
                           u'注册号/统一社会信用代码': 'Branches:branch_registrationno',
                           u'注册号': 'Branches:branch_registrationno',
                           u'名称': 'Branches:branch_registrationname',
                           u'登记机关': 'Branches:branch_registrationinstitution'}

dongchandiyadengji_column_dict = {u'序号': 'Chattel_Mortgage:chattelmortgage_no',
                                  u'登记编号': 'Chattel_Mortgage:chattelmortgage_registrationno',
                                  u'登记日期': 'Chattel_Mortgage:chattelmortgage_registrationdate',
                                  u'登记机关': 'Chattel_Mortgage:chattelmortgage_registrationinstitution',
                                  u'被担保债权数额': 'Chattel_Mortgage:chattelmortgage_guaranteedamount',
                                  u'状态': 'Chattel_Mortgage:chattelmortgage_status',
                                  u'公示日期': 'Chattel_Mortgage:chattelmortgage_announcedate',
                                  u'详情': 'Chattel_Mortgage:chattelmortgage_details'}

guquanchuzhidengji_column_dict = {u'序号': 'Equity_Pledge:equitypledge_no',
                                  u'登记编号': 'Equity_Pledge:equitypledge_registrationno',
                                  u'出质人': 'Equity_Pledge:equitypledge_pledgor',
                                  u'证照/证件号码': 'Equity_Pledge:equitypledge_pledgorid',
                                  u'出质股权数额': 'Equity_Pledge:equitypledge_amount',
                                  u'质权人': 'Equity_Pledge:equitypledge_pawnee',
                                  u'证照/证件号码1': 'Equity_Pledge:equitypledge_pawneeid',
                                  u'股权出质设立登记日期': 'Equity_Pledge:equitypledge_registrationdate',
                                  u'状态': 'Equity_Pledge:equitypledge_status',
                                  u'公示日期': 'Equity_Pledge:equitypledge_announcedate',
                                  u'变化情况': 'Equity_Pledge:equitypledge_change',
                                  u'详情':'Equity_Pledge:equitypledge_details',
                                  }

xingzhengchufa_column_dict = {u'序号': 'Administrative_Penalty:penalty_no',
                              u'行政处罚决定书文号': 'Administrative_Penalty:penalty_code',
                              u'决定书文号': 'Administrative_Penalty:penalty_code',  # New in Beijing Website @20161228
                              u'违法行为类型': 'Administrative_Penalty:penalty_illegaltype',
                              u'行政处罚内容': 'Administrative_Penalty:penalty_decisioncontent',
                              u'作出行政处罚决定机关名称': 'Administrative_Penalty:penalty_decisioninsititution',
                              u'作出行政处罚决定日期': 'Administrative_Penalty:penalty_decisiondate',
                              u'决定机关名称': 'Administrative_Penalty:penalty_decisioninsititution',     # New in Beijing Website @20161228
                              u'处罚决定日期': 'Administrative_Penalty:penalty_decisiondate',              # New in Beijing Website @20161228
                              u'公示日期': 'Administrative_Penalty:penalty_announcedate',
                              u'详情': 'Administrative_Penalty:penalty_details'}

jingyingyichang_column_dict = {u'序号': 'Business_Abnormal:abnormal_no',
                               u'列入经营异常名录原因': 'Business_Abnormal:abnormal_events',
                               u'列入日期': 'Business_Abnormal:abnormal_datesin',
                               u'移出经营异常名录原因': 'Business_Abnormal:abnormal_moveoutreason',
                               u'移出日期': 'Business_Abnormal:abnormal_datesout',
                               u'作出决定机关': 'Business_Abnormal:abnormal_decisioninstitution',
                               u'作出决定机关(列入)': 'Business_Abnormal:abnormal_decisioninstitution_in',
                               u'作出决定机关(移出)': 'Business_Abnormal:abnormal_decisioninstitution_out'
                               }

yanzhongweifa_column_dict = {u'序号': 'Serious_Violations:serious_no',
                             u'列入严重违法企业名单原因': 'Serious_Violations:serious_events',
                             u'列入日期': 'Serious_Violations:serious_datesin',
                             u'移出严重违法企业名单原因': 'Serious_Violations:serious_moveoutreason',
                             u'移出日期': 'Serious_Violations:serious_datesout',
                             u'作出决定机关': 'Serious_Violations:serious_decisioninstitution'}

chouchajiancha_column_dict = {u'序号': 'Spot_Check:check_no',
                              u'检查实施机关': 'Spot_Check:check_institution',
                              u'类型': 'Spot_Check:check_type',
                              u'日期': 'Spot_Check:check_date',
                              u'结果': 'Spot_Check:check_result',
                              u'备注': 'Spot_Check:check_remark'}

# ------------年报用字段------------分割线------------分割线------------分割线------------

# 年报列表--table_id--39
qiyenianbao_column_dict = {u'公司名称': 'annual_report:enterprisename',
                           u'序号': 'annual_report:xh',
                           u'报送年度': 'annual_report:bsnd',
                           u'报送日期': 'annual_report:bsrq',
                           u'发布日期': 'annual_report:fbrq',
                           u'详情': 'annual_report:xq',
                           }

# 企业年报基本信息 -- 1 --table_id--40
qiyenianbaojiben_column_dict = {u'公司名称': 'report_base:enterprisename',
                                u'合作社名称': 'report_base:enterprisename',  # new in 1108 灵璧县高立彩种植专业合作社
                                u'企业名称': 'report_base:enterprisename',
                                u'名称': 'report_base:enterprisename',  # new in 1104 泾县月亮湾吊车租赁部
                                u'注册号': 'report_base:zch',  # new in 1104
                                u'营业执照注册号': 'report_base:zch',  # new in 20161215 @hebei e.g.爱玛客服务产业（中国）有限公司秦皇岛分公司
                                u'经营者姓名':'report_base:jyzxm',
                                u'注册号/统一社会信用代码':'report_base:zch',
                                u'统一社会信用代码/注册号':'report_base:zch',
                                u'企业联系电话': 'report_base:lxdh',
                                u'联系电话': 'report_base:lxdh',
                                u'邮政编码': 'report_base:yzbm',
                                u'资金数额': 'report_base:zjse',  # new in 1104 泾县月亮湾吊车租赁部
                                u'企业通信地址': 'report_base:txdz',
                                u'电子邮箱': 'report_base:dzyx',
                                u'有限责任公司本年度是否发生股东（发起人）股权转让': 'report_base:gqzr',
                                u'有限责任公司本年度是否发生股东股权转让': 'report_base:gqzr',
                                u'企业是否有投资信息或购买其他公司股权': 'report_base:qtgq',
                                u'是否有投资信息或购买其他公司股权':'report_base:qtgq',
                                u'企业经营状态': 'report_base:jyzt',
                                u'隶属关系' : 'report_base:lsgx',  # 1104 new in 江苏大自然环境建设集团有限公司马鞍山分公司
                                u'是否有网站或网店': 'report_base:sfwd',
                                u'从业人数': 'report_base:cyrs',
                                u'成员人数': 'report_base:cyrs',  # 1108 new in 阜阳市颍州区西清蛋鸡养殖专业合作社
                                }

# 企业网站或者网店 -- 2 --table_id--41
qiyenianbaowangzhan_column_dict = {u'公司名称': 'web_site:enterprisename',
                                   u'名称': 'web_site:mc',
                                   u'序号': 'web_site:lx',
                                   u'类型': 'web_site:lx',
                                   u'网址': 'web_site:wz',
                                   # u'报送日期': 'web_site:mc',
                                   # u'发布日期': 'web_site:wz',
                                   }

# 企业公示股东及出资信息 -- 3  --table_id--42
qiyenianbaogudong_column_dict = {u'公司名称': 'enterprise_shareholder:enterprisename',
                             u'股东': 'enterprise_shareholder:gd',
                             u'实缴出资方式': 'enterprise_shareholder:sjczfs',
                             u'实缴出资额': 'enterprise_shareholder:sjcze',
                             u'实缴出资额（万元）': 'enterprise_shareholder:sjcze',
                             u'实缴出资日期': 'enterprise_shareholder:sjczrq',
                             u'实缴出资时间': 'enterprise_shareholder:sjczrq',
                             u'认缴出资日期': 'enterprise_shareholder:rjczrq',
                             u'认缴出资时间': 'enterprise_shareholder:rjczrq',
                             u'认缴出资方式': 'enterprise_shareholder:rjczfs',
                             u'认缴出资额': 'enterprise_shareholder:rjcze',
                             u'认缴出资额（万元）': 'enterprise_shareholder:rjcze',
                             }

# 企业资产状况信息 -- 4 --table_id--43
qiyenianbaozichanzhuangkuang_column_dict = {u'公司名称': 'industry_status:enterprisename',
                                            u'资产总额': 'industry_status:zcze',
                                            u'所有者权益合计': 'industry_status:qyhj',
                                            u'营业总收入': 'industry_status:yyzsr',
                                            u'利润总额': 'industry_status:lrze',
                                            u'营业总收入中主营业务收入': 'industry_status:zyyw',
                                            u'主营业务收入': 'industry_status:zyyw',        # new in 人民网股份有限公司北京分公司 @20161130
                                            u'净利润': 'industry_status:jlr',
                                            u'纳税总额': 'industry_status:nsze',
                                            u'销售总额中主营业务收入': 'industry_status:xszezy',
                                            u'销售总额': 'industry_status:xsze',
                                            u'负债总额': 'industry_status:fzze',
                                            }

# 对外提供保证担保信息 -- 5 --table_id--44
qiyenianbaoduiwaidanbao_column_dict = {u'公司名称': 'guarantee:enterprisename',
                                       u'债权人': 'guarantee:zqr',
                                       u'债务人': 'guarantee:zwr',
                                       u'主债权种类': 'guarantee:zzqzl',
                                       u'主债权数额': 'guarantee:zzqse',
                                       u'履行债务的期限': 'guarantee:zwqx',
                                       u'保证的期间': 'guarantee:bzqj',
                                       u'保证的方式': 'guarantee:bzfs',
                                       u'保证担保的范围': 'guarantee:dbfw',
                                       }

# 股权变更信息 -- 6  --table_id--45
qiyenianbaoguquanbiangeng_column_dict = {u'公司名称': 'equity_transfer:enterprisename',
                                         u'股东': 'equity_transfer:gd',
                                         u'变更前股权比例': 'equity_transfer:bgq',
                                         u'变更后股权比例': 'equity_transfer:bgh',
                                         u'股权变更日期': 'equity_transfer:bgrq',
                                         }

# 修改记录信息 -- 7  --table_id--46
qiyenianbaoxiugaijilu_column_dict = {u'公司名称': 'modify:enterprisename',
                                     u'序号': 'modify:xh',
                                     u'修改事项': 'modify:xgsx',
                                     u'修改前': 'modify:xgq',
                                     u'修改后': 'modify:xgh',
                                     u'修改日期': 'modify:xgrq',
                                     }

# 对外投资信息 -- 8  --table_id--47
qiyenianbaoduiwaitouzi_column_dict = {u'公司名称': 'investment:enterprisename',
                                      u'投资设立企业或购买股权企业名称': 'investment:qymc',
                                      u'注册号': 'investment:zch',
                                      u'注册号/统一社会信用代码': 'investment:zch',
                                      }

# 年报信息更正声明信息 -- 9
qiyenianbaogengzhengshuoming_column_dict = {u'公司名称': 'annual_report_modify:enterprisename',
                                            u'序号': 'annual_report_modify:xh',
                                            u'更正事项': 'annual_report_modify:gzsx',
                                            u'更正理由': 'annual_report_modify:gzly',
                                            u'更正时间': 'annual_report_modify:gzsj',
                                            }

#  ***********************************************动产抵押详情信息表格****************************************

# 动产抵押登记信息  --tableID--63--dcdydj
dcdy_dengji_column_dict = {u'统一社会信用代码/注册号': 'dcdydj:registrationno',
                          u'登记编号': 'dcdydj:dcdy_djbh',
                          u'登记日期': 'dcdydj:dcdy_djrq',
                          u'登记机关': 'dcdydj:dcdy_djjg',
                          u'被担保债券种类': 'dcdydj:dcdy_bdbzqzl',
                          u'被担保债券数额': 'dcdydj:dcdy_bdbzqsl',
                          u'债务人履行债务的期限': 'dcdydj:dcdy_lxqx',
                          u'担保范围': 'dcdydj:dcdy_dbfw',
                          u'备注': 'dcdydj:dcdy_bz',
                           }

# 抵押权人概况  --tableID--55--dyqrgk, 序号和自增ID重复，程序主体pop掉
dcdy_diyaquanren_column_dict = {u'统一社会信用代码/注册号': 'dyqrgk:registrationno',
                               u'抵押权人名称': 'dyqrgk:dyqr_mc',
                               u'抵押权人证照/证件类型': 'dyqrgk:dyqr_zzlx',
                               u'证照/证件号码': 'dyqrgk:dyqr_zzhm',
                               u'序号': 'dyqrgk:xh',  # 废弃字段,程序使用时删除
                               }

# 被担保债权概况  --tableID--56--bdbzqgk
dcdy_beidanbaozhaiquan_column_dict = {u'种类': 'bdbzqgk:dbzq_zl',
                                      u'数额': 'bdbzqgk:dbzq_sl',
                                      u'担保的范围': 'bdbzqgk:dbzq_fw',
                                      u'债务人履行债务的期限': 'bdbzqgk:dbzq_qx',
                                      u'备注': 'bdbzqgk:dbzq_bz',
                                      }

# 抵押物概况  --tableID--57--dywgk        基本都有翻页，数目巨大
dcdy_diyawu_column_dict = {u'名称': 'dywgk:dyw_mc',
                           u'抵押物名称': 'dywgk:dyw_mc',
                           u'所有权归属': 'dywgk:dyw_gs',
                           u'数量、质量、状况等信息': 'dywgk:dyw_xq',
                           u'数量、质量、状况、所在地等情况': 'dywgk:dyw_xq',
                           u'备注': 'dywgk:dyw_bz',
                           u'序号': 'dywgk:dyw_xh',  # 废弃字段,程序使用时删除
                           }

# 变更  --tableID--58--dcdybg
dcdy_biangeng_column_dict = {u'变更日期': 'dcdybg:dcdy_bgrq',
                             u'变更内容': 'dcdybg:dcdy_bgnr',
                             u'序号': 'dcdybg:dcdy_xh',  # 废弃字段,程序使用时删除
                             }

# 注销  --tableID--59--dcdyzx
dcdy_zhuxiao_column_dict = {u'注销日期': 'dcdyzx:dcdy_zxrq',
                            u'注销原因': 'dcdyzx:dcdy_zxyy',
                            }

#  ---------------------------------------股权出质登记信息详情表格--------------------------------------------------

# 股权出质变更  --tableID--61--gqczbg
gqcz_biangeng_column_dict = {u'变更日期': 'gqczbg:gqcz_bgrq',
                             u'变更内容': 'gqczbg:gqcz_bgnr',
                             u'序号': 'gqczbg:gqcz_xh',  # 废弃字段,程序使用时删除
                             }

# 股权出质注销  --tableID--60--gqczzx
gqcz_zhuxiao_column_dict = {u'注销日期': 'gqczzx:gqcz_zxrq',
                             u'注销原因': 'gqczzx:gqcz_zxyy',
                             u'序号': 'gqczzx:gqcz_xh',  # 废弃字段,程序使用时删除
                             }





