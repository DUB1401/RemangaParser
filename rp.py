#!/usr/bin/python

from Source.Functions import SecondsToTimeString, ManageOtherFormatsFiles
from dublib.Methods import Cls, Shutdown, ReadJSON, WriteJSON
from Source.RequestsManager import RequestsManager
from Source.TitleParser import TitleParser
from Source.Collector import Collector
from Source.Formatter import Formatter
from Source.Updater import Updater
from dublib.Terminalyzer import *
from Source.Functions import Wait

import datetime
import logging
import json
import time
import sys
import os

#==========================================================================================#
# >>>>> ПРОВЕРКА ВЕРСИИ PYTHON <<<<< #
#==========================================================================================#

# Минимальная требуемая версия Python.
PythonMinimalVersion = (3, 10)
# Проверка соответствия.
if sys.version_info < PythonMinimalVersion:
	sys.exit("Python %s.%s or later is required.\n" % PythonMinimalVersion)

#==========================================================================================#
# >>>>> ИНИЦИАЛИЗАЦИЯ ЛОГОВ <<<<< #
#==========================================================================================#

# Создать директорию для логов, если такая отсутствует.
if os.path.exists("Logs") is False:
	os.makedirs("Logs")

# Получение текущей даты.
CurrentDate = datetime.datetime.now()
# Время запуска скрипта.
StartTime = time.time()
# Формирование пути к файлу лога.
LogFilename = "Logs/" + str(CurrentDate)[:-7] + ".log"
LogFilename = LogFilename.replace(':', '-')
# Установка конфигнурации.
logging.basicConfig(filename = LogFilename, encoding = "utf-8", level = logging.INFO, format = "%(asctime)s %(levelname)s: %(message)s", datefmt = "%Y-%m-%d %H:%M:%S")
# Отключение логгирования selenium-wire.
logging.getLogger("seleniumwire").setLevel(logging.CRITICAL)

#==========================================================================================#
# >>>>> ЧТЕНИЕ НАСТРОЕК <<<<< #
#==========================================================================================#

# Вывод в лог заголовка: подготовка скрипта к работе.
logging.info("====== Preparing to starting ======")
# Запись в лог используемой версии Python.
logging.info("Starting with Python " + str(sys.version_info.major) + "." + str(sys.version_info.minor) + "." + str(sys.version_info.micro) + " on " + str(sys.platform) + ".")
# Запись команды, использовавшейся для запуска скрипта.
logging.info("Launch command: \"" + " ".join(sys.argv[1:len(sys.argv)]) + "\".")
# Расположении папки установки веб-драйвера в директории скрипта.
os.environ["WDM_LOCAL"] = "1"
# Отключение логов WebDriver.
os.environ["WDM_LOG"] = str(logging.NOTSET)
# Глобальные настройки.
Settings = ReadJSON("Settings.json")

# Интерпретация выходной директории обложек и коррекция пути.
if Settings["covers-directory"] == "":
	Settings["covers-directory"] = "Covers/"
	
elif Settings["covers-directory"][-1] != '/':
	Settings["covers-directory"] += "/"

# Интерпретация выходной директории обложек и коррекция пути.
if Settings["titles-directory"] == "":
	Settings["titles-directory"] = "Titles/"
	
elif Settings["titles-directory"][-1] != '/':
	Settings["titles-directory"] += "/"

# Запись в лог сообщения: выбранный режим запроса.
logging.info("Requests type: Selenium (JavaScript interpreter in Google Chrome)." if  Settings["selenium-mode"] == True else "Requests type: requests (Python library).")
# Приведение формата описательного файла к нижнему регистру.
Settings["format"] = Settings["format"].lower()
# Запись в лог сообщения: формат выходного файла.
logging.info("Output file format: \"" + Settings["format"] + "\".")
# Запись в лог сообщения: использование ID вместо алиаса.
logging.info("Using ID instead slug: ON." if Settings["use-id-instead-slug"] == True else "Using ID instead slug: OFF.")

#==========================================================================================#
# >>>>> НАСТРОЙКА ОБРАБОТЧИКА КОМАНД <<<<< #
#==========================================================================================#

# Список описаний обрабатываемых команд.
CommandsList = list()

# Создание команды: collect.
COM_collect = Command("collect")
COM_collect.addKeyPosition(["filters"], ArgumentType.All, Important = True)
COM_collect.addFlagPosition(["f"])
COM_collect.addFlagPosition(["s"])
CommandsList.append(COM_collect)

# Создание команды: convert.
COM_convert = Command("convert")
COM_convert.addArgument(ArgumentType.All, Important = True)
COM_convert.addArgument(ArgumentType.All, Important = True)
COM_convert.addArgument(ArgumentType.All, Important = True)
COM_convert.addFlagPosition(["s"])
CommandsList.append(COM_convert)

# Создание команды: getcov.
COM_getcov = Command("getcov")
COM_getcov.addArgument(ArgumentType.All, Important = True)
COM_getcov.addFlagPosition(["f"])
COM_getcov.addFlagPosition(["s"])
CommandsList.append(COM_getcov)

# Создание команды: manage.
COM_manage = Command("manage")
COM_manage.addArgument(ArgumentType.All, Important = True)
COM_manage.addFlagPosition(["del"], Important = True, LayoutIndex = 1)
COM_manage.addKeyPosition(["move"], ArgumentType.ValidPath, Important = True, LayoutIndex = 1)
COM_manage.addFlagPosition(["s"])
CommandsList.append(COM_manage)

# Создание команды: parse.
COM_parse = Command("parse")
COM_parse.addArgument(ArgumentType.All, Important = True, LayoutIndex = 1)
COM_parse.addFlagPosition(["collection"], LayoutIndex = 1)
COM_parse.addFlagPosition(["f"])
COM_parse.addFlagPosition(["s"])
CommandsList.append(COM_parse)

# Создание команды: proxval.
COM_proxval = Command("proxval")
COM_proxval.addFlagPosition(["f"])
COM_proxval.addFlagPosition(["s"])
CommandsList.append(COM_proxval)

# Создание команды: repair.
COM_repair = Command("repair")
COM_repair.addArgument(ArgumentType.All, Important = True)
COM_repair.addKeyPosition(["chapter"], ArgumentType.Number, Important = True)
COM_repair.addFlagPosition(["s"])
CommandsList.append(COM_repair)

# Создание команды: update.
COM_update = Command("update")
COM_update.addArgument(ArgumentType.All, LayoutIndex = 1)
COM_update.addFlagPosition(["local"], LayoutIndex = 1)
COM_update.addFlagPosition(["onlydesc"])
COM_update.addFlagPosition(["f"])
COM_update.addFlagPosition(["s"])
COM_update.addKeyPosition(["from"], ArgumentType.All)
CommandsList.append(COM_update)

# Инициализация обработчика консольных аргументов.
CAC = Terminalyzer()
# Получение информации о проверке команд.
CommandDataStruct = CAC.checkCommands(CommandsList)

# Если не удалось определить команду.
if CommandDataStruct == None:
	# Запись в лог критической ошибки: неверная команда.
	logging.critical("Unknown command.")
	# Завершение работы скрипта с кодом ошибки.
	exit(1)

#==========================================================================================#
# >>>>> ОБРАБОТКА ФЛАГОВ <<<<< #
#==========================================================================================#

# Активна ли опция выключения компьютера по завершении работы парсера.
IsShutdowAfterEnd = False
# Сообщение для внутренних функций: выключение ПК.
InFuncMessage_Shutdown = ""
# Активен ли режим перезаписи при парсинге.
IsForceModeActivated = False
# Сообщение для внутренних функций: режим перезаписи.
InFuncMessage_ForceMode = ""
# Очистка консоли.
Cls()

# Обработка флага: режим перезаписи.
if "f" in CommandDataStruct.Flags and CommandDataStruct.Name not in ["convert", "manage", "repair"]:
	# Включение режима перезаписи.
	IsForceModeActivated = True
	# Запись в лог сообщения: включён режим перезаписи.
	logging.info("Force mode: ON.")
	# Установка сообщения для внутренних функций.
	InFuncMessage_ForceMode = "Force mode: ON\n"

else:
	# Запись в лог сообщения об отключённом режиме перезаписи.
	logging.info("Force mode: OFF.")
	# Установка сообщения для внутренних функций.
	InFuncMessage_ForceMode = "Force mode: OFF\n"

# Обработка флага: выключение ПК после завершения работы скрипта.
if "s" in CommandDataStruct.Flags:
	# Включение режима.
	IsShutdowAfterEnd = True
	# Запись в лог сообщения о том, что ПК будет выключен после завершения работы.
	logging.info("Computer will be turned off after the script is finished!")
	# Установка сообщения для внутренних функций.
	InFuncMessage_Shutdown = "Computer will be turned off after the script is finished!\n"

#==========================================================================================#
# >>>>> ОБРАБОТКА КОММАНД <<<<< #
#==========================================================================================#

# Обработка команды: collect.
if "collect" == CommandDataStruct.Name:
	# Запись в лог сообщения: сбор списка тайтлов.
	logging.info("====== Collecting ======")
	# Инициализация сборщика.
	CollectorObject = Collector(Settings)
	# Название фильтра.
	FilterType = None
	# ID параметра фильтрации.
	FilterID = None
	# Сбор списка алиасов тайтлов, подходящих под фильтр.
	CollectorObject.collect(CommandDataStruct.Values["filters"], IsForceModeActivated)
	
# Обработка команды: convert.
if "convert" == CommandDataStruct.Name:
	# Запись в лог сообщения: конвертирование.
	logging.info("====== Converting ======")
	# Структура тайтла.
	Title = None
	# Имя файла тайтла.
	Filename = None	

	# Добавление расширения к файлу в случае отсутствия такового.
	if ".json" not in CommandDataStruct.Arguments[0]:
		Filename = CommandDataStruct.Arguments[0] + ".json"

	# Чтение тайтла.
	with open(Settings["titles-directory"] + Filename, encoding = "utf-8") as FileRead:
		# Декодирование файла.
		Title = json.load(FileRead)
		# Исходный формат.
		SourceFormat = None

		# Определение исходного формата.
		if CommandDataStruct.Arguments[1] == "-auto":

			# Если формат указан.
			if "format" in Title.keys():
				SourceFormat = Title["format"]

		else:
			SourceFormat = CommandDataStruct.Arguments[1]

		# Создание объекта форматирования.
		FormatterObject = Formatter(Settings, Title, Format = SourceFormat)
		# Конвертирование структуры тайтла.
		Title = FormatterObject.convert(CommandDataStruct.Arguments[2])

	# Сохранение переформатированного описательного файла.
	WriteJSON(Settings["titles-directory"] + Filename, Title)

# Обработка команды: getcov.
if "getcov" == CommandDataStruct.Name:
	# Запись в лог сообщения: заголовок парсинга.
	logging.info("====== Parsing ======")
	# Парсинг тайтла (без глав).
	LocalTitle = TitleParser(Settings, CommandDataStruct.Arguments[0], ForceMode = IsForceModeActivated, Message = InFuncMessage_Shutdown + InFuncMessage_ForceMode, Amending = False)
	# Сохранение локальных файлов тайтла.
	LocalTitle.downloadCovers()

# Обработка команды: manage.
if "manage" == CommandDataStruct.Name:
	# Запись в лог сообщения: заголовок менеджмента.
	logging.info("====== Management ======")
	
	# Вывод в консоль: идёт поиск тайтлов.
	print("Management...", end = "")
	# Менеджмент файлов с другим форматом.
	ManageOtherFormatsFiles(Settings, CommandDataStruct.Arguments[0], CommandDataStruct.Values["move"] if "move" in CommandDataStruct.Keys else None)
	# Вывод в консоль: процесс завершён.
	print("Done.")

# Обработка команды: parse.
if "parse" == CommandDataStruct.Name:
	# Запись в лог сообщения: парсинг.
	logging.info("====== Parsing ======")
	# Генерация сообщения.
	ExternalMessage = InFuncMessage_Shutdown
	
	# Если активирован флаг парсинга коллекций.
	if "collection" in CommandDataStruct.Flags:
		
		# Если существует файл коллекции.
		if os.path.exists("Collection.txt"):
			# Список тайтлов для парсинга.
			TitlesList = list()
			# Индекс обрабатываемого тайтла.
			CurrentTitleIndex = 0
			
			# Чтение содржимого файла.
			with open("Collection.txt", "r") as FileReader:
				# Буфер чтения.
				Bufer = FileReader.read().split('\n')
				
				# Поместить алиасы в список на парсинг, если строка не пуста.
				for Slug in Bufer:
					if Slug.strip() != "":
						TitlesList.append(Slug)

			# Запись в лог сообщения: количество тайтлов в коллекции.
			logging.info("Titles count in collection: " + str(len(TitlesList)) + ".")
			
			# Спарсить каждый тайтл.
			for Slug in TitlesList:
				# Инкремент текущего индекса.
				CurrentTitleIndex += 1
				# Генерация сообщения.
				ExternalMessage = InFuncMessage_Shutdown + InFuncMessage_ForceMode + "Parsing titles: " + str(CurrentTitleIndex) + " / " + str(len(TitlesList)) + "\n"
				# Парсинг тайтла.
				LocalTitle = TitleParser(Settings, Slug, ForceMode = IsForceModeActivated, Message = ExternalMessage)
				# Сохранение локальных файлов тайтла.
				LocalTitle.save()

		else:
			# Запись в лог критической ошибки: отсутствует файл коллекций.
			logging.critical("Unable to find collection file.")
			# Выброс исключения.
			raise FileNotFoundError("Collection.txt")
	
	else:
		# Парсинг тайтла.
		LocalTitle = TitleParser(Settings, CommandDataStruct.Arguments[0], ForceMode = IsForceModeActivated, Message = ExternalMessage)
		# Сохранение локальных файлов тайтла.
		LocalTitle.save()

# Обработка команды: proxval.
if "proxval" == CommandDataStruct.Name:
	# Запись в лог сообщения: валидация.
	logging.info("====== Validation ======")
	# Инициализация менеджера прокси.
	RequestsManagerObject = RequestsManager(Settings, True)
	# Список всех прокси.
	ProxiesList = RequestsManagerObject.getProxies()
	# Сообщение о валидации прокси.
	Message = "Proxies.json updated.\n\n" if IsForceModeActivated == True else ""
	
	# Если указаны прокси.
	if len(ProxiesList) > 0:
		
		# Для каждого прокси провести валидацию.
		for ProxyIndex in range(0, len(ProxiesList)):
			# Вывод результата.
			print(ProxiesList[ProxyIndex], "status code:", RequestsManagerObject.validateProxy(ProxiesList[ProxyIndex], IsForceModeActivated))

			# Выжидание интервала.
			if ProxyIndex < len(ProxiesList) - 1:
				Wait(Settings)
		
	else:
		# Вывод в консоль: файл определений не содержит прокси.
		print("Proxies are missing.")
		# Запись в лог предупреждения: файл определений не содержит прокси.
		logging.warning("Proxies are missing.")
		
	# Вывод в терминал сообщения о завершении работы.
	print(f"\nStatus codes:\n0 – valid\n1 – invalid\n2 – forbidden\n3 – server error (502 Bad Gateway for example)\n\n{Message}Press ENTER to exit...")
	# Закрытие менеджера.
	RequestsManagerObject.close()
	# Пауза.
	input()
	
# Обработка команды: repair.
if "repair" == CommandDataStruct.Name:
	# Запись в лог сообщения: восстановление.
	logging.info("====== Repairing ======")
	# Алиас тайтла.
	TitleSlug = None
	# Название файла тайтла с расширением.
	Filename = (CommandDataStruct.Arguments[0] + ".json") if ".json" not in CommandDataStruct.Arguments[0] else CommandDataStruct.Arguments[0]
	# Чтение тайтла.
	TitleContent = ReadJSON(Settings["titles-directory"] + Filename)
	# Генерация сообщения.
	ExternalMessage = InFuncMessage_Shutdown
	# Вывод в консоль: идёт процесс восстановления главы.
	print("Repairing chapter...")
	
	# Если ключём алиаса является slug, то получить алиас.
	if "slug" in TitleContent.keys():
		TitleSlug = TitleContent["slug"]
		
	else:
		TitleSlug = TitleContent["dir"]

	# Парсинг тайтла.
	LocalTitle = TitleParser(Settings, TitleSlug, ForceMode = False, Message = ExternalMessage, Amending = False)
	
	# Если указано, восстановить главу.
	if "chapter" in CommandDataStruct.Keys:
		LocalTitle.repairChapter(CommandDataStruct.Values["chapter"])
	
	# Сохранение локальных файлов тайтла.
	LocalTitle.save(DownloadCovers = False)

# Обработка команды: update.
if "update" == CommandDataStruct.Name:
	# Запись в лог сообщения: получение списка обновлений.
	logging.info("====== Updating ======")
	# Алиасы обновляемых тайтлов.
	TitlesSlugs = list()
	# Индекс обрабатываемого тайтла.
	CurrentTitleIndex = 0
	# Запись в лог сообщения: режим обновления.
	logging.info("Update only description: " + "ON." if "onlydesc" in CommandDataStruct.Flags else "OFF.")
		
	# Обновить все локальные файлы.
	if "local" in CommandDataStruct.Flags:
		# Вывод в консоль: идёт поиск тайтлов.
		print("Scanning titles...")
		# Получение списка файлов в директории.
		TitlesList = os.listdir(Settings["titles-directory"])
		# Фильтрация только файлов формата JSON.
		TitlesList = list(filter(lambda x: x.endswith(".json"), TitlesList))
		# Алиас стартового тайтла.
		FromTitle = None

		# Если активирован ключ, указывающий стартовый тайтл.
		if "from" in CommandDataStruct.Keys:
			FromTitle = CommandDataStruct.Values["from"]
			
		# Чтение всех алиасов из локальных файлов.
		for File in TitlesList:
			# Открытие локального описательного файла JSON.
			with open(Settings["titles-directory"] + File, encoding = "utf-8") as FileRead:
				# JSON файл тайтла.
				LocalTitle = json.load(FileRead)

				# Помещение алиаса в список.
				if "slug" in LocalTitle.keys():
					TitlesSlugs.append(str(LocalTitle["slug"]))
				elif "dir" in LocalTitle.keys():
					TitlesSlugs.append(str(LocalTitle["dir"]))

		# Запись в лог сообщения: количество доступных для обновления тайтлов.
		logging.info("Local titles to update: " + str(len(TitlesList)) + ".")

		# Старт с указанного тайтла.
		if FromTitle is not None:
			# Запись в лог сообщения: стартовый тайтл обновления.
			logging.info("Updating starts from title with slug: \"" + FromTitle + "\".")
			# Буферный список тайтлов.
			BuferTitleSlugs = list()
			# Состояние: записывать ли тайтлы.
			IsWriteSlugs = False
				
			# Перебор тайтлов.
			for Slug in TitlesSlugs:
					
				# Если обнаружен стартовый тайтл, то включить запись тайтлов в новый список обновлений.
				if Slug == FromTitle:
					IsWriteSlugs = True
						
				# Добавить алиас в список обновляемых тайтлов.
				if IsWriteSlugs is True:
					BuferTitleSlugs.append(Slug)

			# Перезапись списка обновляемых тайтлов.
			TitlesSlugs = BuferTitleSlugs

	# Обновить изменённые на сервере за последнее время тайтлы.
	else:
		# Инициализация проверки обновлений.
		UpdateChecker = Updater(Settings)
		# Получение списка обновлённых тайтлов.
		TitlesSlugs = UpdateChecker.getUpdatesList()

	# Запись в лог сообщения: заголовог парсинга.
	logging.info("====== Parsing ======")

	# Парсинг обновлённых тайтлов.
	for Slug in TitlesSlugs:
		# Инкремент текущего индекса.
		CurrentTitleIndex += 1
		# Очистка терминала.
		Cls()
		# Вывод в терминал прогресса.
		print("Updating titles: " + str(len(TitlesList) - len(TitlesSlugs) + CurrentTitleIndex) + " / " + str(len(TitlesList)))
		# Генерация сообщения.
		ExternalMessage = InFuncMessage_Shutdown + InFuncMessage_ForceMode + "Updating titles: " + str(len(TitlesList) - len(TitlesSlugs) + CurrentTitleIndex) + " / " + str(len(TitlesList)) + "\n"
		# Локальный описательный файл.
		LocalTitle = None
			
		# Если включено обновление только описания.
		if "onlydesc" in CommandDataStruct.Flags:
			# Парсинг тайтла (без глав).
			LocalTitle = TitleParser(Settings, Slug.replace(".json", ""), ForceMode = IsForceModeActivated, Message = ExternalMessage, Amending = False)
				
		else:
			# Парсинг тайтла.
			LocalTitle = TitleParser(Settings, Slug.replace(".json", ""), ForceMode = IsForceModeActivated, Message = ExternalMessage)
				
		# Сохранение локальных файлов тайтла.
		LocalTitle.save()

		# Выжидание указанного интервала, если не все тайтлы обновлены.
		if CurrentTitleIndex < len(TitlesSlugs):
			Wait(Settings)

#==========================================================================================#
# >>>>> ЗАВЕРШЕНИЕ РАБОТЫ СКРИПТА <<<<< #
#==========================================================================================#

# Запись в лог сообщения: заголовок завершения работы скрипта.
logging.info("====== Exiting ======")
# Очистка консоли.
Cls()
# Время завершения работы скрипта.
EndTime = time.time()
# Запись времени завершения работы скрипта.
logging.info("Script finished. Execution time: " + SecondsToTimeString(EndTime - StartTime) + ".")

# Выключение ПК, если установлен соответствующий флаг.
if IsShutdowAfterEnd == True:
	# Запись в лог сообщения о немедленном выключении ПК.
	logging.info("Turning off the computer.")
	# Выключение ПК.
	Shutdown()

# Выключение логгирования.
logging.shutdown()