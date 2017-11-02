# coding=utf-8

ying_ye_zhi_zhao_dict = {
    u'统一社会信用代码': 'tyshxy_code',
    u'注册号': 'zch',
    u'企业名称': 'enterprisename',
    u'类型': 'enterprisetype',
    u'法定代表人': 'legalrepresentative',
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
}

bian_geng_dict = {
    'altBe': 'changedannouncement_before',  # 变更前
    'altAf': 'changedannouncement_after',  # 变更后
    'altItem_CN': 'changedannouncement_events',  # 变更事项
    'altDate': 'changedannouncement_date',  # 变更日期
}

gu_dong_dict = {
    'bLicNo': 'shareholder_certificationno',  # 证照/证件号码
    'inv': 'shareholder_name',  # 股东名称
    'blicType_CN': 'shareholder_certificationtype',  # 证照/证件类型
    'invType_CN': 'shareholder_type',  # 股东类型
    'liSubConAm': 'subscripted_amount',  # 认缴出资额
    'liAcConAm': 'actualpaid_amount',  # 实缴出资额
    'sConForm_CN': 'subscripted_method',  # 认缴出资方式
    'respForm_CN': 'actualpaid_method',  # 实缴出资方式
}

gu_quan_chu_zhi_dict = {
    # "altDate": "",  # 变更日期
    # "canDate": '',
    # "cancelDate": '',
    # "cancelRea": "",
    # "equPleCanRea": "",
    "equPleDate": 'equitypledge_registrationdate',  # 股权出质设立登记日期
    "equityNo": 'equitypledge_registrationno',  # 登记编号
    "impAm": 'equitypledge_amount',  # 出质股权数额
    "impOrg": 'equitypledge_pawnee',  # 质权人
    "impOrgBLicNo": 'equitypledge_pawneeid',  # 质权人证件号码
    # "impOrgBLicType_CN": "",
    # "impOrgCerNo": "",
    # "impOrgCerType_CN": "",
    # "impOrgId": "ff808081529c41fb0152b0556c883de5",
    # "pledAmUnit": "",
    "pledBLicNo": "equitypledge_pledgorid",  # 出质人证件号码
    # "pledBLicType_CN": "",
    # "pledCerNo": "",
    # "pledCerType_CN": "",
    "pledgor": 'equitypledge_pledgor',  # 出质人
    "publicDate": 'equitypledge_announcedate',  # 公示日期
    # "regCapCur_CN": "",  # 出质股权币种单位
    "type": "equitypledge_status",  # 状态
    # "type_CN": "",
    # "vStakQualitInfoAlt": ''
}

dong_chan_di_ya_dict = {
    # "canDate": null,
    # "morCanRea_CN": "",
    "morRegCNo": "chattelmortgage_registrationno",  # 登记编号
    # "morReg_Id": "PROVINCENODENUM130000a0a0e3984ee39312014f6e223a051bc3",  # id
    "priClaSecAm": 'chattelmortgage_guaranteedamount',  # 被担保债权数额
    "publicDate": 'chattelmortgage_announcedate',  # 公示日期
    # "regCapCur_Cn": "人民币",  # 被担保数额币种
    "regOrg_CN": "chattelmortgage_registrationinstitution",  # 登记机关
    "regiDate": 'chattelmortgage_registrationdate',  # 登记日期
    "type": "chattelmortgage_status",  # 状态
    # "type_CN": ""，
}

jing_ying_yi_chang_dict = {
    "decOrg_CN": "abnormal_decisioninstitution_in",  # 作出决定机关(列入)
    "reDecOrg_CN": "abnormal_decisioninstitution_out",  # 作出决定机关(移出)
    "remExcpRes_CN": "abnormal_moveoutreason",  # 移出经营异常名录原因
    "speCause_CN": "abnormal_events",  # 列入经营异常名录原因
    "abntime": "abnormal_datesin",  # 列入日期
    "remDate": "abnormal_datesout",  # 移出日期
}

chou_cha_jian_cha_dict = {
    'insAuth_CN': 'check_institution',  # 检查实施机关
    'insRes_CN': 'check_result',  # 结果
    'insDate': 'check_date',  # 日期
    'insType': 'check_type',  # 类型
}

xing_zheng_chu_fa_dict = {
    "illegActType": "penalty_illegaltype",  # 违法行为类型
    "penAuth_CN": "penalty_decisioninsititution",  # 决定机关名称
    "penContent": "penalty_decisioncontent",  # 行政处罚内容
    "penDecIssDate": 'penalty_decisiondate',  # 处罚决定日期
    "penDecNo": "penalty_code",  # 决定书文号
    "publicDate": 'penalty_announcedate',  # 公示日期
}


key_person_role_dict = {
    'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAAOCAYAAACVZ7SQAAACqElEQVR42r2WUYSUURTHx1irh8RKkqzoIVlj7dsaayWykmRfMg9ZSezDyDysX'
    'pL00EvWWvMwljWStTIkSdaItVZW1rL2IUkiWaOHLMk+jQx1Tn43Z447830zDx1+Zu65937f/d97zrlfJtNui8IR0x4Qqpl0dkWYyPRnt4Qx0x7Dl9YuCDNpBx8IR017UGil'
    'mHdC+C4UaK90QTeuyOYFPgvrpr2Oz44pIrwa4a3wsUPfbBqRzQSBOn5HWDa+QheywqhwyVAXHpj2PeEl/y8LU8wZJWI8ZWGtQ9+/CFlFzG9+n4P1NU1fsOPCO+EV7VM9hNh'
    '9xL0RvkKDjd5k0Ws824fua9OvvGe+9dXThOsAIg45UeU6OxzsEaJ17G1hN6XAEXeSgccIiPWNmPmH7nn67orzNdPmZE74YdrTTuSQOcEDCk+JF3aiRJGI9WkufujQN+NEJp'
    '1kV5G6Y+Psqi5o24msuTlZwusZ7ZjIFmEXRIZcrjm2KTjenzPvyyN42lAhPK1Px5z0JfgJ6rVK3mUx2t5KEFkjbytdwlOfM+l8mgobJhUGyb0l56sTrsGKkU3ciETAFwpPW'
    'xF4SBjYcF0yQocjIheEPfKyH5ENV+43I1fBvhF5kfzzrCDU+vaoulNJOamhcxUBWuKvkZNZ7sY8i63+J5H5DtfSMlXa+nZIucluIlXQNwTZrxoNn/MsMFg/IvU9c/wGZlmw'
    '9WnanDPzypEPDL3GPjnfvg9XL3KIQSXXr+J+cpW86EFkK/LJN05UWHbJJe+3cyci18ti5Orxufx3l28IvwjDLUInZg1OuJQgUqvtU17WoogEO+0qYaAcqZKBYff8Y1TQAid'
    '5J+lyvskRz9GeN3egtxwCB4yvRNWzNo/wMrlk7QwL7IWzkatrlUK44GpJm/0B+H4BqS3ysBwAAAAASUVORK5CYII=': u'执行董事',
    'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB0AAAAOCAYAAADT0Rc6AAABdklEQVR42qWUMUgDQRBFDwsrsbGwEBEsLIJIOpEgIkgQK7tUV4iQIoiFnYi9h'
    'cgVQZBUYmEnInIIIQQLEUFSiIgIIiGlnVVKZ+EffL4TTnHhkezfnZ3d2b8XRX7bMIrUL0L7bVsy4rxJNaNBvBlN6jeh8ZwaNtJwuDVeBoxVs6RzxgqRGvvU3zUu8H/VKCMm'
    'sOaQGNcDxriC0R6S3RgfoGd8Gm0sErh0Sn1F44EnxLOWankLctKMAyzojRUo/kvW2zTqovU1aYxJSrjL5wFjsSTNO2nfM9OIcS7cw0Cqz1LcAjawTtRRTtbCnHFNOma0jGE'
    'i3N2xaCnKy87XKrScCr3DSD+S9sTebcf6XUq6jPtTTpGYtQ5cXf5v0lDaisMJXgFrDzDmot7pDn4zqliAtW1jhuISnIy5M15F63rlnccHgHnEXaheoriS85yOnKemXogmxG'
    'kZiePCjEnZ9CgcWsFJt/K+vVMI+AvTssaQcYYndYircNs3bFSWiVYudnIAAAAASUVORK5CYII=': u'董事',
    'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAAOCAYAAACVZ7SQAAACk0lEQVR42rWWQWRcURSGn4roYoSI6qKqVESMitlVRUSJqCxidhExiwgjYlR1U'
    '1XVRZUsqkY9pSIisggREREjjIgsIsLoIqqqVEXULGYXXTxPaM+p/9bpce6dN6WXz9x37rtzz3/vOee+KOq8dREznrFZoiCeC7BlbaNEKcN7eSLO4OdfbYW4CPBWvJsjEvQX'
    'iCXBF6IunuuwyXcWIHzJ4JD45BkrCx/GiJZHXC+xSmz8wwFGW0RRiRzCgo4a8Vw8P8U87j8gxjGHmTCoEruesUIGkXNEk9gkrlkiFvHCd0ETdp9Ibs8gbo/4Bs7hxAGcZra'
    'N0N0R48wp5ktbzfBViuxGdHDEfMaGeFuMndA7EwdE5tVJOhYhwBrLi/+/CKznWhIQ2UP8IBrEdJZwjJETOkdCIksY13AufvSMlZTIdieZtDnJm53kHC9eUXlQEU75wpWf1x'
    'XHCB9tvyPm3cN/FwUxwlPa+J3rmMMF5WeH/ImMq/gDH7mAyD5iH7nh4Nx7p2w1nEAkKrM+5X0jAr4aeaYLTwkbG2w5hI7Lm1T0GxASEnmuwvzAuArOhMj7yD/NKoRK2wdU3'
    'fGAyCtYr5xF5AhIRf/kP4jkUJ0yeI8qLW0nKGQjba6Qu/BrLCQyEblzKfpNCBnC3WPl5GP8OspwWNoeEgNiXtVIiyNcA9J2liFcB4kb2JQUqWCKbHnKdh0i5RdFonZwS9FA'
    'Lmn7sJg3bFwvb4yrp2acjhM5ivFUfCxMYIzDfNI6SVe2L0W/BZFPUAj2ICDC7hUNqkaVdOiS34PCMYWTrGS4CR6hcrJvL4yvmz74moqPmd/VdV1VQ8crbMI8sYz8crt2Cw5'
    '2wm3lEBeNNaz/Gmu1a/3ES/gdanz1dP0CG38SpdFXf2kAAAAASUVORK5CYII=': u'副董事长',
    'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFUAAAAOCAYAAABevFBuAAAEC0lEQVR42r2YcUScYRzHXzknk8hkMnNkJjkTk5NkYjL3RyaSzEkikzmTyJzM/'
    'hhnTjInkiRJZDKZjHPOzElMf0xm4uTkTCIzk/tjtN/L95nv/fY819myh4973+d5n+d9nu/z+/2e33ueZy+jQgfdd6Cu1nJXiNX47C1hWNU1CFMX9LspPLLUx9FmK03CjPef'
    'yoSwSBwIGbrPoI6fmYDQixbeC58dbeNCQAiCkHAitFHdsvCa7oPow6VZKKkN6RGOhWuOdT4T1nD9UCg76FbGYfD7jAjfHZT4ZbeFe8Q2dtTcPxU2cX1f6EMfn6iFOeGto82'
    '3+gQ2ylAU9nG9B2EyigTN14yVFF7QfUGYpXttpcfYRK+K6Hm69w0gDaEXsK4x1Jl5bOI6CGErSgJivhMOwRGsKAeRfN5YQsEWtft8Qn+u266ymDSFC56oq5wLG8K6gw08wy'
    'UlPMfifYEaVfsUvLHZ8r4ThCQPos5jnH7oEUR7hajtylINSQhma2un/nqHeDdNKav7ebiLz5lwiutT3JcIm6jBKqIHlagRCFYP48mq+L2M56cd42lRjcHsCl/JaCp0iEEET'
    'QZuaWuLKVEvstTyX1pq+RJEXcY4/jy/IQTUwb1LiPWdEGYfIa6aqDW7f4PFjXaww7o+TP26IMgDIo0Jcl2MDpA4JmPwY+FHXOexUNP2E7/TStRBNT4zqEStA1lkDGFYWB6H'
    'G5cBvN8PFa8g1Dl+DyGqOS9MDI4iFPwh6lW8lE/cUYofhm24P2cO2oqzFgsv0OFRj000LMBqGrCoLWor47f+H2NqQnlARM2BaQEuS/0irGCdRVyvukQ9UulPzpIaFUnUXrx'
    'EY17IdXs4PfvUyZqmkz8NKyhQm839o7A843Y7KsbXwVpN6YfFryFVW0ddyRHHX1Zx/wBtsA5VDZchqu/6QxYWkEVw3S4OPuNudzCpEQiXIpc6p9RoQ81zCRsSxQaYM+EAaZ'
    'OHMOOL00r55hI8L4q16jNlvUqMZlHjpIXJlFifNh1TJ5UbjEMgrovjK8iUOVgmkycXMRQtuWMLYmleHVQ5bMKYev4KLCqkRPUQA0PwhCnMvUBCsxV3kaXXKuowQmEPGUoS8'
    '2TjqfjwiKjDYxMLLljqu6lftyXdmrWkYjoW98C6eh2nfxMsIUvWPYk681zGIsA0Fu/B3WchYgpj/bDkzC5R/c35gNCRUx8gF+bU1x2n6JzlFDfcUGM0YnJDsLzHVXZ+BoK2'
    '1ZBSjSMsJTB2F835DF5gXG8JX02d5H0BHH5PEHKMAfHX2j6yAa6Lw1MGKIaOKu/jg8rwO0sJqW/cWmi1uNUqdjxlC9pUQnBlU5IQzIM1r1jGDjj+jNHxPFzDfx1NsP5qtFr'
    '6hR2f3kzkF9n7lseFpaXKAAAAAElFTkSuQmCC': u'董事长兼总经理',
    'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACsAAAAOCAYAAAC2POVFAAAB/0lEQVR42rWVQUSDYRjHJ5MOiUw6TCJJJtltMpmYyQ7pNh12SOwwSbol6dClQ'
    '7LDRHaaDpEkySdmpkMS0yFJIpkOHbqlw+xSz5v/x9Pj+fZ+O/Tys33P+z7f+7zP+3+eLxDQxyIRZc9R2PyOBJH1sS5CFC1rgtKQJ0qMZ6LCniuw8TV5HKCkcEU8eszl2L5J'
    '4sMjyH6iTBzLiUk4ujjEJnteJ07xf5ZIwceQVigQFx5zUR/BLhHvxAkxoJ1kA0FeEq/gDS+rYXPDmSKJczZvuIc/tznKnjzYbtyWucEnHMxTO0mFHQSizUWY/6eSGanFZpt'
    'g+4gvok4s2ISexcslRqsPHnNZEawts01LZoc6KOBAL3EkuMG1SPsE85tC4POMIq6d28yaQfiYwvnukD83FSKq0I6L0ea+sDnICO8kMutV5UZeFB3KAssiQdYRQkHxNlNTWl'
    'CDBTsDfUrKCJjb7tAlUm2C7cJ+uf8I1kggo3CArsJttyjYaUvrikHfSZtm1/DrksPG3LZCjDG/AjLJuUb74baGDxmME2EcrgWJqSOGxs+pQ2vSHmd+caWt7Sktz1Gy5Qabw'
    'HyLfTTSmDPymeNOYVG5LgWlql1kq+lDgWSQ2WUfdbKKSjdBbSlfqxCKswUJ/Y5hbNQJI+LFpjgO0dp2IRnbGCW2iR7LOtPygj81EMiFCWOxNQAAAABJRU5ErkJggg==': u'董事长',
    'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB0AAAAOCAYAAADT0Rc6AAABaUlEQVR42mNgwA7SgNgUiV8OxEoMxAN7II4lRmERENtC2cuBOBzKlgbiL0DMg'
    '0VPIhDPxoIPAvE1HHJpyAYsRLII2dIuIH4MFUPGWUCsB8ReWPAEIN6CQ86AkKXyQPwBiP2waNZD0rsJagkMXwLi+2hi27AFLzZLdwNxLdTyHUAsiyNqPqHxk4F4CprYD2Is'
    'rYS6jgkqVgDE74DYEYelhHyK1VKQywKwxCky8IHGLxeSmCU0pQYg4SlQByOLgdSIY7OYDYpBhmsh8ZExH5qeLKglyHgvEF9BE7sLTQsoAJQl/gPxayjGx4ZlH0do/KHjhVC'
    'LkcXOQVO1G7qln3BE/A+0+ONBCtpwLHgmNOEhi50E4g6ksoBsSxmgrl+Iho8C8Q00sYe4gpccS62B2AUN90HzLrLYNiiNUgSuAeJfSCXOHxzsX1C1RWiO5oOm0HCoT3MIlb'
    'vGOIosfNgYzQxQfl4MdVgPjrIaDAC5foW6ShoocQAAAABJRU5ErkJggg==': u'监事',
    'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACsAAAAOCAYAAAC2POVFAAACPUlEQVR42sWVX2SVYRzHHzNHcsSRJF2MyWR2l5kk3SXnYjKOYzKZMV0dk9jFJ'
    'F3EZCZJzMwcSczMLmZipovM7H4XGZkuJhlJki5ifX983vl59j7vToz9+DjP8573eZ7fn+/ze0M4alfEg5znDf7Ls4p4HE7BLog9Meie3RTfxMXEmifiLeN74k+CG7xzSww5b'
    'M198TPBXt6hVZgUz9z8s5h28zirFkhHQQIsmA03HxWvCGBGvBAjPMv8WGJcwuEjdiAWxLsEC7zjbUo8ZVM7+Fz0/yOxQ8Vi2xdlxubsa/bpF8uMy0XOlgoyVIqc7cORM2JCr'
    'Lv/7JB53h9P7Bc7uytWxJb4ynj1pJydp5S22Q+k0EaZTWezopcDt8WdY5z9bxnUxN0EtcjZNling/SQkQ0upbcBAjDJvMSBA353cXYFRzONV5HEiWl2wmUhk0Y5wSVIZfaTa'
    'BL8F8ZvUs5WyVSW/k3RHWWy5uYW9V/a1iIB9ZNB47v47ebPC2TQjvZjGQT3zqHNobUq5Qj0wB3aU6DP2qGdrl/aumHWnY/2HCKA0MIFa6Bx4z3SmHVczRadJQMdkbMBjdnz2'
    '7ShUfpuJTrYsn7dVaZVZwdpWabxOkzSEeqOww/SQ6LJSrCWs/E4mwbKPo1zU2jsF7e+lcxa0B+R0Ad0H8txKRVhnYPNLpPlpivBHF+pXqehdm74mLjmLteaY5vu4J81uEwDT'
    'qPDnNfMuWAZqV4duqIS1GlLx1mFchbRmbOux33KU/T9A1cGuQIA/VG9AAAAAElFTkSuQmCC': u'总经理',
    'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB0AAAAOCAYAAADT0Rc6AAABoUlEQVR42r2UT0REURTGr5G0eCJJWkWrFrNLxshom1m0mM1IRkak1WgRLUbSLm'
    'mRJDIyRtImaTFGJC3Sov0s0ma0GEkkSVrE9J18L2fuvDtv2nT5effdd+89/77zjGkefWDV/PNYA0ecz4JPBxPcMwkyCjkzB94c1E1AlE9gOMSpG/W+AHbpyD7YBvNck5EEp5'
    'x303DT2ALr/CgX9Frfl8E9GAhw5hl4nIvRPd4zDc4492yjMV7YA/LgUn2TzUXQACuODNhGa6AMbsEj5xXbaJEpksVXpjjC9EkdCmCcB6tgKsRoR+mNEIlwEUTpodQvYRlI0R'
    'EpxQ4vavBZo9EyDfoaSDLVLTXNK6/8lHsOhogr0jtQYhAPnB/aRsWLL7bLCTjmWp28gA/1vtkmvV3Uhp1eo/b89tsByHJjv3Vpho6YDoSUowaEc6a8oBgNukBqG+fzL0Zn2C'
    'qigTTZoILTikH/UJx9KjV4p0o7iVR695qluaIu9LDT26LIJTCmRHShqFLNei1H0aRUDbMUTSlASD6uXv/5JSZCGAk4F2V07Yh9A2Qgg+AVrBiLAAAAAElFTkSuQmCC': u'经理',
    'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAAOCAYAAACVZ7SQAAACg0lEQVR42rWXQWScQRTHR0SsWqGH6qFWyaGihypRqyKixB6qokJEVFWUVTlUDy'
    'GicqheqodaVbmsHKJiiYiIiBA5VA97yaGqclh66KGqQtUe6hNL+qZ+H5PJ++abrfbxY/b73nwz/5k3780ac9puCFWTbVV8NHsoXPKeTQvDJt4GhVHzn21KaATeN/DxrV84Fg'
    'a853XEx9qSsBrhV2e8dga/8Dll94UjHBLaGgk+R/RJ7bGwR/urUPxLkW+FN5EiQ36zmsheJvZAWKetsY5PkT6ptYQx2m1P5IIwIdSE9zmT38M/RuQWY2rUNJFuuDbZJY2mEq'
    '4z7LBxRD5iV74J34U14YnQCUy8h+/sR4r8LGxk8CFPZItQ0Gh5Is8jJCHB2LNwwrmySWfHCdeCtxi+jdL/p3AhIkFdCbwv4fNPEs8KghKST1EJ11Rk+i7Lanx/WZgP+N0lIp'
    'IcOhlJ8s/DThcdnwsXlXDVRF4jKZmM7Gz7VYSbREchIHJbKW1+6dkIiey2hPRFiNwUPrHzmr0QDp3fTRYwVuQquSEossqZ2404k7u0Z7sQeUcYF4bIzq6ViZCK8mw4UuSOsv'
    'hnRI4xmZR5hKe/54Snnk8lQuSSt8J20HfO78uEppYJXwk/WJiQyBIXgwPm1ZcXrvZsLJLhprwycUy4jkSE60AgLJdpD3FG952JGWWH2t7Fo8ep0WVKiV3MW0SZXZiXLOCZkE'
    'mvSrbgX1UGtAnmGbedj4SfJrLB+VrxWOP7ZRatw2oXAjmgl3p7wiXBjnWbjThgARaU8lJ3NuW6u1O1nNpjnHo3xy0mncim935SuUhMO98v5fwR8G2ccezZ/kKiuSecy6mVr+'
    '24vwGFkdkzltO0vAAAAABJRU5ErkJggg==': u'其他人员',
    'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADkAAAAOCAYAAACVZ7SQAAACxUlEQVR42r2WX2RbURzHr4iYiRE1NXsoNTNTM6aqpvYyM3moKRFVNVWqDxMzIw'
    '8104dSUzVTY6aiZkJN7KGmVE1NTdljH6bM7CFiwkzNTIXtd/hcvjnuvUkfusOHc07uPff3/f07CYLjj7QxEbF/wZiN2C/xW9TIGY+C/zQqxmECz+TZrPEn4oyzRt0Yl70R47'
    'vRG/Pdx8Zr5hOcG8V1nrlhTArunbsJdteP64iacSdGZB4WjQVZfzGWZe1H0TmgL+Gbzgm7sp4xVvj+C+OpMc1eaEeNeQahbcMZ2EB9SIP9TiL/GutGNYZ1ntGxZMxjjDP4jP'
    'f7Q+OADPFHEzsCRD7nnFHjLfNslMgVXtChXuokMpMQkYwncggBp4w5Y9srhwrPl2PO80V+NTaMPQLj5u/iRO4YL4WdExJZ4QxnxE9SNkU61vn2IIbuG7c7iOw6XV0h35P6yb'
    'Oe7FJkgd+jKHgiU7BNRx4gArs0Kx1jCJ+nAR5y1iERnCZyeanhPKnbJtKlzVoC2ROoyTnxepjC2RjOQVwkP2Onc9o35q98kWGR3oQjmX8yerrorilJk4/GZS9yBVk7L7e4Pt'
    '7giFFpeD+M37J+kpCuaYLkp2sgz7SJHIEjme91ELlKLeVJmzD1D7gmAu5JZ2y/3HfuvSne64konWpCjavIkvSQTVJY+8ol/4IP06sl8wZGXKGdq8jTeLzPExlQQ27/FtfBDP'
    'dmzjPYRXlYMqFbkeNcHS4QRVgkKEWhV0U25RCN1Jbn6Zz8/gDvhamyFWFQGWMC0nMZUUvU0C+6aDeRdM76QBDeU9d+2dTiPBNGZwNaMm8iskyr3iQiAZ4aZn6eqK5Jqqzyr2'
    'ZQvpOmY943rknT2RL2ySDdK9FkxqQGp7wGqY0npKzdtUrT8FnAuFmMdsZfjXHWRS9VilwPnUZOekAc/RHvDXhXXhRD/wB5SwMiRVOUpAAAAABJRU5ErkJggg==': u'副总经理',
    # '': u'',
    # '': u'',
    # '': u'',
    # '': u'',
    # '': u'',
}

ying_ye_zhi_zhao_table = {
    u'统一社会信用代码': 'xydm',
    u'注册号': 'zch',
    u'企业名称': 'mc',
    u'类型': 'qylx',
    u'法定代表人': 'frdb',
    u'注册资本': 'zczb',
    u'成立日期': 'clrq',
    u'营业期限自': 'jyqx_zi',
    u'营业期限至': 'jyqx_zhi',
    u'登记机关': 'djjg',
    u'核准日期': 'hzrq',
    u'登记状态': 'djzt',
    u'住所': 'dz',
    u'经营范围': 'jyfw',
    u'负责人': 'frdb',
    u'经营场所': 'dz',
    u'营业场所': 'dz',
    u'吊销日期': 'dxrq',
    u'投资人': 'frdb',
    u'主要经营场所': 'dz',
    u'合伙期限自': 'jyqx_zi',
    u'合伙期限至': 'jyqx_zhi',
    u'执行事务合伙人': 'frdb',
    u'组成形式': 'zcxs',
    u'经营者': 'frdb',
    u'首席代表': 'frdb',
    u'派出企业名称': 'pcqymc',
    u'成员出资总额': 'zczb',
    u'省份': 'sf',
    u'迁入地工商局': 'qrdgsj',
    u'业务范围': 'jyfw',
    u'名称': 'mc',
    u'注册日期': 'clrq',
    u'注册资金': 'zczb',
    u'经营期限自': 'jyqx_zi',
    u'经营期限至': 'jyqx_zhi',
}
