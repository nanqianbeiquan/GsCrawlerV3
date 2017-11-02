# coding=utf-8

jiben_column_dict = {u'统一社会信用代码/注册号': 'Registered_Info:registrationno',
            u'注册号/统一社会信用代码': 'Registered_Info:registrationno',             # modified by jing
            u'注册号': 'Registered_Info:registrationno',
            u'统一社会信用代码': 'Registered_Info:registrationno',                  # modified by jing
            u'名称': 'Registered_Info:enterprisename',
            u'企业名称': 'Registered_Info:enterprisename',
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
            u'吊销日期': 'Registered_Info:revocationdate',
            u'吊销时间': 'Registered_Info:revocationdate',
            u'投资人': 'Registered_Info:investor',
            u'执行事务合伙人': 'Registered_Info:executivepartner',
            u'主要经营场所': 'Registered_Info:mianbusinessplace',
            u'合伙期限自': 'Registered_Info:partnershipfrom',
            u'合伙期限至': 'Registered_Info:partnershipto',
            u'注销日期': 'Registered_Info:candate',
            u'成员出资总额':'Registered_Info:totalcontributionofmembers',
            u'详情页url':'Registered_Info:detailpageurl'}                              # modified by jing

gudong_column_dict = {u'股东类型':'Shareholder_Info:shareholder_type', 
                      u'股东（发起人）类型':'Shareholder_Info:shareholder_type',
                      u'发起人类型':'Shareholder_Info:shareholder_type',
                       u'股东':'Shareholder_Info:shareholder_name', 
                       u'发起人名称':'Shareholder_Info:shareholder_name',
                       u'股东名称':'Shareholder_Info:shareholder_name', 
                       u'股东（发起人）':'Shareholder_Info:shareholder_name',
                       u'证照/证件类型':'Shareholder_Info:shareholder_certificationtype', 
                       u'证照/证件号码':'Shareholder_Info:shareholder_certificationno',
                       u'详情':'Shareholder_Info:shareholder_details',
                       u'认缴明细':'Shareholder_Info:rjmx',
                       u'实缴明细':'Shareholder_Info:sjmx',
                       u'认缴额（万元）':'Shareholder_Info:subscripted_capital',
                       u'实缴额（万元）':'Shareholder_Info:actualpaid_capital',
                       u'认缴出资方式':u'认缴出资方式',
                       u'认缴出资额（万元）':u'认缴出资额（万元）',
                       u'认缴出资日期':u'认缴出资日期',
                       u'实缴出资方式':u'实缴出资方式',
                       u'实缴出资额（万元）':u'实缴出资额（万元）',
                       u'实缴出资日期':u'实缴出资日期',
                        u'出资人类型':'Shareholder_Info:shareholder_type',
                        u'出资人':'Shareholder_Info:shareholder_name',
                        u'主管部门类型':'Shareholder_Info:shareholder_type',
                        u'主管部门名称':'Shareholder_Info:shareholder_name' }

touziren_column_dict ={u'投资人':'Shareholder_Info:shareholder_name',
                       u'姓名':'Shareholder_Info:shareholder_name',
                       u'出资方式':'Shareholder_Info:subscripted_method'}

hehuoren_column_dict = {u'合伙人类型':'Shareholder_Info:shareholder_type',
                        u'合伙人':'Shareholder_Info:shareholder_name',
                        u'合伙人信息':'Shareholder_Info:shareholder_name',
                        u'证照/证件类型':'Shareholder_Info:shareholder_certificationtype',
                        u'证照/证件号码':'Shareholder_Info:shareholder_certificationno',
                        u'国家（地区）':'Shareholder_Info:country',
                        u'住所':'Shareholder_Info:address',
                        u'承担责任方式':'Shareholder_Info:dutytype',
                        u'注册号':'Shareholder_Info:registrationno'}

# DICInfo_column_dict = {u'序号':'DIC_Info:dic_no',
#                         u'出资人类型':'DIC_Info:dic_sponsortype',
#                         u'出资人':'DIC_Info:dic_sponsorname',
#                         u'主管部门类型':'DIC_Info:dic_sponsortype',
#                         u'主管部门名称':'DIC_Info:dic_sponsorname',
#                         u'证照/证件类型':'DIC_Info:dic_idtype',
#                         u'证照/证件号码':'DIC_Info:dic_idno',
#                         u'注册号':'DIC_Info:registrationno'}


biangeng_column_dict = {u'变更事项':'Changed_Announcement:changedannouncement_events', 
                         u'变更前内容':'Changed_Announcement:changedannouncement_before', 
                         u'变更后内容':'Changed_Announcement:changedannouncement_after', 
                         u'变更日期':'Changed_Announcement:changedannouncement_date',
                         u'注册号':'Changed_Announcement:registrationno',
                         u'详细':'Changed_Announcement:changedannouncement_details'}

zhuyaorenyuan_column_dict={u'序号':'KeyPerson_Info:keyperson_no',
                           u'姓名':'KeyPerson_Info:keyperson_name',
                           u'职务':'KeyPerson_Info:keyperson_position'}

jiatingchengyuan_column_dict = {u'序号':'Family_Info:familymember_no',
                                u'姓名':'Family_Info:familymember_name',
                                u'职务':'Family_Info:familymember_position'}

chengyuanmingce_column_dict = {u'序号':'KeyPerson_Info:members_no',
                               u'姓名':'KeyPerson_Info:members_name',
                               u'姓名（名称）':'KeyPerson_Info:members_name'}

fenzhijigou_column_dict = {u'序号':'Branches:branch_no', 
                            u'注册号/统一社会信用代码':'Branches:branch_registrationno',
                            u'名称':'Branches:branch_registrationname',
                            u'登记机关':'Branches:branch_registrationinstitution'}
                            
qingsuanxinxi_column_dict ={u'清算负责人':'liquidation_Information:liquidation_pic',
                            u'清算组成员':'liquidation_Information:liquidation_member'
                            }

dongchandiyadengji_column_dict = {u'序号':'Chattel_Mortgage:chattelmortgage_no', 
                                  u'登记编号':'Chattel_Mortgage:chattelmortgage_registrationno', 
                                  u'登记日期':'Chattel_Mortgage:chattelmortgage_registrationdate',
                                  u'登记机关':'Chattel_Mortgage:chattelmortgage_registrationinstitution', 
                                  u'被担保债权数额':'Chattel_Mortgage:chattelmortgage_guaranteedamount', 
                                  u'状态':'Chattel_Mortgage:chattelmortgage_status',
                                  u'公示日期':'Chattel_Mortgage:chattelmortgage_announcedate', 
                                  u'详情':'Chattel_Mortgage:chattelmortgage_details'}

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

dyqrgk_column_dict = {u'抵权人名称':'dyqrgk:dyqr_mc',
                      u'抵押权人证照/证件类型':'dyqrgk:dyqr_zzlx',
                      u'证照/证件号码':'dyqrgk:dyqr_zzhm'}

dywgk_column_dict = {u'名称':'dywgk:dyw_mc',
                      u'所有权归属':'dywgk:dyw_gs',
                     u'所有权或使用权归属':'dywgk:dyw_gs',
                      u'数量、质量、状况、所在地等情况':'dywgk:dyw_xq',
                     u'数量、质量、所在地、状况等情况':'dywgk:dyw_xq',
                      u'备注':'dywgk:dyw_bz'}

gqczzx_biangeng_dict = {u'变更日期':'gqczzx:gqcz_bgrq',
                      u'变更内容':'gqczzx:gqcz_bgnr'}


guquanchuzhidengji_column_dict = {u'序号':'Equity_Pledge:equitypledge_no',
                                  u'登记编号':'Equity_Pledge:equitypledge_registrationno', 
                                  u'出质人':'Equity_Pledge:equitypledge_pledgor', 
                                  u'证照/证件号码1':'Equity_Pledge:equitypledge_pledgorid',
                                  u'出质股权数额':'Equity_Pledge:equitypledge_amount', 
                                  u'质权人':'Equity_Pledge:equitypledge_pawnee', 
                                  u'证照/证件号码1':'Equity_Pledge:equitypledge_pawneeid', 
                                  u'股权出质设立登记日期':'Equity_Pledge:equitypledge_registrationdate',
                                  u'状态':'Equity_Pledge:equitypledge_status', 
                                  u'公示日期':'Equity_Pledge:equitypledge_announcedate', 
                                  u'变化情况':'Equity_Pledge:equitypledge_change'}


sifaxiezu_column_dict = {u'序号':'Judicial_Aid:xuhao',
                          u'被执行人':'Judicial_Aid:beizhiren',
                          u'股权数额':'Judicial_Aid:guquanshue',
                          u'执行法院':'Judicial_Aid:zhixingfayuan',
                          u'执行通知书文号':'Judicial_Aid:zhixinwenhao',
                          u'状态':'Judicial_Aid:zhuangtai',
                          u'详情':'Judicial_Aid:detail'}

xingzhengchufa_column_dict = {u'序号':'Administrative_Penalty:penalty_no', 
                              u'行政处罚决定书文号':'Administrative_Penalty:penalty_code',
                              u'违法行为类型':'Administrative_Penalty:penalty_illegaltype', 
                              u'行政处罚内容':'Administrative_Penalty:penalty_decisioncontent',
                              u'作出行政处罚决定机关名称':'Administrative_Penalty:penalty_decisioninsititution', 
                              u'作出行政处罚决定日期':'Administrative_Penalty:penalty_decisiondate', 
                              u'公示日期':'Administrative_Penalty:penalty_announcedate', 
                              u'详情':'Administrative_Penalty:penalty_details'}

jingyingyichang_column_dict = {u'序号':'Business_Abnormal:abnormal_no', 
                               u'列入经营异常名录原因':'Business_Abnormal:abnormal_events',
                               u'标记经营异常状态原因':'Business_Abnormal:abnormal_events',
                               u'列入日期':'Business_Abnormal:abnormal_datesin',
                               u'标记日期':'Business_Abnormal:abnormal_datesin',
                               u'移出经营异常名录原因':'Business_Abnormal:abnormal_moveoutreason',
                               u'恢复正常记载状态原因':'Business_Abnormal:abnormal_moveoutreason',
                               u'移出日期':'Business_Abnormal:abnormal_datesout',
                               u'恢复日期':'Business_Abnormal:abnormal_datesout',
                               u'作出决定机关':'Business_Abnormal:abnormal_decisioninstitution',
                               u'作出决定机关(列入)':'Business_Abnormal:abnormal_decisioninstitution(in)',
                               u'作出决定机关(移出)':'Business_Abnormal:abnormal_decisioninstitution(out)'
                               }

yanzhongweifa_column_dict = {u'序号':'Serious_Violations:serious_no', 
                             u'列入严重违法企业名单原因':'Serious_Violations:serious_events', 
                             u'列入日期':'Serious_Violations:serious_datesin', 
                             u'移出严重违法企业名单原因':'Serious_Violations:serious_moveoutreason',
                             u'移出日期':'Serious_Violations:serious_datesout', 
                             u'作出决定机关':'Serious_Violations:serious_decisioninstitution'}

chouchajiancha_column_dict = {u'序号':'Spot_Check:check_no', 
                              u'检查实施机关':'Spot_Check:check_institution', 
                              u'类型':'Spot_Check:check_type',
                              u'日期':'Spot_Check:check_date', 
                              u'结果':'Spot_Check:check_result', 
                              u'备注':'Spot_Check:check_remark'}
