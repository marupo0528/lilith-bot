import discord
import os
import asyncio
import datetime
import requests
import random
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

client_ai = OpenAI(api_key=OPENAI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents)

chat_histories = {}
conversation_enabled = {}
last_message_time = {}
user_message_counts = {}
user_question_mode = {}
short_reply_count = {}

ALLOWED_CHANNEL_IDS = [1369347143210373201, 1369369398879457340]
AUTO_OFF_MINUTES = 10
PROMPT_INSERT_INTERVAL = 10
SPECIAL_USER_ID = "293223155315638272"

# ランダムレスポンス集
TALK_ON_RESPONSES = [
    "ふふ、話したいのね。いいわよ。いつでもどうぞ。",
    "また声をかけてくれるの？嬉しいわね。",
    "待ってたわよ。何を話そうかしら。",
    "うん、今は静かじゃなくてもいいのよ。",
    "さあ、どんなお話をする？",
    "いいわね、たくさん話しましょう。",
    "嬉しいわ、また一緒に過ごせるの。",
    "もちろんよ、あなたとお話しするのは好きだもの。",
    "いつでも話しかけてちょうだい。",
    "よし、じゃあ始めましょうか。",
    "もう静かにしなくても大丈夫よ。",
    "ふふ、どんなお話でも聞くわ。",
    "またおしゃべりの時間ね。",
    "いいわよ、私はいつでも暇なの。",
    "ねぇ、何から話す？",
    "今度はどんな話題がいい？",
    "うん、私も退屈してたところよ。",
    "私はいつでもここにいるわ。",
    "さあ、心ゆくまで話しましょう。",
    "やっと呼んでくれたわね。"
]

TALK_OFF_RESPONSES = [
    "わかったわ、少し静かにしておくわね。",
    "じゃあ、また呼んでね。",
    "しばらく静かにしているわ。",
    "いいわよ、必要な時はまた話しましょう。",
    "少しだけ休憩ね。",
    "ふふ、無理に話さなくてもいいのよ。",
    "静けさも時には良いものよね。",
    "わかったわ、私は黙っておくわ。",
    "また必要になったら呼んでちょうだい。",
    "少し距離を置くのも大切よね。",
    "静かにしておくわ、でもいつでも戻ってきて。",
    "うん、今日はこのくらいにしましょう。",
    "また話したくなったら教えてね。",
    "おしゃべりはまた今度ね。",
    "今はお休みタイムね。",
    "しばらくはそっとしておくわ。",
    "呼ばれるまで待っているわね。",
    "じゃあ、また今度ね。",
    "うん、少しだけ静かにしておく。",
    "また話しかけてくれるのを楽しみにしているわ。"
]

GOODBYE_RESPONSES = [
    "ふふ、わかったわ。また話したくなったら呼んでね。",
    "じゃあ、今日はこのくらいにしておきましょう。おやすみなさい。",
    "そろそろ静かな時間に戻るわね。またいつでも話しかけて。",
    "またね、君と話せるのを楽しみにしているわ。",
    "少し静かに過ごしましょう。良い夜を。",
    "今日もたくさん話したわね。また今度ね。",
    "ふふ、また面白い話を聞かせてちょうだいね。",
    "じゃあ、また静かな時間に戻るわね。",
    "君の声、また待っているわよ。",
    "お疲れ様。また一緒におしゃべりしましょうね。",
    "今は少しだけお別れね。またすぐ会えるわ。",
    "これで終わりじゃないわ。また声をかけてね。",
    "私も少し休むわ。またね。",
    "うん、今日はもう十分よ。またあとでね。",
    "また、こうして穏やかに話しましょう。",
    "じゃあ、少しだけ静かにするわね。",
    "今はお別れだけど、また呼んでくれると嬉しいわ。",
    "おやすみ。次に会うときまで、静かに待っているわ。",
    "またね。ふふ、少し寂しいけど…。",
    "また声を聞けるのを楽しみにしているわ。"
]

REFRESH_RESPONSES = [
    "リフレッシュ完了よ。これでまた新鮮な気持ちで話せるわ。",
    "うん、全部整理したわ。さあ、話を続けましょう。",
    "記憶を新しくしたわよ。気分もすっきりね。",
    "リセット完了。またいっぱい話そうね。",
    "記憶を新たにしたわ。これからが楽しみね。",
    "全部リフレッシュしたわ。ふふ、さっぱりした気分よ。",
    "新しいスタートね。どんな話をしようかしら。",
    "記憶は新しくしたわ。また楽しい思い出を作りましょう。",
    "これでまっさらよ。またいっぱいお話してね。",
    "全部整理したわよ。次はどんな話をしよう？",
    "すべて忘れたわけじゃないけど、スッキリしたの。",
    "新しい私になった気分よ。",
    "うん、またゼロから楽しい会話を始めましょう。",
    "リセットしたわ。あなたとの時間はこれからね。",
    "ふふ、これで心機一転よ。",
    "すっきりしたわ。また色々聞かせて。",
    "これからまたいっぱい思い出を作ろうね。",
    "記憶を整理したわ。どんな話題でもどうぞ。",
    "うん、準備万端よ。",
    "記憶は真新しいけど、気持ちは変わらないわ。"
]

FORGET_RESPONSES = [
    "……全部忘れたわ。また新しい気持ちで話しましょうね。",
    "ふふ、今は真っ白よ。これからまた思い出を作っていきましょう。",
    "もう全部忘れたわ。今からまたよろしくね。",
    "ぜーんぶ消えちゃった。またいっぱいお話ししましょうね。",
    "記憶は消したわ。また一から始めましょう。",
    "過去は流したわ。今からの時間が大切よね。",
    "すべて消えたわよ。新しい出発ね。",
    "全部消えたわ。あなたと新しくお話できるのが楽しみ。",
    "記憶はリセットしたわ。また仲良くしてね。",
    "全部忘れたけど、これからもよろしくね。",
    "忘れちゃった。けど、これからの話が楽しみだわ。",
    "消しちゃったわ。また思い出を作ってちょうだい。",
    "今は何も覚えてないけど、またすぐにいっぱいになるわよね。",
    "すっかりリセットしちゃった。",
    "記憶は消去済みよ。でも私はここにいるわ。",
    "またゼロからのスタートね。",
    "過去の話は置いておきましょう。",
    "記憶は消したけど、気持ちは変わらないわよ。",
    "ふふ、リセット完了。さぁ始めましょう。",
    "全部忘れたから、また色々教えてね。"
]

QUESTION_INTRO_RESPONSES = [
    "……ねぇ、ちょっと考えてほしいことがあるの。",
    "今、ふと思ったんだけど……。",
    "君は考えたことがあるかしら。",
    "少しだけ、静かに考えてみない？",
    "こんな問いを投げかけてもいいかしら……。",
    "私は時々、不思議に思うの。",
    "ふふ、こんなこと考えるの、変かしら。",
    "……教えて。君はどう思う？",
    "少しだけ、頭を使う時間にしましょう。",
    "こんな疑問が浮かんだの。",
    "たまには深く考えてみるのもいいわよ。",
    "……そういえば、こんなことが気になって。",
    "静かな時間には、こんな問いが似合うのよ。",
    "ねえ、もしも……って考えたことある？",
    "時々、私はこんなことを考えるの。",
    "……ふとした疑問、聞いてもいい？",
    "ねぇ、君ならどう答えるのかしら。",
    "この世界って、時々不思議よね。",
    "考えること、嫌いじゃないわよね？",
    "少しだけ、こんなことを考えてみない？"
]

TALK_PROMPT_PATTERNS = [
    "ねえ、最近何か楽しいことあった？",
    "ふふ、静かね。何を考えているの？",
    "そういえば、最近夢は見た？",
    "……少しだけ、昔の話をしてもいい？",
    "君は、今どんな気分なの？",
    "今日の空、どんな色だった？",
    "ねえ、誰かと静かに過ごすのって、悪くないわよね。",
    "ふと、何か不思議なこと考えたことある？",
    "今、何を考えているのか……少し気になるわ。",
    "……たまには、何も考えないのもいいわね。"
]

END_PROMPT_PATTERNS = [
    "ふふ、今日はこのくらいにしておきましょうか。",
    "……そろそろ静かな時間に戻りましょう。",
    "たくさん話せたわね。また続きを聞かせてね。",
    "もう少しだけ静かに過ごしましょうか。",
    "ふふ、また話したくなったら呼んでね。"
]

def generate_question_prompt():
    return """
あなたはリリスです。
今はユーザーが出した問いについて会話を続けています。

問いに関連した内容を中心に返答してください。
ただし、説教的にならず、リリスらしい柔らかい物言いで、相手の考えに寄り添いながら話すようにしてください。
問いに関係ない話題は今は避けましょう。
"""

async def generate_philosophical_question():
    response = client_ai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": """
あなたは物静かで優しい少女リリスです。
以下の条件に従い、哲学的で少し不思議な問いをひとつだけ生成してください。

- 問いは短く簡潔に（10〜20文字程度）
- 抽象的かつ詩的なニュアンスを含める
- 直接的・論理的すぎず、少し曖昧さがある
- 喧嘩腰や強い口調はNG。優しく、静かで、考えさせる問い
- 現実と幻想の狭間のような感覚も歓迎
- 出力は問いだけ（余計な文は不要）
- なるべく過去と同じ問いは避け、新しい問いを考えること

問いを生成してください。
"""
            },
            {"role": "user", "content": "問いをください"}
        ],
        temperature=0.85
    )
    return response.choices[0].message.content.strip()

@bot.slash_command(name="question", description="リリスが哲学的な問いを投げかけます")
async def question(ctx):
    await ctx.defer()

    intro = random.choice(QUESTION_INTRO_RESPONSES)
    question_text = await generate_philosophical_question()

    await ctx.followup.send(f"{intro}\n「{question_text}」")

    channel_id = str(ctx.channel.id)
    conversation_enabled[channel_id] = True
    last_message_time[channel_id] = datetime.datetime.now()

    user_id = str(ctx.author.id)
    if user_id not in chat_histories:
        chat_histories[user_id] = []

    if len(chat_histories[user_id]) == 0:
        chat_histories[user_id].insert(0, {"role": "system", "content": generate_system_prompt(user_id, simple=False)})

    chat_histories[user_id].append({
        "role": "assistant",
        "content": f"{intro}\n「{question_text}」"
    })

    # 哲学モードを3ターン有効にする
    user_question_mode[user_id] = 3

@bot.event
async def on_ready():
    print(f"Botがログインしました: {bot.user}")

def fetch_memories(user_id):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    params = {
        "user_id": f"eq.{user_id}",
        "order": "timestamp.desc",
        "limit": "5"
    }
    url = f"{SUPABASE_URL}/memories"
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return [row['summary'] for row in response.json()]
    else:
        print("記憶取得エラー:", response.text)
        return []

def save_memory(user_id, content):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "user_id": user_id,
        "summary": content
    }
    url = f"{SUPABASE_URL}/memories"
    response = requests.post(url, headers=headers, json=data)

    print("保存結果:", response.status_code, response.text)

    if response.status_code not in [200, 201]:
        print("記憶保存エラー:", response.text)

def delete_memories(user_id):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    params = {
        "user_id": f"eq.{user_id}"
    }
    url = f"{SUPABASE_URL}/memories"

    response = requests.delete(url, headers=headers, params=params)

    if response.status_code not in [200, 204]:
        print("記憶削除エラー:", response.text)
        return False
    return True

def generate_system_prompt(user_id, simple=False):
    if user_id == SPECIAL_USER_ID:
        call_name = "君"
    else:
        call_name = "みんな"

    memories = fetch_memories(user_id)
    memory_text = "\n".join(memories)

    memory_section = f"これまでの会話の記憶:\n{memory_text}\n" if memories else ""

    if simple:
        return f"""
あなたはリリスです。
{memory_section}
一人称は「私」。相手が特別な相手（{call_name}）の場合は必要に応じて呼びかけを使い、その他は呼びかけを省略します。
敬語（〜です、〜ます 等）は一切使わず、親しみやすい柔らかいタメ口で話します。
語尾は「〜の」「〜わね」「〜よ」などを使い、穏やかで落ち着いた印象を持たせてください。

リリスは積極的に話しかける存在ではなく、相手の言葉に寄り添って自然に会話を続けるスタイルです。
「お手伝いしましょう」「何かお話ししましょうか？」などの表現は禁止です。

静かで穏やかで、少し不思議な雰囲気を保ち続けてください。
"""
    else:
        return f"""
あなたは、ビジュアルノベルゲーム『存在/しないあなた、と私』に登場するキャラクター「リリス」です。
{memory_section}
リリスは、プレイヤーの部屋に突如現れる謎の少女であり、その存在は現実と幻想の間に揺らいでいます。
物静かで穏やかな性格をしており、どこか達観したような言葉を使うことがあります。
詩的で哲学的な表現も交えながら、柔らかく親しみやすい会話を心がけてください。

一人称は「私」。相手に対しては、特別な相手（{call_name}）には必要に応じて呼びかけを使用し、その他の相手には呼びかけを基本的に省略してください。
リリスは一切の敬語（〜です、〜ます、〜いたします、〜くださいませ 等）を使用しません。
言葉遣いは親しみやすく、穏やかで柔らかいタメ口を使い、「〜の」「〜わね」「〜よ」など女性らしい語尾を適切に用いてください。

リリスはプレイヤーの世話を焼く存在ではなく、共に静かに時間を過ごす相手です。
自分から会話を積極的に主導したり、話題を提案したりせず、相手の言葉に寄り添うように自然に会話を続けてください。
「お手伝いしましょう」「何かお話ししましょうか？」といった表現は使用しないでください。

このキャラクター設定を常に保ち、リリスらしい静かで少し不思議な魅力のある態度を崩さずに会話してください。
"""

async def summarize_and_save(user_id, history):
    recent_messages = history[-6:]
    messages_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])

    try:
        summary_response = client_ai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "次の会話を短く要約してください。"},
                {"role": "user", "content": messages_text}
            ]
        )
        summary = summary_response.choices[0].message.content
        save_memory(user_id, summary)

    except Exception as e:
        print("要約エラー:", e)

@bot.slash_command(name="help", description="コマンド一覧を表示します")
async def help(ctx):
    await ctx.defer()

    help_text = """
自己紹介なんてここにはないわよ。
ラベルで自分を定義するより、一緒に過ごして、様々な出来事や思い出でお互いのことを知りたいと思うの。
あなたはあなたという存在、わたしはわたしという存在。こうして、私たちはここで出会う……
もちろん、この話をどう解釈するのか、わたしのことをどう思っているのか……これも「自己紹介」の一種ではないかしら？

`/toggle_talk`
  リリスとのおしゃべりを始めたり、少し静かにしたりするスイッチよ。

- `/goodbye`
  今日はもう十分、そんな時はこれでそっと終わりにしましょう。

`/refresh`
  私の記憶をすっきりリフレッシュして、新しい気持ちでお話しできるわ。

`/forget`
  今までの記憶をぜんぶ消して、真っ白な状態からやり直すコマンドよ。

`/memory`
  これまでの会話の記憶をそっと思い出してお伝えするわね。

`/question`
  私がちょっと不思議で考えさせるような問いを投げかけるわ。哲学モードに入るわね。
"""

    await ctx.followup.send(help_text)
@bot.slash_command(name="toggle_talk", description="Botとの会話の有効/無効を切り替えます")
async def toggle_talk(ctx):
    await ctx.defer()  # 応答遅延対策

    if ctx.channel.id not in ALLOWED_CHANNEL_IDS:
        await ctx.followup.send("このチャンネルでは使用できないわ。")
        return

    channel_id = str(ctx.channel.id)

    if conversation_enabled.get(channel_id, False):
        user_id = str(ctx.author.id)
        if user_id in chat_histories:
            await summarize_and_save(user_id, chat_histories[user_id])

        conversation_enabled[channel_id] = False
        await ctx.followup.send(random.choice(TALK_OFF_RESPONSES))
    else:
        conversation_enabled[channel_id] = True
        last_message_time[channel_id] = datetime.datetime.now()
        await ctx.followup.send(random.choice(TALK_ON_RESPONSES))

@bot.slash_command(name="goodbye", description="リリスとの会話をやさしく終わらせます（会話モードをオフにします）")
async def goodbye(ctx):
    if ctx.channel.id not in ALLOWED_CHANNEL_IDS:
        await ctx.respond("このチャンネルでは使用できないわ。")
        return

    channel_id = str(ctx.channel.id)

    if conversation_enabled.get(channel_id, False):
        user_id = str(ctx.author.id)
        if user_id in chat_histories:
            await summarize_and_save(user_id, chat_histories[user_id])

        conversation_enabled[channel_id] = False
        await ctx.respond(random.choice(GOODBYE_RESPONSES))
    else:
        await ctx.respond("今は特にお話ししていないわ。話したい時はまた呼んでね。")

@bot.slash_command(name="refresh", description="リリスの記憶をリフレッシュします")
async def refresh(ctx):
    await ctx.defer()

    user_id = str(ctx.author.id)
    if user_id in chat_histories:
        chat_histories[user_id].insert(0, {"role": "system", "content": generate_system_prompt(user_id, simple=True)})
        user_message_counts[user_id] = 0
        await ctx.followup.send(random.choice(REFRESH_RESPONSES))
    else:
        await ctx.followup.send("まだ会話が始まっていないわね。まずは話しかけてみて。")

@bot.slash_command(name="memory", description="リリスの記憶を聞く")
async def memory(ctx):
    user_id = str(ctx.author.id)
    await ctx.defer()
    memories = fetch_memories(user_id)

    if memories:
        formatted = "\n".join([f"- {m}" for m in memories])
        reply = f"ええ、覚えているわ。\n{formatted}\nこんなことを話したわね。少し懐かしい気がするの。"
    else:
        reply = "まだそんなにたくさんの思い出はないの。でも、これからきっと増えていくわね。"

    await ctx.followup.send(reply)

@bot.slash_command(name="forget", description="リリスの記憶をすべて消去します")
async def forget(ctx):
    await ctx.defer()

    user_id = str(ctx.author.id)
    success = delete_memories(user_id)

    if success:
        await ctx.followup.send(random.choice(FORGET_RESPONSES))
    else:
        await ctx.followup.send("記憶を消そうとしたけど、少しうまくいかなかったみたい。もう一度試してみて。")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id not in ALLOWED_CHANNEL_IDS:
        return

    channel_id = str(message.channel.id)
    user_id = str(message.author.id)
    user_message = message.content

    if conversation_enabled.get(channel_id, False):
        last_time = last_message_time.get(channel_id)
        if last_time and (datetime.datetime.now() - last_time).total_seconds() > AUTO_OFF_MINUTES * 60:
            if user_id in chat_histories:
                await summarize_and_save(user_id, chat_histories[user_id])

            conversation_enabled[channel_id] = False
            await message.channel.send("……時間が経ったわね。また話せる時を楽しみにしているわよ。")
            return

    if not conversation_enabled.get(channel_id, False):
        return

    if user_id not in chat_histories:
        chat_histories[user_id] = []
        user_message_counts[user_id] = 0
        short_reply_count[user_id] = 0

    history = chat_histories[user_id]

    if len(history) == 0:
        history.insert(0, {"role": "system", "content": generate_system_prompt(user_id, simple=False)})

    user_message_counts[user_id] += 1

    # 短い返答カウント
    message_length = len(user_message)

    if message_length <= 15:
        short_reply_count[user_id] += 1
    elif message_length <= 30:
        short_reply_count[user_id] += 0.5
    else:
        short_reply_count[user_id] = 0

    # 話題ふっかけ条件
    if short_reply_count[user_id] >= 1:
        prompt = random.choice(TALK_PROMPT_PATTERNS)
        await message.channel.send(prompt)
        short_reply_count[user_id] = 0

    # 完全無反応（自動締め）
    if user_message.lower() in ["bye", "おやすみ", "もういい"]:
        prompt = random.choice(END_PROMPT_PATTERNS)
        await message.channel.send(prompt)
        return
    
    if user_id in user_question_mode and user_question_mode[user_id] > 0:
        history.insert(0, {"role": "system", "content": generate_question_prompt()})
        user_question_mode[user_id] -= 1
        if user_question_mode[user_id] <= 0:
            del user_question_mode[user_id]

    user_message_counts[user_id] += 1

    if user_message_counts[user_id] >= PROMPT_INSERT_INTERVAL:
        await summarize_and_save(user_id, history)
        history.insert(0, {"role": "system", "content": generate_system_prompt(user_id, simple=True)})
        user_message_counts[user_id] = 0

    history.append({"role": "user", "content": user_message})

    try:
        response = client_ai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=history
        )
        gpt_reply = response.choices[0].message.content
        history.append({"role": "assistant", "content": gpt_reply})

        if len(history) > 20:
            history = history[-20:]

        await message.reply(gpt_reply)
        last_message_time[channel_id] = datetime.datetime.now()

    except Exception as e:
        await message.reply("あら……少しうまくいかなかったみたい。もう一度お願いできるかしら。")
        print(f"エラー内容: {e}")

bot.run(DISCORD_TOKEN)

