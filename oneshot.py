import os, re, requests, discord, io, asyncio, logging

from dotenv import load_dotenv
from discord.ext import commands
from datetime import datetime
from selenium import webdriver
from selenium.webdriver import FirefoxOptions

logging.basicConfig(filename="oneshot.log", filemode='a', format='%(asctime)s-%(process)d-%(levelname)s-%(message)s', level=logging.ERROR)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
USER = os.getenv('DISCORD_USER')
bot = commands.Bot(command_prefix="!")


async def scrapeid():
    await asyncio.sleep(5)
    channel = await bot.fetch_user(int(USER))
    user = os.getenv("ID_USER")
    password = os.getenv("ID_PASS")
    options = FirefoxOptions()
    profile = webdriver.FirefoxProfile()
    profile.set_preference("general.useragent.override", "[user-agent string]")
    options.add_argument('--headless')
    options.add_argument('--start-maximized')
    driver = webdriver.Firefox(executable_path="c:\geckodriver.exe", firefox_options=options, firefox_profile=profile)
    driver.get(
        "https://reg.usps.com/portal/login?app=RMIN&appURL=https%3A%2F%2Finformeddelivery.usps.com%2Fbox%2Fpages%2Fintro%2Fstart.action%3Frestart%3D1")
    driver.find_element_by_id("username").send_keys(user)
    driver.find_element_by_id("password").send_keys(password)
    driver.find_element_by_id("btn-submit").click()

    #await asyncio.sleep(5)

    today = datetime.today().strftime("%m/%d/%Y")

    try:
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

        packages = driver.find_elements_by_class_name("pack_row")
        driver.find_element_by_id("pkgtab").click()

        msg = "\n"
        num_pkg = 0
        for pkg in packages:
            status = pkg.find_element_by_class_name("pack_status-bigNumber")
            details = pkg.find_element_by_class_name("pack_details")
            lastscan = pkg.find_element_by_class_name("pack_lastscan_desk")

            if len(details.find_elements_by_class_name("pack_green")) != 0:
                break

            num_pkg += 1
            msg += "Package {}".format(num_pkg)
            msg += "```Tracking number: " + details.find_element_by_class_name("pack_h4").text + "\n"
            month = str(status.find_element_by_class_name("date-small.pack_blue").text).title()
            msg += "Expected Delivery {} {} ".format(month,
                                                     status.find_element_by_class_name("date-num-large.pack_blue").text)
            msg += re.findall("(by .*$|between .*$)", details.find_element_by_class_name("pack_blue").text)[0]
            scan = "\t" + str(lastscan.text).replace("\n", "\n\t")
            msg += "\nLast Scan:\n{}".format(scan)
            msg += "```"

        if num_pkg > 0:
            await channel.send("There are {} incoming packages".format(num_pkg) + msg)
        else:
            await channel.send("There are no incoming packages.")

        await channel.send("That's all for today! See you tomorrow!")
    except Exception:
        await channel.send("Unable to finish fetching mail information. Please check oneshot.log for more information.")
        logging.error(Exception)

    driver.close()
    await bot.close()


bot.loop.create_task(scrapeid())
bot.run(TOKEN)
