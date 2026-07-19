/* 閱讀練習題庫（Claude 依 TOEIC 真題題型編寫）
   RP5：Part 5 單句填空（tags[0] 為考點大分類，與英文填空的診斷分類一致）
   RP6：Part 6 短文填空（每篇 4 題，text 內 ___(n)___ 對應 qs[n-1]，各含一題句子插入）
   RP7：Part 7 閱讀測驗（單篇/雙篇/三篇，含主旨、細節、NOT、推論、同義詞、跨篇整合題型）
   ans 為 opts 的索引；前端顯示時會打亂選項順序，所以 ans 位置分布不影響作答 */

const RP5 = [
  // ---------- 假設語氣（18 題） ----------
  {id:"p5-001", tags:["假設語氣","與過去事實相反"], q:"If the shipment ___ on time, we would not have missed the product launch.", opts:["arrived","had arrived","arrives","would arrive"], ans:1, exp:"主要子句 would not have missed 表示與過去事實相反，if 子句要用過去完成式 had arrived。"},
  {id:"p5-002", tags:["假設語氣","倒裝 Had"], q:"Had Ms. Chen known about the schedule change, she ___ her flight earlier.", opts:["would have rebooked","rebooked","would rebook","has rebooked"], ans:0, exp:"Had Ms. Chen known ＝ If Ms. Chen had known 的倒裝，與過去事實相反，主句用 would have + p.p.。"},
  {id:"p5-003", tags:["假設語氣","與現在事實相反"], q:"If I ___ you, I would accept the transfer to the Singapore office.", opts:["was","were","am","be"], ans:1, exp:"與現在事實相反的假設，be 動詞一律用 were（If I were you 是固定用法）。"},
  {id:"p5-004", tags:["假設語氣","假設現在式"], q:"The director insisted that the report ___ submitted by Friday.", opts:["is","be","was","has been"], ans:1, exp:"insist、suggest、recommend 等要求動詞接 that 子句時，動詞用原形（假設現在式），故選 be。"},
  {id:"p5-005", tags:["假設語氣","與過去事實相反"], q:"We would have signed the contract if the terms ___ more favorable.", opts:["were","had been","would be","are"], ans:1, exp:"主句 would have signed 是對過去的假設，if 子句用過去完成式 had been。"},
  {id:"p5-006", tags:["假設語氣","倒裝 Were"], q:"___ it not for the loyal customers, the store would have closed years ago.", opts:["Were","Should","Had","If"], ans:0, exp:"Were it not for ～＝要不是有～（If it were not for 的倒裝）。Had it not been for 也可，但這裡空格後是 not for，搭配 Were。"},
  {id:"p5-007", tags:["假設語氣","were to 未來假設"], q:"If the company ___ to relocate, employees would receive a relocation allowance.", opts:["were","is","has","will be"], ans:0, exp:"were to + 原形動詞表示對未來的假設（可能性低），主句搭配 would。"},
  {id:"p5-008", tags:["假設語氣","as if"], q:"Mr. Alvarez talks about the budget as if he ___ the chief financial officer.", opts:["is","were","be","has been"], ans:1, exp:"as if 引導與現在事實相反的比喻（他其實不是財務長），be 動詞用 were。"},
  {id:"p5-009", tags:["假設語氣","倒裝 Should"], q:"Should you ___ any questions about your benefits, please contact Human Resources.", opts:["have","has","had","having"], ans:0, exp:"Should you have ～＝ If you should have ～ 的倒裝，Should 後面接原形動詞。"},
  {id:"p5-010", tags:["假設語氣","without 假設"], q:"Without the government subsidy, the factory ___ to remain open last year.", opts:["would not have been able","will not be able","is not able","had not been able"], ans:0, exp:"Without ～ 相當於 if 子句；last year 指過去，主句用 would not have been able。"},
  {id:"p5-011", tags:["假設語氣","if only"], q:"If only the marketing team ___ more time to prepare for the launch.", opts:["has","had","have","will have"], ans:1, exp:"If only（要是～就好了）表達與現在事實相反的願望，用過去式 had。"},
  {id:"p5-012", tags:["假設語氣","假設現在式"], q:"The consultant recommended that the firm ___ its outdated inventory system.", opts:["replace","replaces","replaced","replacing"], ans:0, exp:"recommend that + S + 原形動詞（假設現在式）。主詞 the firm 後直接用 replace。"},
  {id:"p5-013", tags:["假設語氣","直說法條件句"], q:"Unless the invoice ___ by the end of the month, a late fee will apply.", opts:["is paid","were paid","paid","pays"], ans:0, exp:"主句用 will，是有可能發生的直說法條件句，不是假設語氣；unless 子句用現在式，invoice 是被付的，用被動 is paid。"},
  {id:"p5-014", tags:["假設語氣","直說法條件句"], q:"Provided that all documents ___ in order, the loan will be approved within five business days.", opts:["are","were","be","being"], ans:0, exp:"provided that（只要）引導真實條件句，主句用 will，條件句用現在式 are，不必用假設語氣。"},
  {id:"p5-015", tags:["假設語氣","倒裝 Had"], q:"Had it not been for your quick response, we ___ the client's account.", opts:["would have lost","would lose","lost","had lost"], ans:0, exp:"Had it not been for ～（要不是～）是對過去的假設，主句用 would have + p.p.。"},
  {id:"p5-016", tags:["假設語氣","假設現在式"], q:"It is essential that every visitor ___ a security badge at all times while in the facility.", opts:["wear","wears","wore","wearing"], ans:0, exp:"It is essential/important/necessary that 子句用原形動詞（假設現在式），故選 wear。"},
  {id:"p5-017", tags:["假設語氣","wish"], q:"I wish our department ___ a larger budget for training this year.", opts:["has","had","will have","have"], ans:1, exp:"wish 接與現在事實相反的願望，子句用過去式 had。"},
  {id:"p5-018", tags:["假設語氣","混合時態"], q:"If the engineers had tested the prototype more carefully, the recall ___ necessary now.", opts:["would not be","would not have been","is not","was not"], ans:0, exp:"混合假設：if 子句是過去（had tested），主句講現在的結果（now），用 would not be。"},
  // ---------- 詞性（8 題） ----------
  {id:"p5-019", tags:["詞性","名詞"], q:"The ___ of the new branch has been postponed until further notice.", opts:["open","opening","opened","openly"], ans:1, exp:"The ___ of 結構需要名詞，opening（開幕）。"},
  {id:"p5-020", tags:["詞性","副詞"], q:"Ms. Patel responded ___ to all customer inquiries during the system outage.", opts:["prompt","promptness","promptly","prompted"], ans:2, exp:"修飾動詞 responded 要用副詞 promptly（迅速地）。"},
  {id:"p5-021", tags:["詞性","形容詞"], q:"The seminar provided ___ advice on retirement planning.", opts:["practice","practical","practically","practicality"], ans:1, exp:"修飾名詞 advice 要用形容詞 practical（實用的）。"},
  {id:"p5-022", tags:["詞性","名詞"], q:"Employees must obtain ___ from their supervisor before working overtime.", opts:["approve","approval","approved","approvingly"], ans:1, exp:"obtain 的受詞需要名詞 approval（核准）。"},
  {id:"p5-023", tags:["詞性","形容詞"], q:"The updated manual is considerably more ___ than the previous edition.", opts:["informative","information","inform","informatively"], ans:0, exp:"be 動詞後接形容詞作補語，more informative（更詳盡）。"},
  {id:"p5-024", tags:["詞性","名詞"], q:"All ___ for the design award must be submitted electronically by May 1.", opts:["apply","applicants","applications","applicable"], ans:2, exp:"能「被提交」的是 applications（申請文件）；applicants 是人，不能 be submitted。"},
  {id:"p5-025", tags:["詞性","形容詞"], q:"The CFO gave a ___ summary of the quarterly results before taking questions.", opts:["brief","briefly","briefing","brevity"], ans:0, exp:"a ___ summary 需要形容詞 brief（簡短的）修飾名詞。"},
  {id:"p5-026", tags:["詞性","副詞"], q:"___, the hotel is within walking distance of the convention center.", opts:["Convenient","Conveniently","Convenience","More convenient"], ans:1, exp:"修飾整句用副詞 Conveniently（方便的是）。"},
  // ---------- 時態（4 題） ----------
  {id:"p5-027", tags:["時態","未來完成式"], q:"By the time the auditors arrive next Monday, the finance team ___ all the receipts.", opts:["will have organized","organized","has organized","is organizing"], ans:0, exp:"By the time + 未來時間點，表示屆時已完成，用未來完成式 will have organized。"},
  {id:"p5-028", tags:["時態","現在完成式"], q:"Since its founding in 2015, the startup ___ into three overseas markets.", opts:["expanded","has expanded","expands","will expand"], ans:1, exp:"Since + 過去時間點，表示從那時持續到現在，用現在完成式 has expanded。"},
  {id:"p5-029", tags:["時態","過去進行式"], q:"When the fire alarm sounded, the technicians ___ the server room.", opts:["were inspecting","have inspected","inspect","will inspect"], ans:0, exp:"過去某一時刻正在進行的動作，用過去進行式 were inspecting。"},
  {id:"p5-030", tags:["時態","現在簡單式"], q:"The maintenance crew ___ the elevators on the first Monday of every month.", opts:["inspects","inspected","has inspected","will have inspected"], ans:0, exp:"every month 表示例行公事，用現在簡單式；主詞 crew 是單數，動詞加 s。"},
  // ---------- 介系詞（4 題） ----------
  {id:"p5-031", tags:["介系詞","期間"], q:"The warranty remains valid ___ two years from the date of purchase.", opts:["for","since","until","by"], ans:0, exp:"for + 一段時間（two years）表示持續期間。"},
  {id:"p5-032", tags:["介系詞","方向"], q:"All complaints should be directed ___ the customer service department.", opts:["to","at","for","with"], ans:0, exp:"direct A to B 固定搭配，把～轉給～。"},
  {id:"p5-033", tags:["介系詞","慣用語"], q:"___ the exception of Friday, the clinic is open daily from 9 A.M. to 6 P.M.", opts:["With","By","In","On"], ans:0, exp:"with the exception of ～＝除了～之外，固定慣用語。"},
  {id:"p5-034", tags:["介系詞","起點"], q:"The two companies have been in negotiations ___ the end of last year.", opts:["since","for","from","during"], ans:0, exp:"現在完成式搭配 since + 過去時間點（去年年底以來）。"},
  // ---------- 連接詞（4 題） ----------
  {id:"p5-035", tags:["連接詞","讓步"], q:"___ the budget was tight, the event exceeded everyone's expectations.", opts:["Although","Despite","Because of","However"], ans:0, exp:"空格後是完整子句，要用連接詞 Although；Despite/Because of 是介系詞，However 不能直接連接兩子句。"},
  {id:"p5-036", tags:["連接詞","時間"], q:"Please remain seated ___ the seatbelt sign is turned off.", opts:["until","during","despite","among"], ans:0, exp:"接完整子句且語意是「直到～為止」，用連接詞 until；during 是介系詞只能接名詞。"},
  {id:"p5-037", tags:["連接詞","因果"], q:"The product launch was delayed ___ a shortage of components.", opts:["because of","because","although","so that"], ans:0, exp:"空格後 a shortage 是名詞片語，要用介系詞片語 because of；because 是連接詞須接子句。"},
  {id:"p5-038", tags:["連接詞","相關連接詞"], q:"Neither the manager ___ her assistants were aware of the policy change.", opts:["nor","or","and","but"], ans:0, exp:"neither A nor B 相關連接詞固定搭配。"},
  // ---------- 字彙（5 題） ----------
  {id:"p5-039", tags:["字彙","動詞辨析"], q:"The committee will ___ all the proposals and announce its decision next week.", opts:["review","glance","stare","gaze"], ans:0, exp:"review（審閱）proposals 是常見搭配；glance/stare/gaze 都是不及物的「看」，不能直接接受詞。"},
  {id:"p5-040", tags:["字彙","動詞辨析"], q:"Please ___ your seat assignment before boarding the shuttle bus.", opts:["verify","testify","qualify","notify"], ans:0, exp:"verify（確認）座位；testify 作證、qualify 使合格、notify 通知（後面接人）。"},
  {id:"p5-041", tags:["字彙","名詞辨析"], q:"The hotel offers a complimentary shuttle ___ to and from the airport.", opts:["service","advice","research","equipment"], ans:0, exp:"shuttle service（接駁服務）固定搭配。"},
  {id:"p5-042", tags:["字彙","副詞辨析"], q:"Sales figures for March were ___ higher than analysts had expected.", opts:["significantly","approximately","accidentally","previously"], ans:0, exp:"significantly higher（明顯更高）；approximately 接數字、accidentally 意外地、previously 先前。"},
  {id:"p5-043", tags:["字彙","動詞辨析"], q:"The training session has been ___ until next Thursday due to low enrollment.", opts:["postponed","expired","attained","prevented"], ans:0, exp:"postpone until ～＝延期到～；expire 到期（不及物）、attain 達成、prevent 防止。"},
  // ---------- 片語動詞（2 題） ----------
  {id:"p5-044", tags:["片語動詞","look 系列"], q:"The IT department will ___ the software issue as soon as possible.", opts:["look into","look up to","look after","look out"], ans:0, exp:"look into＝調查；look up to 尊敬、look after 照顧、look out 小心。"},
  {id:"p5-045", tags:["片語動詞","fill 系列"], q:"Please ___ the registration form and return it to the front desk.", opts:["fill out","fill up","fill in for","fill with"], ans:0, exp:"fill out a form＝填寫表格；fill up 裝滿、fill in for 代班、fill with 使充滿。"},
  // ---------- 代名詞（2 題） ----------
  {id:"p5-046", tags:["代名詞","所有格"], q:"Employees who park in the garage must display ___ permits on the dashboard.", opts:["their","they","them","theirs"], ans:0, exp:"修飾名詞 permits 用所有格 their。"},
  {id:"p5-047", tags:["代名詞","指示代名詞"], q:"The design proposed by our team was more innovative than ___ of the competing firm.", opts:["that","this","those","it"], ans:0, exp:"代替前面的單數名詞 the design，比較句中用 that of ～。"},
  // ---------- 語態（1 題） ----------
  {id:"p5-048", tags:["語態","被動式"], q:"The quarterly report ___ to all shareholders last Friday.", opts:["was distributed","distributed","has distributed","distributing"], ans:0, exp:"report 是被分發的對象，用被動式；last Friday 是過去時間，用 was distributed。"}
];

const RP6 = [
  {id:"p6-1", src:"E-mail｜價格調整通知", text:"To: All Valued Customers\nFrom: Meridian Office Supplies\nSubject: Price Adjustment\n\nDear Customer,\n\nThank you for your continued ___(1)___ of Meridian Office Supplies. Owing to rising material costs, we will adjust the prices of selected paper products, ___(2)___ January 15. Most increases will not exceed four percent. ___(3)___ You can also lock in current prices by placing bulk orders before that date. We appreciate your understanding and look forward to ___(4)___ you for many years to come.\n\nSincerely,\nCustomer Relations Team", qs:[
    {opts:["support","supporter","supportive","supportively"], ans:0, exp:"your continued ___ 需要名詞；依語意選 support（支持、惠顧），supporter 是「支持者」不合語意。"},
    {opts:["effective","effect","effects","effectively"], ans:0, exp:"effective + 日期＝自某日起生效，商業書信固定用法。"},
    {opts:["A full list of affected items is attached to this message.","The warehouse will be closed for renovation.","We regret that your order has been canceled.","Our store hours will change next month."], ans:0, exp:"句子插入題：前句講部分商品調價，接「受影響品項清單見附件」最連貫；其他選項與漲價主題無關。"},
    {opts:["serving","serve","served","service"], ans:0, exp:"look forward to 的 to 是介系詞，後面接動名詞 serving。"}
  ]},
  {id:"p6-2", src:"Memo｜辦公室搬遷", text:"To: All Staff\nFrom: Facilities Department\nRe: Office Relocation\n\nBeginning Monday, May 2, the accounting department will be ___(1)___ on the fifth floor. Packing crates will be delivered to each desk this Friday. ___(2)___ your belongings by the end of the day on April 29. Items left behind ___(3)___ to the new office the following week. ___(4)___\n\nThank you for your cooperation.", qs:[
    {opts:["located","locating","location","locate"], ans:0, exp:"be located on ～＝位於～，被動分詞作補語。"},
    {opts:["Please pack","Packing","To pack","Packed"], ans:0, exp:"這句是請員工打包的指示，用祈使句 Please pack。"},
    {opts:["will be transferred","transferred","have transferred","are transferring"], ans:0, exp:"Items 是被搬運的對象且是未來的事，用未來被動式 will be transferred。"},
    {opts:["If you need additional crates, contact Facilities at extension 4501.","The fifth floor was renovated in 2019.","Accounting reports are due at the end of the month.","We hope you enjoyed the company picnic."], ans:0, exp:"句子插入題：全文在講打包搬遷，補充「需要更多紙箱請聯絡總務」最切題。"}
  ]},
  {id:"p6-3", src:"Notice｜會員續約通知", text:"Riverside Fitness Center — Membership Renewal Notice\n\nYour annual membership is due to expire on August 31. Renew before August 15 and receive a ten percent ___(1)___ on the standard rate. ___(2)___, early renewers will be entered into a drawing for a free personal training session. Renewals can be completed online or ___(3)___ person at the front desk. ___(4)___ We look forward to helping you reach your fitness goals for another year.", qs:[
    {opts:["discount","discounted","discounting","discountable"], ans:0, exp:"a ten percent ___ 需要名詞 discount（折扣）。"},
    {opts:["In addition","However","Otherwise","For instance"], ans:0, exp:"前句是九折優惠、後句是再加抽獎，兩個好處並列，用 In addition（此外）。"},
    {opts:["in","at","by","on"], ans:0, exp:"in person＝親自，固定片語。"},
    {opts:["Please note that rates will increase for memberships renewed after the deadline.","The swimming pool will be closed all summer.","Our new branch opened last month in Dover.","Thank you for submitting your job application."], ans:0, exp:"句子插入題：呼應前文的 8/15 期限，提醒逾期續約費率調漲最連貫。"}
  ]},
  {id:"p6-4", src:"Letter｜錄取通知", text:"Dear Mr. Okafor,\n\nWe are pleased to ___(1)___ you the position of logistics coordinator at Hartwell Distribution. Your starting salary will be $52,000, ___(2)___ a comprehensive benefits package. ___(3)___ Please sign and return the enclosed agreement by June 10 to confirm your ___(4)___. We look forward to welcoming you to the team.\n\nSincerely,\nAmelia Hartwell\nDirector of Personnel", qs:[
    {opts:["offer","apply","accept","request"], ans:0, exp:"offer you the position＝提供你這個職位；accept 是求職者的動作，apply/request 語意不合。"},
    {opts:["along with","as well","in order to","whereas"], ans:0, exp:"along with + 名詞＝連同～；as well 放句尾、in order to 接動詞、whereas 接子句。"},
    {opts:["A detailed description of these benefits is enclosed.","Unfortunately, the position has been filled.","Your interview is scheduled for next Tuesday.","The warehouse is located near the airport."], ans:0, exp:"句子插入題：前句剛提到 benefits package，接「福利明細如附件」最連貫；(B)(C) 與錄取通知矛盾。"},
    {opts:["acceptance","accepted","accepting","acceptable"], ans:0, exp:"confirm your ___ 需要名詞 acceptance（接受、就任意願）。"}
  ]},
  {id:"p6-5", src:"公告｜圖書館二手書義賣", text:"Grandview Public Library — Community Notice\n\nThe library will host its annual used-book sale from October 3 ___(1)___ October 5 in the main lobby. Proceeds ___(2)___ new computers for the children's reading room. Volunteers are still needed to help sort donations. ___(3)___ interested in volunteering should e-mail Ms. Reyes at the library by September 20. ___(4)___", qs:[
    {opts:["through","among","between","within"], ans:0, exp:"from A through B＝從 A 到 B（含 B 當天）；between 要搭配 and。"},
    {opts:["will fund","funded","funding","to fund"], ans:0, exp:"義賣是未來的事，收益「將資助」新電腦，用未來式 will fund。"},
    {opts:["Those","Whoever","They","Them"], ans:0, exp:"Those interested in ～＝有意～的人（Those who are interested 的省略）。"},
    {opts:["Donations may be dropped off at the circulation desk during regular hours.","The library cafeteria menu changes weekly.","Computer classes were canceled last spring.","Ms. Reyes retired from the library in June."], ans:0, exp:"句子插入題：全文講二手書義賣與捐書分類，補充「捐書可於開館時間送至流通櫃台」最切題；(D) 與前句請大家聯絡 Ms. Reyes 矛盾。"}
  ]}
];

const RP7 = [
  {id:"p7-1", src:"單篇｜文字訊息鏈", passages:[
    {type:"文字訊息鏈", text:"Maya Lindqvist [10:12 A.M.]\nAre you at the trade show yet? I can't find our booth.\n\nDaniel Cho [10:13 A.M.]\nYes, we're in Hall B, booth 214. The organizers moved us this morning because of a lighting problem.\n\nMaya Lindqvist [10:14 A.M.]\nGood to know. I'm walking over now, and I have the extra brochures with me.\n\nDaniel Cho [10:15 A.M.]\nPerfect timing. We handed out the last ones ten minutes ago."}
  ], qs:[
    {q:"Where most likely are the writers?", opts:["At a convention center","At a printing shop","At an electronics store","At a company cafeteria"], ans:0, exp:"trade show、booth、Hall B 都指向會展中心。"},
    {q:"At 10:15 A.M., what does Mr. Cho most likely mean when he writes, \"Perfect timing\"?", opts:["The brochures are needed right away.","The trade show has just opened.","Ms. Lindqvist arrived earlier than expected.","The lighting problem was fixed quickly."], ans:0, exp:"意圖題：前一句說剛把最後的傳單發完，Maya 正好帶著備品過來，所以「來得正是時候」指的是傳單正缺。"}
  ]},
  {id:"p7-2", src:"單篇｜廣告", passages:[
    {type:"廣告", text:"GreenLeaf Catering\n\nFamily-owned since 2001, GreenLeaf Catering specializes in office luncheons and corporate events of all sizes. Choose from more than 30 menu options, including vegetarian and gluten-free dishes prepared fresh each morning.\n\nBook at least two weeks in advance and receive free delivery anywhere in the city of Brampton. First-time customers: mention code LUNCH10 when ordering to receive 10% off.\n\nVisit www.greenleafcatering.ca to view the complete menu."}
  ], qs:[
    {q:"What is indicated about GreenLeaf Catering?", opts:["It is a family-run business.","It opened last year.","It has several branch locations.","It serves only vegetarian food."], ans:0, exp:"開頭 Family-owned since 2001 直接對應「家族經營」；2001 年創立、素食只是選項之一。"},
    {q:"How can customers receive free delivery?", opts:["By booking at least two weeks ahead","By ordering through the Web site","By spending a minimum amount","By mentioning a promotional code"], ans:0, exp:"細節題：Book at least two weeks in advance and receive free delivery。代碼 LUNCH10 對應的是 9 折不是免運。"},
    {q:"Who is eligible to use code LUNCH10?", opts:["Customers placing their first order","Customers in Brampton only","Corporate event planners","Vegetarian menu subscribers"], ans:0, exp:"First-time customers: mention code LUNCH10＝首購客戶專屬。"}
  ]},
  {id:"p7-3", src:"單篇｜E-mail", passages:[
    {type:"E-mail", text:"From: Human Resources <hr@brightline-ins.com>\nTo: All Employees\nSubject: Employee Wellness Program\nDate: February 2\n\nStarting March 1, Brightline Insurance will launch a six-month employee wellness program. Participants may attend free yoga classes on Tuesday evenings, receive discounted memberships at Core Gym, and join monthly nutrition workshops led by a registered dietitian.\n\nEmployees who complete at least 20 program activities by August 31 will earn one extra vacation day. To register, log in to the HR portal and click \"Wellness\" by February 20. Space in the yoga classes is limited to 25 people per session, so early registration is encouraged."}
  ], qs:[
    {q:"What is the purpose of the e-mail?", opts:["To announce a new program for staff","To advertise a gym to the public","To explain a change in vacation policy","To introduce a new dietitian"], ans:0, exp:"主旨題：全文在宣布 3/1 開跑的員工健康計畫。"},
    {q:"What is NOT mentioned as part of the program?", opts:["Free medical checkups","Yoga classes","Gym membership discounts","Nutrition workshops"], ans:0, exp:"NOT 題：瑜伽、健身房折扣、營養工作坊都有提到，唯獨沒有免費健檢。"},
    {q:"What will employees who complete 20 activities receive?", opts:["An additional day off","A gym membership","A cash bonus","A dinner voucher"], ans:0, exp:"細節題：will earn one extra vacation day＝多一天假。"},
    {q:"The word \"Space\" in paragraph 2, line 3, is closest in meaning to", opts:["room","distance","scenery","emptiness"], ans:0, exp:"同義詞題：Space is limited＝名額（容納空間）有限，最接近 room（容量）的意思。"}
  ]},
  {id:"p7-4", src:"雙篇｜E-mail ×2", passages:[
    {type:"E-mail 1", text:"From: Priya Raman, Fairmont Conference Center\nTo: Jordan Blake, Innovex Ltd.\nSubject: RE: October workshop\nDate: September 28\n\nDear Mr. Blake,\n\nThank you for reserving Meeting Room C for Friday, October 14, from 9 A.M. to 4 P.M. As requested, we will set up 30 chairs, one projector, and two whiteboards.\n\nCatering can be added for $18 per person; please confirm by October 7 if you would like this service. Note that Meeting Room C does not have built-in videoconferencing equipment. If any of your presenters need to join remotely, I recommend upgrading to Meeting Room A for an additional $75.\n\nBest regards,\nPriya Raman"},
    {type:"E-mail 2", text:"From: Jordan Blake, Innovex Ltd.\nTo: Priya Raman, Fairmont Conference Center\nSubject: RE: RE: October workshop\nDate: September 29\n\nDear Ms. Raman,\n\nThank you for the details. Two of our presenters will connect from our Denver office, so please switch our reservation to the room you suggested. We will not need catering—our staff will bring their own lunches.\n\nCould you also add a second projector? I will send you the final attendee list on Monday.\n\nJordan Blake"}
  ], qs:[
    {q:"What is the main purpose of the first e-mail?", opts:["To confirm details of a room reservation","To advertise a new conference center","To cancel a catering order","To request payment for a workshop"], ans:0, exp:"主旨題：第一封信在確認 10/14 的訂位細節並補充加購資訊。"},
    {q:"What is indicated about Meeting Room C?", opts:["It lacks videoconferencing equipment.","It holds up to 100 people.","It costs an additional $75.","It is unavailable on October 14."], ans:0, exp:"細節題：does not have built-in videoconferencing equipment。$75 是升級 A 房的價差。"},
    {q:"Which room will Innovex most likely use?", opts:["Meeting Room A","Meeting Room C","The Denver office","The main hall"], ans:0, exp:"跨篇整合題：第二封說 switch to the room you suggested，而第一封建議的是 Meeting Room A。"},
    {q:"What does Mr. Blake decline?", opts:["The catering service","The extra projector","The room upgrade","The attendee list"], ans:0, exp:"細節題：We will not need catering＝婉拒餐飲服務。"},
    {q:"What does Mr. Blake ask Ms. Raman to do?", opts:["Provide an additional projector","Reserve a larger parking area","Send a price list","Contact the Denver office"], ans:0, exp:"細節題：Could you also add a second projector?"}
  ]},
  {id:"p7-5", src:"三篇｜廣告＋E-mail＋評論", passages:[
    {type:"廣告", text:"Summit Business Institute — Evening Courses, Fall Term\n\nProject Management — Mondays\nBusiness Writing — Tuesdays\nData Analysis — Wednesdays\nPublic Speaking — Thursdays\n\nAll courses run September 5 to November 18, 6:30–8:30 P.M.\nTuition: $420 per course. Register by August 15 and save $50.\nMembers of the Riverdale Chamber of Commerce receive an additional 10% off."},
    {type:"E-mail", text:"From: Tomas Vega\nTo: registration@summitbi.edu\nSubject: Fall enrollment\nDate: August 12\n\nTo whom it may concern,\n\nI would like to enroll in your Thursday course this fall. My employer, Vega & Associates, joined the Riverdale Chamber of Commerce in June, so please apply any discounts I qualify for.\n\nAlso, could you tell me whether class sessions are recorded? I travel for work one week each month and want to be sure I can catch up on anything I miss.\n\nThank you,\nTomas Vega"},
    {type:"線上評論", text:"★★★★★ — posted November 20 by T.V.\n\nAs someone who used to dread giving presentations, I found this course transformative. The instructor, Dana Whitfield, gives every student individual feedback after each speech. I missed a few sessions because of business trips, but catching up was easy—every class is recorded and posted the next day. Well worth the tuition."}
  ], qs:[
    {q:"According to the advertisement, how can students save $50?", opts:["By registering before August 15","By enrolling in two courses","By paying tuition in cash","By writing an online review"], ans:0, exp:"細節題：Register by August 15 and save $50。"},
    {q:"Which course did Mr. Vega most likely enroll in?", opts:["Public Speaking","Project Management","Business Writing","Data Analysis"], ans:0, exp:"跨篇整合題：他要報 Thursday 的課，廣告表列週四是 Public Speaking。"},
    {q:"What discounts is Mr. Vega most likely eligible for?", opts:["Both the early registration and the chamber discounts","The early registration discount only","The chamber discount only","No discounts"], ans:0, exp:"跨篇整合題：8/12 報名早於 8/15 期限，雇主六月加入商會，兩項折扣都符合。"},
    {q:"In the review, the word \"transformative\" is closest in meaning to", opts:["life-changing","temporary","confusing","optional"], ans:0, exp:"同義詞題：transformative＝帶來徹底改變的，最接近 life-changing。"},
    {q:"What is suggested about Mr. Vega's concern in his e-mail?", opts:["It was resolved because classes are recorded.","It caused him to withdraw from the course.","It was never answered by the school.","It led the school to change its schedule."], ans:0, exp:"跨篇整合題：他擔心出差缺課，評論（署名 T.V.）說每堂課都有錄影隔天上架、補課容易，可見疑慮已解決。"}
  ]}
];
