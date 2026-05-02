import csv, sys, re

csv.field_size_limit(sys.maxsize)

input_file = 'C:/Users/yukiw/Documents/rp/email_scraper/emails.csv'

with open(input_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

print(f"Total emails: {len(rows)}")

# =====================================================
# Mass sender domains (always F regardless of content)
# =====================================================
mass_sender_domains = [
    # Job platforms
    'rikunabi', 'mynavi', 'indeed', 'wantedly',
    'green-japan', 'bizreach', 'linkedin',
    'en-engage', 'offerbox', 'doda',
    'bacross', 'goodfind', 'intern-street',
    'internstreet', 'gaishishukatsu',
    'shukatsu-kaigi', 'type.js', 'type-net',
    'achivement', 'achievement', 'scouted.',
    # Tech/general platforms
    'naver', 'yahoo', 'google.com', 'amazon', 'apple.com',
    'microsoft.com', 'github.com', 'qiita.com',
    'zenn.dev', 'note.com', 'camp-fire', 'readyfor',
    'kaggle.com', 'paiza.jp', 'atcoder',
    'ted.com', 'wired.com', 'craft.do', 'craftdocs',
    # News/media
    'newspicks', 'wired.com', 'bloomberg',
    'pixabay', '@it', 'atit', 'daily.dev',
    'deeplearning.ai', 'medium.com', 'refind',
    'ground.news', 'exacteditions',    # Shopping/services
    'youtube.com', 'ebay', 'zozotown', 'rakuten',
    'mora', 'gmo.jp', 'pinterest', 'aliexpress',
    'xppen', 'linsoul', 'head-fi',
    'domino', 'ubereats', 'uber.com', 'doordash',
    'hmV', 'hmv', 'loiske', 'rochtke',
    'dlsite', 'withny', 'garmin', 'coinbase',
    'bitflyer', 'for-books',
    # Email/auth
    'protonmail', 'proton.me',
    # Finance
    'money-forward', 'paypay', 'aozorabank',
    # Gaming/entertainment
    'riotgames', 'twitch', 'nintendo',
    'ringconn', 'fantia.jp', 'fantia',
    'ci-en.jp', 'ci-en', 'u-next', 'unext',
    'dmm.com', 'netflix', 'abema',
    'nothing.tech', 'nothingtechnology',
    # Telecom/transport
    'povo', 'fedex', 'diidigi', 'didi',
    'conoha', 'xp_pen',
    # Security/VPN
    'nordvpn', 'nordaccount', 'mozilla',
    # Social
    'instagram', 'reddit.com',
    # Misc services
    'pdfFiller', 'pdffiller',
    'infura', 'infra', 'demae-can', 'demacan',
    'loiske', 'hmv.co', 'chatgpt.com', 'openai.com',
    'scout-ed', 'stackexchange', 'stackoverflow',
    'pokemon', 'adobe.com', 'rplay',
    'kakuyomu', 'alphapolis', 'careerforum',
    'majorhifi', 'presonus', 'cocora',
    'academia.edu', 'pdfguru', 'eblofficial',
    'transportnsw', 'mi.com', 'xiaomi',
    'coconala', 'renew', '42tokyo',
]

# Mass sender name substrings (always F)
mass_sender_names = [
    # Job platforms
    'リクナビ', 'マイナビ', 'Indeed', 'OfferBox',
    'doda', 'Goodfind', '就活会議', '外資就活',
    'キミスカ', 'Intern Street', 'キャリタス',
    'type就活', 'ゼロワンインターン', 'キャリアチケット',
    'アチーブメント', 'ABABA',
    # News/media
    'NewsPicks', 'WIRED', 'Bloomberg', 'Pixabay',
    '@IT通信', '＠IT通信', 'daily.dev',
    'Julie Hook', 'Emma Tucker', 'WSJ', 'Martin from',
    'The Batch', 'The Up Team', 'Refind', 'SCOUTED',
    'DeepLearning.AI',
    # Shopping/services
    'Amazon', 'ZOZOTOWN', '楽天', 'mora',
    'AliExpress', 'Domino', 'XPPEN', 'Linsoul',
    'Head-Fi', 'HMV', 'QUOカード',
    # Social/gaming
    'YouTube', 'eBay', 'Pinterest', 'Kaggle',
    'Medium', 'Twitch', 'Instagram', 'Reddit',
    'Nintendo', 'Riot Games', 'Netflix',
    # Entertainment
    'Fantia', 'Ci-en', 'U-NEXT', 'DMM', 'ABEMA',
    'Manchester United', 'The Colonel',
    # Email/auth
    'Proton', 'RingConn', 'Mozilla',
    # Security/VPN
    'NordVPN', 'Nord Account',
    # Finance
    'Money Forward', 'PayPay', 'あおぞら銀行',
    # Transport/telecom
    'FedEx', 'フェデックス', 'DiDi',
    'DiDi Australia', 'Uber', 'DoorDash',
    'povo', 'ConoHa', '出前館',
    # Misc services
    'pdfFiller', 'Nothing Technology',
    '上馬歯科', 'Y.M_IMAGallery', 'The \'J',
    'Cs Australia', 'Sarah from', 'ChatGPT',
    'ローチケ', '出前館', '江里口',
    'フューチャー新卒', 'Stack Overflow',
    'Pokémon GO', 'Adobe', 'RPLAY',
    'カクヨム', 'アルファポリス', 'CareerForum',
    'MajorHifi', 'PreSonus', 'ココナラ',
    'Academia.edu', 'PDF Guru', 'EBL',
    'Transport for NSW', 'Mi Japan', '伊藤　美波',
]

# =====================================================
# Private / non-job-hunting subject keywords → F
# =====================================================
private_subject_keywords = [
    # Orders/shopping
    '請求書', '領収書', '注文確認', '配送',
    'Order #', 'Shipped:', 'Delivered:', 'Order Confirmation',
    'We found something', 'recommendations',
    'セール', '割引', 'Off ends', '% Off',
    'クーポン', 'ポイント', 'プレゼント',
    '航空券', 'チケット情報', '抽選',
    # Login/auth
    'ログインコード', 'ログインがありました', 'ログイン通知',
    'ログインをお試し', '不審なログイン',
    'New login to', 'への新規ログイン',
    'を使用してログイン', 'ログインを確認',
    '新しいログイン', 'Authentication', 'アカウント切り替え',
    'ワンタイムキー', 'ワンタイムパスワード',
    'Set your password',
    # Salary/work private
    '給与明細',
    # Service notifications
    'システムメンテナンス', 'サービス終了',
    '登録が完了しました', '付与完了',
    'Subscription renewal', 'Payment in',
    '金利', '預金金利', '資産状況',
    'アカウントは削除',
    # Personal/misc
    'お誕生日おめでとう',
    'リマインダー', 'Reminder',
    'メンバー限定', '新しい投稿',
    'no longer available', 'sent a message about',
    'PR　毎日', 'Save 25%', 'Update from',
    'New post by', 'replied to your post',
    'To pair with what you purchased',
    'Last Chance', 'Almost Gone',
    'Claim your FREE', 'Faster, smarter',
    'Automatic reply', 'Automatic',
    'メールマガジン', 'メルマガ',
    '配信停止', '配信解除', 'Ticket Alert',
    # Social media
    'ライブ配信を開始', 'ストーリーズに追加',
    'プロモーションをご利用',
    # Marketing
    'ようこそ', 'Ask anything',
    'About our plans', 'New Era Is',
    'Best of', 'Write everything down',
    'We Miss You',
    # Newsletters
    '通信 第', '通信増刊号',
    'Science of Everything',
    'new event',
    # Job-hunting marketing
    '候補者基準を満たしている',
    '高待遇企業への転職',
    '高待遇の求人紹介',
    '即戦力候補',
    '個別にお送りさせていただきました',
    'キャリアサポートツール',
    'ES選考なしで',
    '受付開始／GD',
    '手応えがない理由',
    'スタートダッシュ',
    'Your receipt from',
    'パスワード再設定',
    # Game/contest
    'カクヨム通信',
    # Misc
    '在外公館等投票', '注意喚起',
    'プラチナポイント',
    'エントリーシート送付',
    'エントリーの御礼',
    'エントリー期限',
    'Serial Code',
    'ご購入完了',
    'Published a new event',
    '申込受付中',
]

# =====================================================
# T signals (only checked if NOT F)
# =====================================================

# Meeting links in body
meeting_link_patterns = [
    r'zoom\.us/j/', r'zoom\.us/wc/', r'zoom\.us/my/',
    r'zoom\.us/meeting/', r'zoom\.us/webinar/',
    r'meet\.google\.com',
    r'teams\.microsoft\.com/l/meetup', r'teams\.live\.com',
]

# T phrases in SUBJECT only
t_subject_phrases = [
    # Selection results
    '内定のお知らせ', '内定通知', '採用内定', '内々定のお知らせ',
    '採用通知', '採用決定', '選考結果', '面接結果',
    'お祈り', '不採用', '不合格', '落選',
    '書類選考通過', '選考通過',
    # Selection invitations
    '面接のご案内', '面接案内', '面接にご招待',
    '面接日程', '面接日のご', '面接実施', '面接設定',
    '面接可能日', '面接希望日', '面接日程調整',
    '選考のご案内', '選考にご招待', '選考へご招待',
    '選考日程', '選考に進んで', '選考へ進',
    '二次面接のご', '最終面接のご', '二次選考のご', '最終選考のご',
    '三次面接', '三次選考',
    '適性検査のご案内', '適性検査案内',
    'WEBテストのご案内', 'WEBテスト案内', 'Webテストのご案内',
    'グループディスカッションのご案内',
    '書類選考の結果',
    '面接のお願い', '面接へのお願い',
    '一次面接', '1次面接',
    '選考招待', '面接招待',
    '面談日程調整',
    # MyPage
    'マイページ登録', 'マイページの登録', 'マイページ開設',
    'ログインID', 'パスワード発行',
    'パスワードのお知らせ', 'ID発行',
    '本登録のお願い', '本登録のご案内',
    'マイページ登録のご案内',
    'マイページの開設',
]

# T phrases in BODY (more specific to avoid false positives)
t_body_phrases = [
    '内定のお知らせ', '内定通知', '採用内定', '内々定のお知らせ',
    '採用通知', '採用決定', '選考結果のお知らせ',
    '面接結果のお知らせ', 'お祈り申し',
    '不採用となりました', '不合格となりました',
    '面接のご案内', '面接日程',
    '選考のご案内', '選考日程',
    '二次面接のご', '最終面接のご',
    '適性検査のご案内', 'WEBテストのご案内', 'Webテストのご案内',
    'マイページ登録', 'マイページの登録',
    '本登録のお願い', '本登録のご案内',
    'オンライン面接のご案内',
    '面談日程調整',
]

# Additional F signals in subject
f_subject_keywords = [
    '合同説明会', '合説', '合同企業説明会', '合同就活',
    '就活フェア', '就活イベント',
    '志向に合った募集', 'ピックアップ', 'おすすめ',
    'あなたに合った', 'あなたにおすすめ',
    '就活速報', 'スカウトが届き',
    'ウェビナー', 'WEBセミナー',
    'セミナー予約',
    'ES免除',
    'インターン募集',
    'オープンカンパニー', 'オープンカンパー',
    'エントリー開始',
    '本選考受付中', '本選考受付',
    'プレエントリー',
    'キャンペーン', 'アンケート',
    '特集', 'ウェビナー',
    '早期内定',
    'ラストチャンス',
    '参加者募集', '参加者は',
    'オファーが届き', 'オファーが取り消さ',
    'メッセージが届き',
    '未読のメッセージ',
    '早期就活生',
    '就活Kickoff',
    'サマーインターン',
    'フォームにご記入',
    '今後の流れについて',
    '新着メッセージ',
    '新着のオファー',
    '未承諾の',
    '豪華特典',
    'データ使い放題',
]

count_t = 0
count_f = 0
count_blank = 0

for row in rows:
    subject = (row.get('subject', '') or '').strip()
    body = (row.get('body', '') or '').strip()
    sender = (row.get('sender_address', '') or '').strip().lower()
    sender_name = (row.get('sender_name', '') or '').strip()

    combined = subject + ' ' + body
    combined_lower = combined.lower()
    subject_lower = subject.lower()

    is_t = False
    is_f = False

    # =============================================
    # Phase 1: Check F - mass sender domains
    # =============================================
    for domain in mass_sender_domains:
        if domain.lower() in sender:
            is_f = True
            break

    # Phase 1b: mass sender names
    if not is_f:
        for name in mass_sender_names:
            if name in sender_name:
                is_f = True
                break

    # =============================================
    # Phase 2: Check F - private / non-job-hunting
    # =============================================
    if not is_f:
        for kw in private_subject_keywords:
            if kw in subject or kw.lower() in subject_lower:
                is_f = True
                break

    # =============================================
    # Phase 3: Check F - additional F subject keywords
    # =============================================
    if not is_f:
        for kw in f_subject_keywords:
            if kw in subject:
                is_f = True
                break

    # =============================================
    # Phase 4: Check T (only if not F)
    # =============================================
    if not is_f:
        # 4a. Meeting links in body
        for p in meeting_link_patterns:
            if re.search(p, combined_lower):
                is_t = True
                break

        # 4b. T phrases in subject
        if not is_t:
            for kw in t_subject_phrases:
                if kw in subject:
                    is_t = True
                    break

        # 4c. T phrases in body (more specific)
        if not is_t:
            for kw in t_body_phrases:
                if kw in body:
                    is_t = True
                    break

    if is_t:
        row['真偽値'] = 'T'
        count_t += 1
    elif is_f:
        row['真偽値'] = 'F'
        count_f += 1
    else:
        row['真偽値'] = ''
        count_blank += 1

print(f"T: {count_t}")
print(f"F: {count_f}")
print(f"Blank: {count_blank}")

# Write output
new_fieldnames = list(fieldnames) + ['真偽値']

with open(input_file, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=new_fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("Done!")
