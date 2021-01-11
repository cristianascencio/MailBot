import aiocron, discord, io, os, re, requests

from datetime import datetime
from discord.ext import commands
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from usps import USPSApi

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
USER = os.getenv('DISCORD_USER')
bot = commands.Bot(command_prefix="!")


@bot.command(name="track", help="Track - call function with a USPS tracking number to view the tracking details")
async def track(ctx, package: str):
    api = os.getenv("USPS_API")
    usps = USPSApi(api)
    response = usps.track(package)
    description = response.result['TrackResponse']['TrackInfo']
    if "Error" in description:
        msg = """```css
- {}
```""".format(description["Error"]["Description"])
        print(msg)
        await ctx.send(msg)
    else:
        await ctx.send("hold, i havent implemented working tracking number")


# minute hour day(month) month day(week) seconds?
@aiocron.crontab('12 16 * * *')
async def daily():
    channel = await bot.fetch_user(USER)
    user = os.getenv("ID_USER")
    password = os.getenv("ID_PASS")
    options = FirefoxOptions()
    profile = webdriver.FirefoxProfile()
    profile.set_preference("general.useragent.override", "[user-agent string]")
    options.add_argument('--headless')
    driver = webdriver.Firefox(executable_path="c:\geckodriver.exe", firefox_options=options, firefox_profile=profile)
    driver.get(
        "https://reg.usps.com/portal/login?app=RMIN&appURL=https%3A%2F%2Finformeddelivery.usps.com%2Fbox%2Fpages%2Fintro%2Fstart.action%3Frestart%3D1")
    driver.find_element_by_id("username").send_keys(user)
    driver.find_element_by_id("password").send_keys(password)
    driver.find_element_by_id("btn-submit").click()
    driver.implicitly_wait(5)
    today = datetime.today().strftime("%m/%d/%Y")
    driver.find_element_by_id(today).click()
    num_mail = int(re.findall("\d{1,2}", driver.find_element_by_id(today).text)[0])

    if num_mail == 0:
        await channel.send("There is no mail coming in today!")
    else:
        response = "There are {} piece(s) of mail today!\n".format(num_mail)
        imgs = driver.find_elements_by_class_name("mailpieceIMG")
        if len(imgs) == 0:
            await channel.send(response + "Sorry, there are no images available for today's mail!")
        else:
            response += "These are the available images for today's mail:"
            enum = 1
            my_files = []
            headers = {
                "User-Agent":
                    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
            }
            for img in imgs:
                src = img.get_attribute("src")  # i think this gets the whole string that I need
                session = requests.session()
                session.headers.update(headers)

                for cookie in driver.get_cookies():
                    c = {cookie['name']: cookie['value']}
                    session.cookies.update(c)

                resp = session.get(src, allow_redirects=True)
                data = io.BytesIO(resp.content)
                my_files.append(discord.File(data, datetime.today().strftime("%m_%d_%Y_") + "{}.png".format(enum)))
                enum += 1

            await channel.send(response, files=my_files)

    await channel.send("That's all for today! See you tomorrow!")


bot.run(TOKEN)
