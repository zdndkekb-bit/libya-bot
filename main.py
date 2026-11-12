import discord
from discord.ext import commands
import time
import os
from collections import defaultdict

# حط التوكن الجديد هنا - لازم تكون درت Reset للقديم
TOKEN = os.getenv("DISCORD_TOKEN")

PANEL_SUPPORT = 1570038863886286878
STATUS_SUPPORT = 1559698854792790109
PANEL_ACTIVATION = 1570037714231763006
STATUS_ACTIVATION = 1559698861373522031

PANEL_CITY = 1570245780932132874
STATUS_CITY = 1559698715588165702

# حماية - الايديهات اللي عطيتهملي
LOG_PROTECTION = 1570390900968919050
PANEL_PROTECTION = 1570395118228349048

IMG_OPEN = "https://cdn.discordapp.com/attachments/1569932163527352491/1570039674083217498/IMG-20261111-WA1052.jpg?ex=6af5a4e4&is=6af45364&hm=e525b510f85bb275cae664c499a3965602891bf9d0677ded3fae9a3a438d2a20&"
IMG_CLOSED = "https://cdn.discordapp.com/attachments/1569932163527352491/1570039692013998120/IMG-20261111-WA7940.jpg?ex=6af5a4e8&is=6af45368&hm=a180ed92627cdb086bf14bf4fac9d4ebec496e41ae3223588bddb32b39dd431f&"
IMG_CITY = "https://cdn.discordapp.com/attachments/1561778282071068805/1570244933464629328/IMG-20261110-WA3400.jpg?ex=6af6640d&is=6af5128d&hm=20b5324e5968b310a8ec5bbc24ad02ce92bb93402e56e41bdfba70263893967c&"

SERVER_IP = "94.23.168.153:3372"
SERVER_NAME = "||⫷ @everyone ⫸||"

VOICE_SUPPORT = 1559698641889927220
VOICE_ACTIVATION = 1559698654200336425

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="+", intents=intents)

# ===== نظام الحماية =====
spam_data = defaultdict(list)
join_times = []
raid_mode = False
protection_on = True

async def send_log(text, color=0xFF0000):
    ch = bot.get_channel(LOG_PROTECTION)
    if ch:
        embed = discord.Embed(title="🛡️ نظام الحماية - الواقع الليبي", description=text, color=color)
        await ch.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if protection_on:
        # حماية روابط سيرفرات ثانية
        if "discord.gg/" in message.content or "discord.com/invite" in message.content or "discordapp.com/invite" in message.content:
            if not message.author.guild_permissions.administrator:
                try: await message.delete()
                except: pass
                await send_log(f"🚨 {message.author.mention} حاول ينشر رابط سيرفر ثاني وتم حذفه")
                return
        # حماية سبام
        now = time.time()
        spam_data[message.author.id].append(now)
        spam_data[message.author.id] = [t for t in spam_data[message.author.id] if now - t < 5]
        if len(spam_data[message.author.id]) >= 5:
            try: await message.channel.send(f"⚠️ {message.author.mention} وقف سبام، تم تحذيرك")
            except: pass
            await send_log(f"⚠️ سبام من {message.author.mention} في <#{message.channel.id}>")
            spam_data[message.author.id].clear()
            try: await message.author.timeout(60)
            except: pass
            return
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    global raid_mode
    if not protection_on:
        return
    now = time.time()
    join_times.append(now)
    join_times[:] = [t for t in join_times if now - t < 10]
    if len(join_times) >= 5 and not raid_mode:
        raid_mode = True
        await send_log("🚨🚨 تنبيه ريد! خشو 5 اعضاء في 10 ثواني، تم تفعيل وضع الحماية وقفل الرومات")
        for ch in member.guild.text_channels:
            try: await ch.set_permissions(member.guild.default_role, send_messages=False)
            except: pass
    age = (discord.utils.utcnow() - member.created_at).days
    if age < 7:
        await send_log(f"👀 حساب جديد مشكوك فيه دخل: {member.mention} | عمر الحساب: {age} يوم")

# ===== اوامر الحماية =====
@bot.command(name="حظر")
async def ban_cmd(ctx, member: discord.Member, *, reason="مخالفة قوانين"):
    if not ctx.author.guild_permissions.ban_members:
        await ctx.send("❌ لازم تكون ادمن"); return
    await member.ban(reason=reason)
    await ctx.send(f"✅ تم حظر {member.mention} | السبب: {reason}")
    await send_log(f"🔨 حظر | {member.mention} بواسطة {ctx.author.mention} | السبب: {reason}")

@bot.command(name="طرد")
async def kick_cmd(ctx, member: discord.Member, *, reason="مخالفة"):
    if not ctx.author.guild_permissions.kick_members:
        await ctx.send("❌ لازم تكون ادمن"); return
    await member.kick(reason=reason)
    await ctx.send(f"✅ تم طرد {member.mention}")
    await send_log(f"👢 طرد | {member.mention} بواسطة {ctx.author.mention}")

@bot.command(name="قفل")
async def lock_cmd(ctx):
    if not ctx.author.guild_permissions.manage_channels:
        await ctx.send("❌ لازم تكون ادمن"); return
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 تم قفل الروم")
    await send_log(f"🔒 قفل روم <#{ctx.channel.id}> بواسطة {ctx.author.mention}")

@bot.command(name="فتح")
async def unlock_cmd(ctx):
    if not ctx.author.guild_permissions.manage_channels:
        await ctx.send("❌ لازم تكون ادمن"); return
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 تم فتح الروم")
    await send_log(f"🔓 فتح روم <#{ctx.channel.id}> بواسطة {ctx.author.mention}")

@bot.command(name="حماية")
async def protection_status(ctx):
    embed = discord.Embed(title="🛡️ حالة الحماية", description=f"الحماية: {'🟢 شغالة' if protection_on else '🔴 طافية'}\nوضع الريد: {'🔴 شغال' if raid_mode else '🟢 طافي'}\nحماية السبام: 🟢 شغالة\nحماية الروابط: 🟢 شغالة\nحماية الحسابات الجديدة: 🟢 شغالة", color=0x00FF00)
    await ctx.send(embed=embed)

# ===== لوحة الحماية الجديدة =====
class ProtectionChooseView(discord.ui.View):
    def __init__(self): super().__init__(timeout=60)
    @discord.ui.button(label="تشغيل الحماية 🟢", style=discord.ButtonStyle.success)
    async def on_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        global protection_on
        protection_on = True
        await interaction.response.defer(ephemeral=True)
        await send_log(f"🟢 تم تشغيل الحماية بواسطة {interaction.user.mention}", 0x00FF00)
        await interaction.followup.send("✅ تم تشغيل الحماية", ephemeral=True)
    @discord.ui.button(label="ايقاف الحماية 🔴", style=discord.ButtonStyle.danger)
    async def off_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        global protection_on
        protection_on = False
        await interaction.response.defer(ephemeral=True)
        await send_log(f"🔴 تم ايقاف الحماية بواسطة {interaction.user.mention}")
        await interaction.followup.send("✅ تم ايقاف الحماية", ephemeral=True)
    @discord.ui.button(label="قفل السيرفر 🔒", style=discord.ButtonStyle.secondary)
    async def lock_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        for ch in interaction.guild.text_channels:
            try: await ch.set_permissions(interaction.guild.default_role, send_messages=False)
            except: pass
        await send_log(f"🔒 تم قفل كل الرومات بواسطة {interaction.user.mention}")
        await interaction.followup.send("✅ تم قفل كل الرومات", ephemeral=True)
    @discord.ui.button(label="فتح السيرفر 🔓", style=discord.ButtonStyle.secondary)
    async def unlock_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        global raid_mode
        raid_mode = False
        await interaction.response.defer(ephemeral=True)
        for ch in interaction.guild.text_channels:
            try: await ch.set_permissions(interaction.guild.default_role, send_messages=True)
            except: pass
        await send_log(f"🔓 تم فتح كل الرومات بواسطة {interaction.user.mention}", 0x00FF00)
        await interaction.followup.send("✅ تم فتح كل الرومات", ephemeral=True)

class ProtectionPanelView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="لوحة الحماية", style=discord.ButtonStyle.primary, emoji="🛡️", custom_id="protection_panel_btn")
    async def prot_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ لازم تكون ادمن", ephemeral=True)
            await send_log(f"⚠️ {interaction.user.mention} حاول يضغط على لوحة الحماية وهو مش ادمن")
            return
        await interaction.response.send_message("اختر حالة الحماية:", view=ProtectionChooseView(), ephemeral=True)

@bot.command(name="لوحة_الحماية")
async def لوحة_الحماية(ctx):
    channel = bot.get_channel(PANEL_PROTECTION)
    embed = discord.Embed(title="الواقع الليبي • لوحة الحماية", description="اضغط على الزر للتحكم في حماية السيرفر\n\n🟢 تشغيل / 🔴 ايقاف الحماية\n🔒 قفل كل الرومات وقت الريد\n🔓 فتح كل الرومات\n\nكل حركة حتوصل في روم <#" + str(LOG_PROTECTION) + ">", color=0x2B2D31)
    await channel.send(embed=embed, view=ProtectionPanelView())
    await ctx.send(f"✅ تم تركيب لوحة الحماية في <#{PANEL_PROTECTION}>")

# ===== كودك الاصلي للوحات =====
async def send_status(channel_id, نوع, user, حالة):
    channel = bot.get_channel(channel_id)
    if not channel: return
    now = int(time.time())
    if نوع == "المدينة":
        color = 0x00FF00 if حالة == "مفتوح" else 0xFF0000
        embed = discord.Embed(title=f"الواقع الليبي • حالة المدينة | {SERVER_NAME}", color=color)
        embed.description = f"أسم السيرفر : الواقع الليبي\n\nحالة المدينة : {حالة}\n\nالوقت : <t:{now}:R>\n\nIP السيرفر : `{SERVER_IP}`"
        embed.set_image(url=IMG_CITY)
        await channel.send(embed=embed)
        if حالة == "مغلق":
            await send_log(f"🏙️ المدينة تسكرت بواسطة {user.mention} - تذكر تسكر سيرفر اللعبة {SERVER_IP}")
        return
    img = IMG_OPEN if حالة == "مفتوح" else IMG_CLOSED
    color = 0x00FF00 if حالة == "مفتوح" else 0xFF0000
    if نوع == "الدعم":
        title = "الواقع الليبي • الدعم الفني"
        اسم_الحقل = "أسم الإداري"
        حقل_الحالة = "حالة الدعم"
        صوت_منشن = f"<#{VOICE_SUPPORT}>" if VOICE_SUPPORT != 0 else "|| 🛠️ • انتظار • الدعم"
    else:
        title = "الواقع الليبي • التفعيل"
        اسم_الحقل = "أسم المشرف"
        حقل_الحالة = "حالة التفعيل"
        صوت_منشن = f"<#{VOICE_ACTIVATION}>" if VOICE_ACTIVATION != 0 else "🔒 | انتظار • التفعيل"
    embed = discord.Embed(title=title, color=color)
    embed.description = f"{اسم_الحقل} : {user.mention}\n\n{حقل_الحالة} : {حالة}\n\nالوقت : <t:{now}:R>\n\nصوت : {صوت_منشن}"
    embed.set_image(url=img)
    await channel.send(embed=embed)

class SupportChooseView(discord.ui.View):
    def __init__(self): super().__init__(timeout=60)
    @discord.ui.button(label="فتح 🟢", style=discord.ButtonStyle.success)
    async def open_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await send_status(STATUS_SUPPORT, "الدعم", interaction.user, "مفتوح")
        await interaction.followup.send("✅ غيرت حالة الدعم لـ **مفتوح**", ephemeral=True)
        try: await interaction.delete_original_response()
        except: pass
    @discord.ui.button(label="إغلاق 🔴", style=discord.ButtonStyle.danger)
    async def close_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await send_status(STATUS_SUPPORT, "الدعم", interaction.user, "مغلق")
        await interaction.followup.send("✅ غيرت حالة الدعم لـ **مغلق**", ephemeral=True)
        try: await interaction.delete_original_response()
        except: pass

class ActivationChooseView(discord.ui.View):
    def __init__(self): super().__init__(timeout=60)
    @discord.ui.button(label="فتح 🟢", style=discord.ButtonStyle.success)
    async def open_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await send_status(STATUS_ACTIVATION, "التفعيل", interaction.user, "مفتوح")
        await interaction.followup.send("✅ غيرت حالة التفعيل لـ **مفتوح**", ephemeral=True)
        try: await interaction.delete_original_response()
        except: pass
    @discord.ui.button(label="إغلاق 🔴", style=discord.ButtonStyle.danger)
    async def close_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await send_status(STATUS_ACTIVATION, "التفعيل", interaction.user, "مغلق")
        await interaction.followup.send("✅ غيرت حالة التفعيل لـ **مغلق**", ephemeral=True)
        try: await interaction.delete_original_response()
        except: pass

class CityChooseView(discord.ui.View):
    def __init__(self): super().__init__(timeout=60)
    @discord.ui.button(label="فتح 🟢", style=discord.ButtonStyle.success)
    async def open_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await send_status(STATUS_CITY, "المدينة", interaction.user, "مفتوح")
        await interaction.followup.send("✅ غيرت حالة المدينة لـ **مفتوح**", ephemeral=True)
        try: await interaction.delete_original_response()
        except: pass
    @discord.ui.button(label="إغلاق 🔴", style=discord.ButtonStyle.danger)
    async def close_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        await send_status(STATUS_CITY, "المدينة", interaction.user, "مغلق")
        await interaction.followup.send("✅ غيرت حالة المدينة لـ **مغلق**", ephemeral=True)
        try: await interaction.delete_original_response()
        except: pass

class SupportPanelView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="الدعم الفني", style=discord.ButtonStyle.primary, emoji="🛠️", custom_id="support_panel_btn")
    async def support_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ لازم تكون ادمن", ephemeral=True)
            await send_log(f"⚠️ {interaction.user.mention} حاول يضغط على لوحة الدعم وهو مش ادمن")
            return
        await interaction.response.send_message("اختر حالة الدعم الفني:", view=SupportChooseView(), ephemeral=True)

class ActivationPanelView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="التفعيل", style=discord.ButtonStyle.primary, emoji="✅", custom_id="activation_panel_btn")
    async def activation_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ لازم تكون ادمن", ephemeral=True)
            await send_log(f"⚠️ {interaction.user.mention} حاول يضغط على لوحة التفعيل وهو مش ادمن")
            return
        await interaction.response.send_message("اختر حالة التفعيل:", view=ActivationChooseView(), ephemeral=True)

class CityPanelView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="حالة المدينة", style=discord.ButtonStyle.primary, emoji="🏙️", custom_id="city_panel_btn")
    async def city_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ لازم تكون ادمن", ephemeral=True)
            await send_log(f"⚠️ {interaction.user.mention} حاول يضغط على لوحة المدينة وهو مش ادمن")
            return
        await interaction.response.send_message("اختر حالة المدينة:", view=CityChooseView(), ephemeral=True)

@bot.command(name="لوحة_الدعم")
async def لوحة_الدعم(ctx):
    channel = bot.get_channel(PANEL_SUPPORT)
    embed = discord.Embed(title="الواقع الليبي • لوحة الدعم الفني", description="اضغط على الزر لتغيير حالة قسم الدعم الفني (مغلق / مفتوح) وسيتم إرسالها تلقائيا في الروم المخصص.", color=0x2B2D31)
    await channel.send(embed=embed, view=SupportPanelView())
    await ctx.send(f"✅ تم تركيب لوحة الدعم في <#{PANEL_SUPPORT}>")

@bot.command(name="لوحة_التفعيل")
async def لوحة_التفعيل(ctx):
    channel = bot.get_channel(PANEL_ACTIVATION)
    embed = discord.Embed(title="الواقع الليبي • لوحة التفعيل", description="اضغط على الزر لتغيير حالة قسم التفعيل (مغلق / مفتوح) وسيتم إرسالها تلقائيا في الروم المخصص.", color=0x2B2D31)
    await channel.send(embed=embed, view=ActivationPanelView())
    await ctx.send(f"✅ تم تركيب لوحة التفعيل في <#{PANEL_ACTIVATION}>")

@bot.command(name="لوحة_المدينة")
async def لوحة_المدينة(ctx):
    channel = bot.get_channel(PANEL_CITY)
    embed = discord.Embed(title="الواقع الليبي • لوحة حالة المدينة", description=f"اضغط على الزر لتغيير حالة المدينة (مغلق / مفتوح)\n\n**السيرفر:** {SERVER_NAME}\n**IP:** `{SERVER_IP}`", color=0x2B2D31)
    embed.set_image(url=IMG_CITY)
    await channel.send(embed=embed, view=CityPanelView())
    await ctx.send(f"✅ تم تركيب لوحة المدينة في <#{PANEL_CITY}>")

@bot.command(name="ركب_الكل")
async def ركب_الكل(ctx):
    await لوحة_الدعم(ctx)
    await لوحة_التفعيل(ctx)
    await لوحة_المدينة(ctx)
    await لوحة_الحماية(ctx)

@bot.event
async def on_ready():
    print(f"✅ شغال: {bot.user}")
    bot.add_view(SupportPanelView())
    bot.add_view(ActivationPanelView())
    bot.add_view(CityPanelView())
    bot.add_view(ProtectionPanelView())

bot.run(TOKEN)
