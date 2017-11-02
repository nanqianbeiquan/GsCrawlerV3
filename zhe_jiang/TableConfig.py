# coding=utf-8

jiben_column_dict = {u'统一社会信用代码/注册号': 'Registered_Info:registrationno',
            u'注册号/统一社会信用代码': 'Registered_Info:registrationno',             # modified by jing
            u'注册号': 'Registered_Info:registrationno',
            u'统一社会信用代码': 'Registered_Info:registrationno',                  # modified by jing
            u'名称': 'Registered_Info:enterprisename',
            u'企业名称': 'Registered_Info:enterprisename',                          # New in website 20170104
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
            # u'吊销日期': 'Registered_Info:dxrq',
            u'成员出资总额':'Registered_Info:totalcontributionofmembers',
            u'社会信用代码': 'Registered_Info:tyshxy_code',
            u'注册号码': 'Registered_Info:zch',
            u'多证合一': 'Registered_Info:dzhy',
            u'详情页url': 'Registered_Info:detailpageurl'}                               # modified by jing

gudong_column_dict = {u'股东类型':'Shareholder_Info:shareholder_type', 
                      u'股东（发起人）类型':'Shareholder_Info:shareholder_type',
                      u'发起人类型':'Shareholder_Info:shareholder_type',
                       u'股东':'Shareholder_Info:shareholder_name', 
                       u'发起人':'Shareholder_Info:shareholder_name', 
                       u'股东名称':'Shareholder_Info:shareholder_name', 
                       u'股东（发起人）':'Shareholder_Info:shareholder_name',
                      u'主管部门名称':'Shareholder_Info:shareholder_name',
                      u'主管部门类型':'Shareholder_Info:shareholder_type',
                       u'证照/证件类型':'Shareholder_Info:shareholder_certificationtype', 
                       u'证照/证件号码':'Shareholder_Info:shareholder_certificationno',
                      u'证照/证件编号':'Shareholder_Info:shareholder_certificationno',
                       u'详情':'Shareholder_Info:shareholder_details', 
                       u'认缴额（万元）':'Shareholder_Info:subscripted_capital',
                      u'认缴额（万）':'Shareholder_Info:subscripted_capital',
                       u'实缴额（万元）':'Shareholder_Info:actualpaid_capital',
                      u'实缴额（万）':'Shareholder_Info:actualpaid_capital',
                       u'认缴出资方式':'Shareholder_Info:subscripted_method', 
                       u'认缴出资额（万元）':'Shareholder_Info:subscripted_amount',
                      u'认缴出资额（万）':'Shareholder_Info:subscripted_amount',
                       u'认缴出资日期':'Shareholder_Info:subscripted_time', 
                       u'实缴出资方式':'Shareholder_Info:actualpaid_method',
                       u'实缴出资额（万元）':'Shareholder_Info:actualpaid_amount',
                      u'实缴出资额（万）':'Shareholder_Info:actualpaid_amount',
                      u'公示日期': 'Shareholder_Info:actualpaid_time',
                       u'实缴出资日期':'Shareholder_Info:actualpaid_time'}

touziren_column_dict ={u'投资人':'Investor_Info:investor_name', 
                       u'出资方式':'Investor_Info:investment_method'}

hehuoren_column_dict = {u'合伙人类型':'Partner_Info:partner_type',
                        u'合伙人信息':'Partner_Info:partner_name',
                        u'证照/证件类型':'Partner_Info:partner_certificationtype',
                        u'证照/证件号码':'Partner_Info:partner_certificationno',
                        u'注册号':'Partner_Info:registrationno'}

DICInfo_column_dict = {u'序号':'DIC_Info:dic_no',
                        u'出资人类型':'DIC_Info:dic_sponsortype', 
                        u'出资人':'DIC_Info:dic_sponsorname', 
                        u'证照/证件类型':'DIC_Info:dic_idtype', 
                        u'证照/证件号码':'DIC_Info:dic_idno',
                        u'注册号':'DIC_Info:registrationno'}

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

chengyuanmingce_column_dict = {u'序号':'Members_Info:members_no',
                               u'姓名':'Members_Info:members_name',
                               u'姓名（名称）':'Members_Info:members_name'}

fenzhijigou_column_dict = {u'序号': 'Branches:branch_no',
                           u'注册号/统一社会信用代码': 'Branches:branch_registrationno',
                           u'注册号': 'Branches:branch_registrationno',
                           u'名称': 'Branches:branch_registrationname',
                           u'登记机关': 'Branches:branch_registrationinstitution'}

qingsuan_column_dict = {u'清算组成员':'liquidation_member',
                            u'清算组负责人':'liquidation_pic'}

dongchandiyadengji_column_dict = {u'序号':'Chattel_Mortgage:chattelmortgage_no', 
                                  u'登记编号':'Chattel_Mortgage:chattelmortgage_registrationno', 
                                  u'登记日期':'Chattel_Mortgage:chattelmortgage_registrationdate',
                                  u'登记机关':'Chattel_Mortgage:chattelmortgage_registrationinstitution', 
                                  u'被担保债权数额':'Chattel_Mortgage:chattelmortgage_guaranteedamount', 
                                  u'状态':'Chattel_Mortgage:chattelmortgage_status',
                                  u'公示日期':'Chattel_Mortgage:chattelmortgage_announcedate', 
                                  u'详情':'Chattel_Mortgage:detail'}

guquanchuzhidengji_column_dict = {u'序号':'Equity_Pledge:equitypledge_no', 
                                  u'登记编号':'Equity_Pledge:equitypledge_registrationno', 
                                  u'出质人':'Equity_Pledge:equitypledge_pledgor', 
                                  # u'证照/证件号码1':'Equity_Pledge:equitypledge_pledgorid',
                                  u'证照/证件号码':'Equity_Pledge:equitypledge_pledgorid',   #tian
                                  u'出质股权数额':'Equity_Pledge:equitypledge_amount', 
                                  u'质权人':'Equity_Pledge:equitypledge_pawnee', 
                                  u'证照/证件号码1':'Equity_Pledge:equitypledge_pawneeid',
                                  # u'证照/证件号码':'Equity_Pledge:equitypledge_pawneeid',  #tian
                                  u'股权出质设立登记日期':'Equity_Pledge:equitypledge_registrationdate',
                                  u'状态':'Equity_Pledge:equitypledge_status', 
                                  u'公示日期':'Equity_Pledge:equitypledge_announcedate', 
                                  u'变化情况':'Equity_Pledge:equitypledge_change',
                                  u'详情':'Equity_Pledge:detail',}

xingzhengchufa_column_dict = {u'序号':'Administrative_Penalty:penalty_no', 
                              u'行政处罚决定书文号':'Administrative_Penalty:penalty_code',
                              u'决定书文号':'Administrative_Penalty:penalty_code',
                              u'违法行为类型':'Administrative_Penalty:penalty_illegaltype',
                              u'行政处罚内容':'Administrative_Penalty:penalty_decisioncontent',
                              u'作出行政处罚决定机关名称':'Administrative_Penalty:penalty_decisioninsititution',
                              u'决定机关名称':'Administrative_Penalty:penalty_decisioninsititution',
                              u'作出行政处罚决定日期':'Administrative_Penalty:penalty_decisiondate',
                              u'处罚决定日期':'Administrative_Penalty:penalty_decisiondate',
                              u'公示日期':'Administrative_Penalty:penalty_announcedate', 
                              u'详情':'Administrative_Penalty:detail'}

jingyingyichang_column_dict = {u'序号':'Business_Abnormal:abnormal_no', 
                               u'列入经营异常名录原因':'Business_Abnormal:abnormal_events',
                               u'纳入经营异常名录原因':'Business_Abnormal:abnormal_events',
                               u'标记经营异常状态原因':'Business_Abnormal:abnormal_events',
                               u'列入日期':'Business_Abnormal:abnormal_datesin',
                               u'标记日期':'Business_Abnormal:abnormal_datesin',
                               u'移出经营异常名录原因':'Business_Abnormal:abnormal_moveoutreason',
                               u'恢复正常记载状态原因':'Business_Abnormal:abnormal_moveoutreason',
                               u'移出日期':'Business_Abnormal:abnormal_datesout',
                               u'恢复日期':'Business_Abnormal:abnormal_datesout',
                               u'作出决定机关':'Business_Abnormal:abnormal_decisioninstitution',
                               u'作出决定机关(列入)':'Business_Abnormal:abnormal_decisioninstitution_in',
                               u'作出决定机关（列入）':'Business_Abnormal:abnormal_decisioninstitution_in',
                               u'作出决定机关(移出)':'Business_Abnormal:abnormal_decisioninstitution_out',
                               u'作出决定机关（移出）':'Business_Abnormal:abnormal_decisioninstitution_out',
                               u'作出决定机关（标记）':'Business_Abnormal:abnormal_decisioninstitution_in',
                               u'作出决定机关（恢复）':'Business_Abnormal:abnormal_decisioninstitution_out',
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
                      u'序号':'dyqrgk:dyqr_id',
                      u'抵押权人证照/证件类型':'dyqrgk:dyqr_zzlx',
                      u'证照/证件号码':'dyqrgk:dyqr_zzhm'}

dywgk_column_dict = {u'名称':'dywgk:dyw_mc',
                     u'序号':'dywgk:dyw_id',
                      u'所有权归属':'dywgk:dyw_gs',
                      u'数量、质量、状况、所在地等情况':'dywgk:dyw_xq',
                      u'备注':'dywgk:dyw_bz'}

dcdybg_column_dict = {u'变更日期':'dcdybg:dcdy_bgrq',
                      u'变更内容':'dcdybg:dcdy_bgnr'}

gqczzx_biangeng_dict = {u'序号':'gqczzx:gqcz_no',
                        u'变更日期':'gqczzx:gqcz_bgrq',
                      u'变更内容':'gqczzx:gqcz_bgnr'}

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
                               u'住所地': 'dyqrgk:dyqr_zsd',               # new in zhejiang website @20170110
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
                           u'所有权或使用权归属': 'dywgk:dyw_gs',
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
