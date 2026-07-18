#!/usr/bin/env python3
"""TOEIC 核心搭配詞 → 單字卡（vocab/words/搭配詞.md ＋ vocab/books/搭配詞.md）。

清單是人工編的 TOEIC 高頻商用搭配詞。例句優先從 27 回模擬考逐字稿
（data/transcripts.js，句句有中文翻譯）撈真實句子——比自編例句更貼近考試語境；
逐字稿沒出現的才用清單裡的後備例句。

產出後跑 tools/import_vocab.py 就會進 data/words.js 並自動建「搭配詞」單字本，
翻卡／測驗／間隔複習全部沿用單字卡既有機制。

用法：
  python3 tools/extract_colloc.py --scan   # 只看每個搭配詞在逐字稿的命中數
  python3 tools/extract_colloc.py          # 產出 vocab/words+books 的 md
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'

# (片語, 詞性, 中文, 級距1-4, 例句用的regex（None=直接用片語）, 後備例句, 後備例句中文)
# regex 只需涵蓋常見變形（時態、單複數），大小寫不計
C = [
    # --- 動詞搭配 ---
    ('make a reservation', 'phr.', '預訂（餐廳、飯店）', 2, r'\bma(?:ke|kes|king|de) (?:a |the )?reservations?\b',
     'I would like to make a reservation for four people.', '我想預訂四個人的位子。'),
    ('place an order', 'phr.', '下訂單', 2, r'\bplac(?:e|es|ing|ed) (?:an? |the |your )?orders?\b',
     'You can place an order through our website.', '你可以透過我們的網站下訂單。'),
    ('meet the deadline', 'phr.', '趕上期限', 2, r'\bm(?:eet|eets|eeting|et) (?:the |a |our )?deadlines?\b',
     'We worked overtime to meet the deadline.', '我們加班趕上了期限。'),
    ('meet the requirements', 'phr.', '符合要求', 3, r'\bm(?:eet|eets|eeting|et) (?:the |all )?requirements?\b',
     'Applicants must meet the requirements listed below.', '應徵者必須符合下列要求。'),
    ('attend a meeting', 'phr.', '出席會議', 1, r'\battend(?:s|ing|ed)? (?:a |the |our )?(?:meeting|conference|seminar)s?\b',
     'She will attend a meeting with the clients.', '她將出席與客戶的會議。'),
    ('give a presentation', 'phr.', '做簡報', 2, r'\bg(?:ive|ives|iving|ave) (?:a |the )?presentations?\b',
     'He gave a presentation on the new product line.', '他就新產品線做了簡報。'),
    ('run late', 'phr.', '遲到；進度落後', 2, r'\brunning (?:a (?:bit|little) )?late\b',
     'The meeting is running late.', '會議進行得比預定時間晚。'),
    ('fill out a form', 'phr.', '填寫表格', 1, r'\bfill(?:s|ing|ed)? (?:out|in) (?:a |the |this )?(?:form|application|survey)s?\b',
     'Please fill out this form first.', '請先填寫這份表格。'),
    ('submit a report', 'phr.', '提交報告', 2, r'\bsubmit(?:s|ting|ted)? (?:a |the |your |it )?(?:report|proposal|application|resume)s?\b',
     'Please submit your report by Friday.', '請在週五前提交報告。'),
    ('sign a contract', 'phr.', '簽合約', 2, r'\bsign(?:s|ing|ed)? (?:a |the )?(?:contract|lease|agreement)s?\b',
     'Both parties signed the contract yesterday.', '雙方昨天簽了合約。'),
    ('take over', 'phr. v.', '接手；接任', 3, r'\btak(?:e|es|ing|en)\s?over\b|\btook over\b',
     'Who will take over Ms. Lee\'s position?', '誰會接任 Lee 女士的職位？'),
    ('fill in for', 'phr. v.', '代班；代理', 3, r'\bfill(?:s|ing|ed)? in for\b',
     'Could you fill in for me on Friday?', '週五可以幫我代班嗎？'),
    ('drop by / stop by', 'phr. v.', '順道拜訪', 2, r'\b(?:drop|stop)(?:s|ping|ped)? by\b',
     'An inspector will stop by our café on Sunday.', '一位稽查員週日會順道來我們咖啡店。'),
    ('drop off', 'phr. v.', '放下、交件；送（人／物）', 2, r'\bdrop(?:s|ping|ped)? (?:\w+ )?off\b',
     'When was this package dropped off at our store?', '這個包裹是什麼時候送到我們店裡的？'),
    ('pick up', 'phr. v.', '取（貨）；接（人）', 1, r'\bpick(?:s|ing|ed)? (?:\w+ )?up\b',
     'Would you book a taxi to pick up our clients?', '你可以訂計程車去接我們的客戶嗎？'),
    ('set up', 'phr. v.', '架設；安排', 2, r'\bset(?:s|ting)? (?:\w+ )?up\b',
     'Who set up the meeting room?', '會議室是誰佈置的？'),
    ('turn in', 'phr. v.', '繳交', 2, r'\bturn(?:s|ing|ed)? (?:\w+ )?in\b',
     'I turned it in to the financial manager.', '我把它交給財務經理了。'),
    ('look over', 'phr. v.', '檢視；過目', 2, r'\blook(?:s|ing|ed)? over\b|\blook(?:s|ing|ed)? (?:it|them) over\b',
     'Sure, I\'ll look over the report.', '好，我會過目這份報告。'),
    ('go over', 'phr. v.', '仔細檢查；討論', 2, r'\bgo(?:es|ing)? over\b|\bwent over\b',
     'When should we go over the marketing materials?', '我們什麼時候要一起看行銷資料？'),
    ('come up with', 'phr. v.', '想出（點子）', 3, r'\bc(?:ome|omes|oming|ame) up with\b',
     'Who came up with our company\'s new slogan?', '我們公司的新標語是誰想出來的？'),
    ('carry out', 'phr. v.', '執行；進行', 3, r'\bcarr(?:y|ies|ying|ied) out\b',
     'The survey will be carried out next month.', '調查將於下個月進行。'),
    ('put off', 'phr. v.', '延期', 3, r'\bput(?:s|ting)? (?:\w+ )?off\b',
     'The launch has been put off until May.', '上市已延到五月。'),
    ('call off', 'phr. v.', '取消', 3, r'\bcall(?:s|ing|ed)? (?:\w+ )?off\b',
     'The outdoor event was called off due to rain.', '戶外活動因雨取消了。'),
    ('run out of', 'phr. v.', '用完；耗盡', 2, r'\br(?:un|uns|unning|an) out of\b',
     'Our printer is out of ink.', '我們的印表機沒墨水了。'),
    ('take place', 'phr.', '舉行；發生', 2, r'\btak(?:e|es|ing)|took place\b' and r'\btak(?:e|es|ing) place\b|\btook place\b',
     'Where will the product demonstration take place?', '產品展示會在哪裡舉行？'),
    ('take effect / go into effect', 'phr.', '生效', 3, r'\b(?:take|takes|took|go(?:es)?|went) into effect\b|\btak(?:e|es|ing) effect\b',
     'Will the leave policy go into effect this month?', '休假政策這個月會生效嗎？'),
    ('take advantage of', 'phr.', '善用；利用', 3, r'\btak(?:e|es|ing) advantage of\b|\btook advantage of\b',
     'I will take advantage of that free offer.', '我會好好利用那個免費優惠。'),
    ('take care of', 'phr.', '處理；照顧', 2, r'\btak(?:e|es|ing) care of\b|\btook care of\b',
     'I can take care of that for you.', '我可以幫你處理那件事。'),
    ('keep track of', 'phr.', '追蹤記錄', 3, r'\bkeep(?:s|ing)? track of\b|\bkept track of\b',
     'This app helps you keep track of expenses.', '這個應用程式幫你追蹤開銷。'),
    ('be in charge of', 'phr.', '負責', 2, r'\bin charge of\b',
     'Who is in charge of the budget report?', '預算報告是誰負責的？'),
    ('be responsible for', 'phr.', '對…負責', 2, r'\bresponsible for\b',
     'The finance department is responsible for processing reports.', '財務部負責處理報告。'),
    ('be eligible for', 'phr.', '有資格獲得', 3, r'\beligible (?:for|to)\b',
     'Full-time staff are eligible for the bonus.', '全職員工有資格領取獎金。'),
    ('be entitled to', 'phr.', '有權享有', 4, r'\bentitled to\b',
     'Members are entitled to a 10% discount.', '會員有權享有九折優惠。'),
    ('be subject to', 'phr.', '需經…；可能受到', 4, r'\bsubject to\b',
     'Prices are subject to change without notice.', '價格如有變動，恕不另行通知。'),
    ('be aware of', 'phr.', '知道；意識到', 3, r'\baware of\b',
     'Neither of them was aware of the schedule change.', '他們兩人都不知道時程變動。'),
    ('be familiar with', 'phr.', '熟悉', 2, r'\bfamiliar with\b',
     'You may be familiar with the show.', '你可能對這個節目很熟。'),
    ('look forward to', 'phr.', '期待', 2, r'\blook(?:s|ing|ed)? forward to\b',
     'We look forward to seeing you at the conference.', '我們期待在會議上見到你。'),
    ('due to', 'prep.', '由於', 2, r'\bdue to\b',
     'The flight was delayed due to the weather.', '航班因天候延誤。'),
    ('prior to', 'prep.', '在…之前', 4, r'\bprior to\b',
     'Please arrive 15 minutes prior to the interview.', '請在面試前 15 分鐘抵達。'),
    ('in advance', 'adv.', '事先；提前', 2, r'\bin advance\b',
     'Register them in advance, please.', '請事先為他們登記。'),
    ('on schedule / behind schedule', 'phr.', '如期／進度落後', 3, r'\b(?:on|behind|ahead of) schedule\b',
     'The construction is behind schedule.', '工程進度落後。'),
    ('ahead of schedule', 'phr.', '提前完成', 3, r'\bahead of schedule\b',
     'Could we finish the analysis a day ahead of schedule?', '我們能提前一天完成分析嗎？'),
    ('out of stock', 'phr.', '缺貨', 2, r'\bout of stock\b',
     'That item is currently out of stock.', '那項商品目前缺貨。'),
    ('out of order', 'phr.', '（機器）故障', 2, r'\bout of order\b',
     'Isn\'t this vending machine out of order?', '這台販賣機不是壞了嗎？'),
    ('out of town', 'phr.', '出遠門；不在本地', 2, r'\bout of town\b',
     'Ms. Kim is out of town this week.', 'Kim 女士這週出遠門。'),
    ('free of charge', 'phr.', '免費', 3, r'\bfree of charge\b|\bat no (?:cost|charge)\b',
     'Delivery is free of charge for members.', '會員享免費配送。'),
    ('in person', 'adv.', '親自；當面', 2, r'\bin person\b',
     'Will the project be discussed in person or online?', '這個專案要當面討論還是線上討論？'),
    ('on short notice', 'phr.', '臨時通知；倉促', 4, r'\bon (?:such )?short notice\b',
     'Thanks for meeting me on short notice.', '謝謝你臨時抽空與我見面。'),
    ('until further notice', 'phr.', '直到另行通知', 4, r'\buntil further notice\b',
     'The branch is closed until further notice.', '該分店暫停營業，直到另行通知。'),
    ('no later than', 'phr.', '不晚於', 3, r'\bno later than\b',
     'Submit the form no later than June 1.', '請於 6 月 1 日前繳交表格。'),
    ('at the latest', 'phr.', '最遲', 3, r'\bat the latest\b',
     'By Friday at the latest.', '最遲週五。'),
    ('as soon as possible', 'phr.', '盡快', 1, r'\bas soon as possible\b|\basap\b',
     'Please reply as soon as possible.', '請盡快回覆。'),
    ('in a row', 'phr.', '連續', 3, r'\bin a row\b',
     'Sales have grown three years in a row.', '銷售額連續三年成長。'),
    ('on a regular basis', 'phr.', '定期', 3, r'\bon a (?:regular|daily|weekly|monthly) basis\b',
     'Staff meetings are held on a regular basis.', '員工會議定期舉行。'),
    ('first come, first served', 'phr.', '先到先得', 3, r'\bfirst come,? first served\b',
     'Spots are assigned first come, first served.', '名額先到先得。'),
    ('in accordance with', 'phr.', '依照', 4, r'\bin accordance with\b',
     'Refunds are made in accordance with our policy.', '退款依照我們的政策辦理。'),
    ('with regard to / regarding', 'prep.', '關於', 3, r'\b(?:with regard to|regarding)\b',
     'Any questions regarding the policy?', '關於這項政策有任何問題嗎？'),
    ('on behalf of', 'phr.', '代表', 4, r'\bon behalf of\b',
     'I am writing on behalf of the sales team.', '我代表業務團隊寫這封信。'),
    ('as of', 'prep.', '自…起；截至', 4, r'\bas of\b',
     'As of today, all workshops still have seats.', '截至今天，所有工作坊都還有名額。'),
    ('effective + 日期', 'phr.', '自（日期）起生效', 4, r'\beffective (?:immediately|from|on|next|this|january|february|march|april|may|june|july|august|september|october|november|december)\b',
     'The new rates are effective immediately.', '新費率即刻生效。'),
    # --- 名詞搭配 ---
    ('expense report', 'n.', '費用報告；報帳單', 2, None,
     'May I see the expense report now?', '我現在可以看費用報告嗎？'),
    ('travel expenses', 'n.', '差旅費', 2, r'\btravel(?:ling)? expenses?\b',
     'Will the company cover our travel expenses?', '公司會支付我們的差旅費嗎？'),
    ('job opening / job fair', 'n.', '職缺／就業博覽會', 2, r'\bjob (?:opening|fair|application|interview)s?\b',
     'Are there any openings on your marketing team?', '你們行銷團隊有職缺嗎？'),
    ('board of directors', 'n.', '董事會', 3, r'\bboard of directors\b|\bboard meeting\b',
     'The proposal was approved by the board of directors.', '提案獲董事會核准。'),
    ('press conference', 'n.', '記者會', 3, None,
     'The president is holding a press conference this afternoon.', '總裁今天下午舉行記者會。'),
    ('press release', 'n.', '新聞稿', 3, r'\bpress (?:release|statement)s?\b',
     'The press statement will be released to the media.', '新聞稿將發布給媒體。'),
    ('keynote speech', 'n.', '主題演講', 3, r'\bkeynote (?:speech|speaker|address)e?s?\b',
     'The keynote speech was inspiring.', '主題演講很激勵人心。'),
    ('sales figures', 'n.', '銷售數字', 3, r'\bsales (?:figures|report|revenue)s?\b',
     'Could you double check the sales figures?', '你可以再核對一次銷售數字嗎？'),
    ('quarterly report', 'n.', '季報', 3, r'\bquarterly (?:report|earnings|meeting)s?\b',
     'We\'d like you to write the next quarterly report.', '我們想請你寫下一份季報。'),
    ('annual report', 'n.', '年報', 2, r'\bannual (?:report|meeting|review|bonus|membership)s?\b',
     'The sales figures are in the annual report.', '銷售數字在年報裡。'),
    ('performance review', 'n.', '績效考核', 3, r'\bperformance (?:review|evaluation)s?\b',
     'Performance reviews are held every June.', '績效考核每年六月舉行。'),
    ('customer satisfaction', 'n.', '顧客滿意度', 3, r'\bcustomer (?:satisfaction|survey|feedback|complaint)s?\b',
     'The survey measures customer satisfaction.', '這份問卷評量顧客滿意度。'),
    ('warranty', 'n.', '保固', 2, r'\bwarrant(?:y|ies)\b',
     'Your computer is still under warranty, isn\'t it?', '你的電腦還在保固期內，對吧？'),
    ('refund', 'n./v.', '退款', 2, r'\brefund(?:s|ed|able)?\b',
     'Faulty merchandise can be returned for a refund.', '瑕疵商品可退貨退款。'),
    ('receipt', 'n.', '收據', 1, r'\breceipts?\b',
     'Do I need a receipt to return goods?', '退貨需要收據嗎？'),
    ('reimbursement', 'n.', '報銷；核銷', 4, r'\breimburse(?:ment|d)?s?\b',
     'How do I request reimbursement for travel expenses?', '差旅費要如何申請報銷？'),
    ('itinerary', 'n.', '行程表', 3, r'\bitinerar(?:y|ies)\b',
     'Let me check her itinerary.', '讓我查一下她的行程表。'),
    ('agenda', 'n.', '議程', 2, r'\bagendas?\b',
     'An updated agenda will be sent out.', '更新後的議程將會寄出。'),
    ('minutes (of a meeting)', 'n.', '會議紀錄', 4, r'\b(?:meeting|the) minutes\b|\bminutes of the\b',
     'Who will take the minutes of the meeting?', '誰負責做會議紀錄？'),
    ('inventory', 'n.', '庫存', 3, r'\binventor(?:y|ies)\b',
     'We need to count our inventory.', '我們需要盤點庫存。'),
    ('merchandise', 'n.', '商品', 3, r'\bmerchandise\b',
     'Where does your firm produce its merchandise?', '你們公司在哪裡生產商品？'),
    ('shipment', 'n.', '出貨；一批貨', 2, r'\bshipments?\b',
     'The shipment had already arrived.', '那批貨已經到了。'),
    ('invoice', 'n.', '發票；請款單', 3, r'\binvoices?\b',
     'Aren\'t we supposed to get an invoice from the landscaper?', '我們不是應該收到園藝公司的請款單嗎？'),
    ('estimate / quote', 'n.', '報價（單）', 3, r'\b(?:price )?estimates?\b|\bquotes?\b|\bquotations?\b',
     'Don\'t you want to see the price estimate?', '你不想看報價單嗎？'),
    ('lease', 'n./v.', '租約；出租', 3, r'\bleas(?:e|es|ing|ed)\b',
     'My apartment lease will expire next month.', '我的公寓租約下個月到期。'),
    ('renovation', 'n.', '整修', 3, r'\brenovat(?:e|es|ing|ed|ion|ions)\b',
     'The meeting will be held in Room B until the renovation is complete.', '整修完成前會議都在 B 室舉行。'),
    ('maintenance', 'n.', '維修保養', 2, r'\bmaintenance\b',
     'The subway line is closed for maintenance work.', '地鐵線因維修停駛。'),
    ('appliance', 'n.', '家電', 3, r'\bappliances?\b',
     'The store sells kitchen appliances.', '這家店賣廚房家電。'),
    ('beverage', 'n.', '飲料', 2, r'\bbeverages?\b',
     'Would you be interested in a beverage?', '想來杯飲料嗎？'),
    ('complimentary', 'adj.', '贈送的；免費的', 4, r'\bcomplimentary\b',
     'Guests get a complimentary breakfast.', '房客享有免費早餐。'),
    ('subscription', 'n.', '訂閱', 2, r'\bsubscri(?:be|ber|bers|ption|ptions)\b',
     'I\'d like to renew my monthly subscription.', '我想續訂月費方案。'),
    ('registration', 'n.', '報名；登記', 2, r'\bregist(?:er|ers|ering|ered|ration|rations)\b',
     'I just confirmed my registration.', '我剛確認了報名。'),
    ('orientation', 'n.', '新人訓練；說明會', 3, r'\borientations?\b',
     'Do the interns require an orientation?', '實習生需要新人訓練嗎？'),
    ('workshop', 'n.', '工作坊；研習', 1, r'\bworkshops?\b',
     'Should we organize the workshops for May or June?', '工作坊要辦在五月還是六月？'),
    ('banquet', 'n.', '宴會', 3, r'\bbanquets?\b',
     'How should we arrange the desks for the banquet?', '宴會的桌子要怎麼排？'),
    ('venue', 'n.', '場地', 3, r'\bvenues?\b',
     'Is a larger venue required?', '需要更大的場地嗎？'),
    ('attendee / participant', 'n.', '出席者；參加者', 3, r'\b(?:attendee|participant)s?\b',
     'Were enough gift bags purchased for attendees?', '給出席者的禮品袋買夠了嗎？'),
    ('candidate / applicant', 'n.', '應徵者；候選人', 2, r'\b(?:candidate|applicant)s?\b',
     'She seems like the most qualified applicant.', '她看起來是最合格的應徵者。'),
    ('supervisor', 'n.', '主管', 2, r'\bsupervisors?\b',
     'Report to your supervisor.', '向你的主管報告。'),
    ('colleague / coworker', 'n.', '同事', 1, r'\b(?:colleague|co-?worker)s?\b',
     'Gifts for some of my colleagues.', '要送給幾位同事的禮物。'),
    ('headquarters', 'n.', '總部', 2, r'\bheadquarters\b',
     'Where is your company\'s headquarters?', '你們公司的總部在哪裡？'),
    ('branch', 'n.', '分公司；分店', 2, r'\bbranch(?:es)?\b',
     'Should we open a new branch in Vancouver?', '我們該在溫哥華開新分店嗎？'),
    ('department', 'n.', '部門', 1, r'\bdepartments?\b',
     'Please direct questions to the human resources department.', '請把問題轉給人資部門。'),
    ('shift', 'n.', '輪班', 2, r'\b(?:night |day |morning |evening )?shifts?\b',
     'You\'re working the night shift tomorrow, aren\'t you?', '你明天上夜班，對吧？'),
    ('promotion', 'n.', '升遷；促銷', 2, r'\bpromot(?:e|es|ed|ing|ion|ions)\b',
     'You were informed of Amy\'s promotion, weren\'t you?', '你聽說 Amy 升遷的事了吧？'),
    ('retirement', 'n.', '退休', 2, r'\bretire(?:ment|d|s)?s?\b',
     'What will you bring to Warren\'s retirement party?', '你要帶什麼去 Warren 的退休派對？'),
    ('paycheck / payroll', 'n.', '薪資（單）', 3, r'\bpay(?:check|roll|day)s?\b',
     'Bonuses come with their next paychecks.', '獎金隨下次薪資發放。'),
    ('overtime', 'n./adv.', '加班', 2, r'\bovertime\b',
     'Why is Henry working overtime?', 'Henry 為什麼在加班？'),
    ('sick leave / paid leave', 'n.', '病假／有薪假', 3, r'\b(?:sick|paid|annual|maternity) leave\b|\bon leave\b',
     'Does the company provide paid sick leave?', '公司提供有薪病假嗎？'),
    ('deadline extension', 'n.', '延長期限', 3, r'\b(?:deadline )?extensions?\b',
     'Will the developers require another deadline extension?', '開發人員還需要再延期嗎？'),
    ('budget proposal', 'n.', '預算提案', 3, r'\bbudget (?:proposal|meeting|report)s?\b',
     'When is the budget proposal due?', '預算提案什麼時候截止？'),
    ('cancellation fee', 'n.', '取消費用', 3, r'\bcancellation (?:fee|policy|fees)s?\b',
     'The hotel charges cancellation fees.', '飯店收取消費。'),
    ('security deposit', 'n.', '押金', 4, r'\b(?:security )?deposits?\b',
     'A security deposit is required when signing the lease.', '簽租約時需付押金。'),
    ('real estate agent', 'n.', '房仲', 3, r'\breal estate( agent| agency)?s?\b',
     'You should hire a real estate agent.', '你應該請個房仲。'),
    ('shareholder / stockholder', 'n.', '股東', 4, r'\b(?:share|stock)holders?\b',
     'Graphs for the shareholders meeting.', '股東會用的圖表。'),
    ('merger / acquisition', 'n.', '合併／收購', 4, r'\bmergers?\b|\bacquisitions?\b',
     'Maybe she is going to announce a merger.', '也許她要宣布合併案。'),
    ('turnout', 'n.', '出席人數', 4, r'\bturnouts?\b',
     'The CEO was disappointed with the turnout.', '執行長對出席人數感到失望。'),
]


def load_transcripts():
    src = (DATA / 'transcripts.js').read_text(encoding='utf-8')
    i = src.index('=', src.index('const TRANSCRIPTS')) + 1
    obj, _ = json.JSONDecoder().raw_decode(src[i:].strip())
    return obj


def find_example(pat, trans):
    """挑最合適的真實例句：有中文、長度 6–22 個字、不是作答說明。"""
    best = None
    rx = re.compile(pat, re.I)
    for test, files in trans.items():
        for f, segs in files.items():
            for s in segs:
                t, z = s.get('t', ''), s.get('z', '')
                if not rx.search(t) or not z:
                    continue
                # 題目說明句（refer to the following…）不是自然例句
                if re.search(r'\b(directions|answer sheet|test book|mark the letter'
                             r'|refer to the following|will be spoken)\b', t, re.I):
                    continue
                # 清掉句首題號：「Number 26. / 26.」中文同步清「第 26 題。」
                t = re.sub(r'^\s*Number\s+\d{1,3}\s*[-.,:]\s*|^\s*\d{1,3}\s*[-.,:]\s*', '', t, flags=re.I).strip()
                z = re.sub(r'^第\s*\d+\s*題[。．,，]?\s*', '', z).strip()
                # 清掉選項標記開頭（例句取到 Part 2 的回應時）：「A. 」
                t = re.sub(r'^\(?[ABC]\)?[.,:]\s+', '', t).strip()
                z = re.sub(r'^\(?[ABCＡＢＣ]\)?[。．,，:]\s*', '', z).strip()
                if not rx.search(t):          # 題號清掉後要再確認片語還在
                    continue
                wc = len(t.split())
                if wc < 6 or wc > 22:
                    continue
                score = abs(12 - wc)          # 偏好 12 字左右的句子
                if best is None or score < best[0]:
                    best = (score, t, z)
    return best and (best[1], best[2])


def main():
    trans = load_transcripts()
    scan = '--scan' in sys.argv
    rows, hits = [], 0
    for c, pos, zh, lv, pat, fex, fexzh in C:
        rx = pat or r'\b' + re.escape(c) + r'\b'
        n = sum(1 for _, fl in trans.items() for _, segs in fl.items()
                for s in segs if re.search(rx, s.get('t', ''), re.I))
        found = find_example(rx, trans)
        if found:
            hits += 1
        if scan:
            print(f'{n:4d}  {"✓" if found else " "}  {c}')
            continue
        ex, exzh = found if found else (fex, fexzh)
        # md 表格欄位裡不能有 |
        clean = lambda x: x.replace('|', '/')
        rows.append(f'| {clean(c)} | {pos} | {clean(zh)} | {lv} | {clean(ex)} | {clean(exzh)} |')

    if scan:
        print(f'\n共 {len(C)} 條，逐字稿有真實例句 {hits} 條')
        return

    words_md = ROOT / 'vocab' / 'words' / '搭配詞.md'
    words_md.write_text(
        '# TOEIC 核心搭配詞（例句多取自 27 回模擬考逐字稿，tools/extract_colloc.py 產生）\n\n'
        '| 單字 | 詞性 | 中文釋義 | 級距 | 英文例句 | 例句翻譯 |\n'
        '| --- | --- | --- | --- | --- | --- |\n' + '\n'.join(rows) + '\n',
        encoding='utf-8')
    book_md = ROOT / 'vocab' / 'books' / '搭配詞.md'
    book_md.write_text('# 搭配詞\n\n' + '\n'.join(f'- {c}' for c, *_ in C) + '\n', encoding='utf-8')
    print(f'寫出 {words_md.name}（{len(rows)} 條）與 {book_md.name}；真實例句 {hits} 條')
    print('接著執行：python3 tools/import_vocab.py')


if __name__ == '__main__':
    main()
