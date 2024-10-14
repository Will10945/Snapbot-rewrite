import logging

from lib.bot import bot

VERSION = "2.0"

logging.basicConfig(handlers=[logging.FileHandler(filename="relicbot.log",
                                                  encoding='utf-8', mode='a')],
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)

bot.run(VERSION)
