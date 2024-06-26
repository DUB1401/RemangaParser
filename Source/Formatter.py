from PIL import Image, UnidentifiedImageError
from dublib.Polyglot import HTML

import logging
import os
import re

# Исключение: использован устаревший формат.
class DeprecatedFormat(Exception):

	# Конструктор: вызывается при обработке исключения.
	def __init__(self, Format: str | None, Version: str):
		# Название парсера.
		Parser = "RemangaParser"
		# Добавление данных в сообщение об ошибке.
		self.__Message = f"Format \"{Format}\" is depreacted. Use {Parser} v{Version}."
		# Обеспечение доступа к оригиналу наследованного свойства.
		super().__init__(self.__Message) 
			
	# Преобразователь: представляет содержимое класса как строку.
	def __str__(self):
		return self.__Message

# Исключение: не существует подходящего конвертера для указанных форматов.
class UnableToConvert(Exception):

	# Конструктор: вызывается при обработке исключения.
	def __init__(self, SourceFormat: str, TargetFormat: str): 
		# Добавление данных в сообщение об ошибке.
		self.__Message = "There isn't suitable converter for these formats: \"" + SourceFormat + "\" > \"" + TargetFormat + "\"."
		# Обеспечение доступа к оригиналу наследованного свойства.
		super().__init__(self.__Message)
			
	# Преобразователь: представляет содержимое класса как строку.
	def __str__(self):
		return self.__Message

# Исключение: указан неизвестный формат.
class UnknownFormat(Exception):

	# Конструктор: вызывается при обработке исключения.
	def __init__(self, UnknownFormat: str | None): 
		# Добавление данных в сообщение об ошибке.
		self.__Message = "Couldn't recognize source or target format: \"" + str(UnknownFormat) + "\"."
		# Обеспечение доступа к оригиналу наследованного свойства.
		super().__init__(self.__Message) 
			
	# Преобразователь: представляет содержимое класса как строку.
	def __str__(self):
		return self.__Message

# Форматировщик структур описательных файлов тайтлов.
class Formatter:

	#==========================================================================================#
	# >>>>> КОНВЕРТЕРЫ <<<<< #
	#==========================================================================================#

	# Конвертер: DMP-V1 > RN-V1.
	def __DMP1_to_RN1(self) -> dict:
		# Перечисление типов тайтла.
		Types = ["Манга", "Манхва", "Маньхуа", "Западный комикс", "Рукомикс", "Индонезийский комикс", "Другое", "Другое"]
		# Перечисление типов тайтла DMP-V1.
		DMP1_Types = ["MANGA", "MANHWA", "MANHUA", "WESTERN_COMIC", "RUS_COMIC", "INDONESIAN_COMIC", "OEL", "UNKNOWN"]
		# Перечисление статусов.
		RN1_Statuses = ["Закончен", "Продолжается", "Заморожен", "Нет переводчика", "Анонс", "Лицензировано"]
		# Буфер обработки возвращаемой структуры.
		FormattedTitle = dict()

		#---> Генерация структуры.
		#==========================================================================================#
		FormattedTitle["format"] = "rn-v1"
		FormattedTitle["site"] = self.__OriginalTitle["site"]
		FormattedTitle["id"] = self.__OriginalTitle["id"]
		FormattedTitle["img"] = {"high": "", "mid": "", "low": ""}
		FormattedTitle["en_name"] = self.__OriginalTitle["en-name"]
		FormattedTitle["rus_name"] = self.__OriginalTitle["ru-name"]
		FormattedTitle["another_name"] = " / ".join(self.__OriginalTitle["another-names"])
		FormattedTitle["dir"] = self.__OriginalTitle["slug"]
		FormattedTitle["description"] = self.__OriginalTitle["description"]
		FormattedTitle["issue_year"] = self.__OriginalTitle["publication-year"]
		FormattedTitle["avg_rating"] = None
		FormattedTitle["admin_rating"] = None
		FormattedTitle["count_rating"] = None
		FormattedTitle["age_limit"] = self.__OriginalTitle["age-rating"]
		FormattedTitle["status"] = dict()
		FormattedTitle["status"]["id"] = None
		FormattedTitle["status"]["name"] = None
		FormattedTitle["count_bookmarks"] = 0
		FormattedTitle["total_votes"] = 0
		FormattedTitle["total_views"] = 0
		FormattedTitle["type"] = dict()
		FormattedTitle["type"]["id"] = DMP1_Types.index(self.__OriginalTitle["type"])
		FormattedTitle["type"]["name"] = Types[DMP1_Types.index(self.__OriginalTitle["type"])]
		FormattedTitle["genres"] = list()
		FormattedTitle["categories"] = list()
		FormattedTitle["bookmark_type"] = None
		FormattedTitle["branches"] = list()
		FormattedTitle["count_chapters"] = 0
		FormattedTitle["first_chapter"] = dict()
		FormattedTitle["first_chapter"]["id"] = 0
		FormattedTitle["first_chapter"]["tome"] = 0
		FormattedTitle["first_chapter"]["chapter"] = str()
		FormattedTitle["continue_reading"] = None
		FormattedTitle["is_licensed"] = self.__OriginalTitle["is-licensed"]
		FormattedTitle["newlate_id"] = None
		FormattedTitle["newlate_title"] = None
		FormattedTitle["related"] = None
		FormattedTitle["uploaded"] = 0
		FormattedTitle["can_post_comments"] = True
		FormattedTitle["adaptation"] = None
		FormattedTitle["publishers"] = list()
		FormattedTitle["is_yaoi"] = False
		FormattedTitle["is_erotic"] = False
		FormattedTitle["chapters"] = dict()

		#---> Внесение правок.
		#==========================================================================================#

		# Переконвертирование обложек.
		for CoverIndex in range(0, len(self.__OriginalTitle["covers"])):
			# Ключи обложек.
			ImgKeys = ["high", "mid", "low"]

			# Поместить до трёх обложек в новый контейнер.
			if CoverIndex < 3:
				FormattedTitle["img"][ImgKeys[CoverIndex]] = self.__OriginalTitle["covers"][CoverIndex]["link"].replace("https://remanga.org", "")

		# Формирование структуры статуса.
		if self.__OriginalTitle["status"] == "ONGOING":
			FormattedTitle["status"]["id"] = 1
			FormattedTitle["status"]["name"] = RN1_Statuses[1]
		elif self.__OriginalTitle["status"] == "ABANDONED":
			FormattedTitle["status"]["id"] = 2
			FormattedTitle["status"]["name"] = RN1_Statuses[2]
		elif self.__OriginalTitle["status"] == "COMPLETED":
			FormattedTitle["status"]["id"] = 0
			FormattedTitle["status"]["name"] = RN1_Statuses[0]
		else:
			FormattedTitle["status"]["id"] = 6
			FormattedTitle["status"]["name"] = "Неизвестный статус"

		# Конвертирование ветвей и подсчёт количества глав.
		for Branch in self.__OriginalTitle["branches"]:
			BuferBranch = dict()
			BuferBranch["id"] = Branch["id"]
			BuferBranch["img"] = str()
			BuferBranch["subscribed"] = False
			BuferBranch["total_votes"] = 0
			BuferBranch["count_chapters"] = Branch["chapters-count"]
			BuferBranch["publishers"] = list()
			FormattedTitle["branches"].append(BuferBranch)
			FormattedTitle["count_chapters"] += Branch["chapters-count"]

		# Формирование структуры первой главы.
		BranchList = list(self.__OriginalTitle["chapters"].keys())
		if len(BranchList) > 0 and len(self.__OriginalTitle["chapters"][BranchList[0]]) > 0:
			FormattedTitle["first_chapter"]["id"] = self.__OriginalTitle["chapters"][BranchList[0]][0]["id"]
			FormattedTitle["first_chapter"]["tome"] = self.__OriginalTitle["chapters"][BranchList[0]][0]["volume"]
			FormattedTitle["first_chapter"]["chapter"] = str(self.__OriginalTitle["chapters"][BranchList[0]][0]["number"])

		# Определение значений полей is_yaoi и is_erotic.
		if "Яой" in self.__OriginalTitle["genres"]:
			FormattedTitle["is_yaoi"] = True
		if "Эротика" in self.__OriginalTitle["genres"]:
			FormattedTitle["is_erotic"] = True

		# Форматирование ветвей.
		for BranchID in BranchList:
			# Создание списка для глав.
			FormattedTitle["chapters"][BranchID] = list()

			# Форматирование отдельных глав.
			for ChapterIndex in range(0, len(self.__OriginalTitle["chapters"][BranchID])):

				BuferChapter = dict()
				BuferChapter["id"] = self.__OriginalTitle["chapters"][BranchID][ChapterIndex]["id"]
				BuferChapter["rated"] = None
				BuferChapter["viewed"] = None
				BuferChapter["is_bought"] = None
				BuferChapter["publishers"] = list()
				BuferChapter["index"] = ChapterIndex + 1
				BuferChapter["tome"] = self.__OriginalTitle["chapters"][BranchID][ChapterIndex]["volume"]
				BuferChapter["chapter"] = self.__OriginalTitle["chapters"][BranchID][ChapterIndex]["number"]
				BuferChapter["name"] = self.__OriginalTitle["chapters"][BranchID][ChapterIndex]["name"]
				BuferChapter["price"] = None
				BuferChapter["score"] = 0
				BuferChapter["upload_date"] = str()
				BuferChapter["pub_date"] = None
				BuferChapter["is_paid"] = self.__OriginalTitle["chapters"][BranchID][ChapterIndex]["is-paid"]
				BuferChapter["slides"] = list()

				# Переформатирование переводчиков.
				if self.__OriginalTitle["chapters"][BranchID][ChapterIndex]["translator"] is not None:
					BuferPublisher = dict()
					BuferPublisher["name"] = self.__OriginalTitle["chapters"][BranchID][ChapterIndex]["translator"]
					BuferPublisher["dir"] = str()
					BuferPublisher["type"] = 1
					BuferChapter["publishers"].append(BuferPublisher)

				# Переформатирование слайдов.
				for Slide in self.__OriginalTitle["chapters"][BranchID][ChapterIndex]["slides"]:
					BuferSlide = dict()
					BuferSlide["id"] = 0
					BuferSlide["link"] = Slide["link"]
					BuferSlide["page"] = Slide["index"] + 1
					BuferSlide["height"] = Slide["height"]
					BuferSlide["width"] = Slide["width"]
					BuferSlide["count_comments"] = 0
					BuferChapter["slides"].append(BuferSlide)

				# Помещение главы в ветвь.
				FormattedTitle["chapters"][BranchID].append(BuferChapter)

		# Конвертирование тегов.
		for TagIndex in range(0, len(self.__OriginalTitle["tags"])):
			FormattedTitle["categories"].append({"id": 0, "name": self.__OriginalTitle["tags"][TagIndex].capitalize()})

		# Конвертирование жанров.
		for GenreIndex in range(0, len(self.__OriginalTitle["genres"])):
			FormattedTitle["genres"].append({"id": 0, "name": self.__OriginalTitle["genres"][GenreIndex].capitalize()})

		return FormattedTitle

	# Конвертер: RN-V1 > DMP-V1.
	def __RN1_to_DMP1(self) -> dict:
		# Перечисление типов тайтла.
		Types = ["MANGA", "MANHWA", "MANHUA", "WESTERN_COMIC", "RUS_COMIC", "INDONESIAN_COMIC", "OEL", "UNKNOWN"]
		# Перечисление статусов.
		Statuses = ["ANNOUNCED", "ONGOING", "ABANDONED", "COMPLETED", "UNKNOWN"]
		# Буфер обработки возвращаемой структуры.
		FormattedTitle = dict()

		#---> Вложенные функции.
		#==========================================================================================#

		# Определяет тип тайтла.
		def IdentifyTitleType(TypeDetermination) -> str:
			# Тип тайтла.
			Type = None

			# Перебор типов тайтла.
			if type(TypeDetermination) is dict and "name" in TypeDetermination.keys():
				if TypeDetermination["name"] in ["Манга"]:
					Type = "MANGA"
				elif TypeDetermination["name"] in ["Манхва"]:
					Type = "MANHWA"
				elif TypeDetermination["name"] in ["Маньхуа"]:
					Type = "MANHUA"
				elif TypeDetermination["name"] in ["Западный комикс"]:
					Type = "WESTERN_COMIC"
				elif TypeDetermination["name"] in ["Рукомикс", "Руманга"]:
					Type = "RUS_COMIC"
				elif TypeDetermination["name"] in ["Индонезийский комикс"]:
					Type = "INDONESIAN_COMIC"
				elif TypeDetermination["name"] in ["OEL-манга"]:
					Type = "OEL"
				else:
					Type = "UNKNOWN"

			else:
				pass

			return Type

		# Определяет статус тайтла.
		def IdentifyTitleStatus(TitleStatusDetermination) -> str:
			# Тип тайтла.
			Status = None

			# Перебор типов тайтла.
			if type(TitleStatusDetermination) is dict and "name" in TitleStatusDetermination.keys():
				if TitleStatusDetermination["name"] in ["Анонс"]:
					Status = "ANNOUNCED"
				elif TitleStatusDetermination["name"] in ["Продолжается"]:
					Status = "ONGOING"
				elif TitleStatusDetermination["name"] in ["Закончен"]:
					Status = "COMPLETED"
				elif TitleStatusDetermination["name"] in ["Заморожен", "Нет переводчика", "Лицензировано"]:
					Status = "ABANDONED"
				else:
					Status = "UNKNOWN"

			else:
				pass

			return Status
		
		#---> Генерация структуры.
		#==========================================================================================#
		FormattedTitle["format"] = "dmp-v1"
		FormattedTitle["site"] = "remanga.org"
		FormattedTitle["id"] = self.__OriginalTitle["id"]
		FormattedTitle["slug"] = self.__OriginalTitle["dir"]
		FormattedTitle["covers"] = list()
		FormattedTitle["ru-name"] = self.__OriginalTitle["rus_name"]
		FormattedTitle["en-name"] = self.__OriginalTitle["en_name"]
		FormattedTitle["another-names"] = self.__OriginalTitle["another_name"].split(" / ")
		FormattedTitle["author"] = None
		FormattedTitle["publication-year"] = self.__OriginalTitle["issue_year"]
		FormattedTitle["age-rating"] = self.__OriginalTitle["age_limit"]
		FormattedTitle["description"] = HTML(self.__OriginalTitle["description"]).plain_text.replace("\r\n\r\n", "\n")
		FormattedTitle["type"] = IdentifyTitleType(self.__OriginalTitle["type"])
		FormattedTitle["status"] = IdentifyTitleStatus(self.__OriginalTitle["status"])
		FormattedTitle["is-licensed"] = self.__OriginalTitle["is_licensed"]
		FormattedTitle["series"] = list()
		FormattedTitle["genres"] = list()
		FormattedTitle["tags"] = list()
		FormattedTitle["branches"] = list()
		FormattedTitle["chapters"] = dict()

		#---> Внесение правок.
		#==========================================================================================#

		# Конвертирование обложек.
		for CoverType in self.__OriginalTitle["img"].keys():
			
			# Если есть данные об обложке.
			if self.__OriginalTitle["img"][CoverType] != "":
				FormattedTitle["covers"].append({"link": "https://remanga.org" + self.__OriginalTitle["img"][CoverType], "filename": self.__OriginalTitle["img"][CoverType].split('/')[-1], "width": None, "height": None})

		# Конвертирование ветвей.
		for OriginalBranch in self.__OriginalTitle["branches"]:
			# Буфер текущей ветви.
			CurrentBranch = dict()
			# Перенос данных.
			CurrentBranch["id"] = OriginalBranch["id"]
			CurrentBranch["chapters-count"] = OriginalBranch["count_chapters"]
			# Сохранение результата.
			FormattedTitle["branches"].append(CurrentBranch)

		# Конвертирование глав.
		for CurrentBranchID in self.__OriginalTitle["chapters"].keys():
			# Буфер текущей ветви.
			CurrentBranch = list()

			# Конвертирование глав.
			for Chapter in self.__OriginalTitle["chapters"][CurrentBranchID]:
				# Буфер текущей главы.
				CurrentChapter = dict()
				# Счётчик слайдов.
				SlideIndex = 0
				# Перенос данных.
				CurrentChapter["id"] = Chapter["id"]
				CurrentChapter["volume"] = Chapter["tome"]
				CurrentChapter["number"] = None
				CurrentChapter["name"] = Chapter["name"]
				CurrentChapter["is-paid"] = Chapter["is_paid"]
				CurrentChapter["translator"] = ""
				CurrentChapter["slides"] = list()

				# Если у главы нет названия, то обнулить его.
				if CurrentChapter["name"] == "":
					CurrentChapter["name"] = None

				# Перенос номера главы c конвертированием.
				if '.' in str(Chapter["chapter"]):
					CurrentChapter["number"] = float(re.search(r"\d+(\.\d+)?", str(Chapter["chapter"])).group(0))
				else:
					CurrentChapter["number"] = int(re.search(r"\d+(\.\d+)?", str(Chapter["chapter"])).group(0))

				# Перенос переводчиков.
				for Publisher in Chapter["publishers"]:
					CurrentChapter["translator"] += Publisher["name"] + " / "

				# Перенос слайдов.
				for Slide in Chapter["slides"]:
					# Инкремент индекса слайда.
					SlideIndex += 1
					# Буфер текущего слайда.
					CurrentSlide = dict()
					# Перенос данных.
					CurrentSlide["index"] = SlideIndex
					CurrentSlide["link"] = Slide["link"]
					CurrentSlide["width"] = Slide["width"]
					CurrentSlide["height"] = Slide["height"]
					# Сохранение результата.
					CurrentChapter["slides"].append(CurrentSlide)

				# Удаление запятой из конца поля переводчика или обнуление поля.
				if CurrentChapter["translator"] != "":
					CurrentChapter["translator"] = CurrentChapter["translator"][:-3]
				else:
					CurrentChapter["translator"] = None

				# Сохранение результата.
				CurrentBranch.append(CurrentChapter)

			# Сохранение результата.
			FormattedTitle["chapters"][CurrentBranchID] = CurrentBranch

		# Вычисление размера локальных обложек.
		for CoverIndex in range(0, len(FormattedTitle["covers"])):
			# Буфер изображения.
			CoverImage = None

			try:

				# Поиск локальных файлов обложек c ID в названии.
				if self.__Settings["use-id-instead-slug"] is True and os.path.exists(self.__Settings["covers-directory"] + str(FormattedTitle["id"]) + "/" + FormattedTitle["covers"][CoverIndex]["filename"]):
					CoverImage = Image.open(self.__Settings["covers-directory"] + str(FormattedTitle["id"]) + "/" + FormattedTitle["covers"][CoverIndex]["filename"])

				# Поиск локальных файлов обложек c алиасом в названии.
				elif self.__Settings["use-id-instead-slug"] is False and os.path.exists(self.__Settings["covers-directory"] + FormattedTitle["slug"] + "/" + FormattedTitle["covers"][CoverIndex]["filename"]):
					CoverImage = Image.open(self.__Settings["covers-directory"] + FormattedTitle["slug"] + "/" + FormattedTitle["covers"][CoverIndex]["filename"])

			except UnidentifiedImageError:
				# Запись в лог ошибки: неизвестная ошибка при чтении изображения.
				logging.error("Resolution of the cover couldn't be determined.")

			# Получение размеров.
			if CoverImage is not None:
				FormattedTitle["covers"][CoverIndex]["width"], FormattedTitle["covers"][CoverIndex]["height"] = CoverImage.size

		# Конвертирование тегов.
		for TagIndex in range(0, len(self.__OriginalTitle["categories"])):
			FormattedTitle["tags"].append(self.__OriginalTitle["categories"][TagIndex]["name"].lower())

		# Конвертирование жанров.
		for GenreIndex in range(0, len(self.__OriginalTitle["genres"])):
			FormattedTitle["genres"].append(self.__OriginalTitle["genres"][GenreIndex]["name"].lower())

		# Сортировка глав по возрастанию.
		for BranchID in FormattedTitle["chapters"].keys():
			FormattedTitle["chapters"][BranchID] = sorted(FormattedTitle["chapters"][BranchID], key = lambda Value: (Value["volume"], Value["number"])) 

		return FormattedTitle
	
	# Конвертер: RN-V1 > RN-V2.
	def __RN1_to_RN2(self) -> dict:
		# Буфер обработки возвращаемой структуры.
		FormattedTitle = dict()

		#---> Вложенные функции.
		#==========================================================================================#

		# Определяет тип тайтла.
		def IdentifyTitleType(TypeDetermination) -> str:
			# Тип тайтла.
			Type = None

			# Перебор типов тайтла.
			if type(TypeDetermination) is dict and "name" in TypeDetermination.keys():
				if TypeDetermination["name"] in ["Манга"]:
					Type = "MANGA"
				elif TypeDetermination["name"] in ["Манхва"]:
					Type = "MANHWA"
				elif TypeDetermination["name"] in ["Маньхуа"]:
					Type = "MANHUA"
				elif TypeDetermination["name"] in ["Западный комикс"]:
					Type = "WESTERN_COMIC"
				elif TypeDetermination["name"] in ["Рукомикс", "Руманга"]:
					Type = "RUS_COMIC"
				elif TypeDetermination["name"] in ["Индонезийский комикс"]:
					Type = "INDONESIAN_COMIC"
				elif TypeDetermination["name"] in ["OEL-манга"]:
					Type = "OEL"
				else:
					Type = "UNKNOWN"

			else:
				pass

			return Type

		# Определяет статус тайтла.
		def IdentifyTitleStatus(TitleStatusDetermination) -> str:
			# Тип тайтла.
			Status = None

			# Перебор типов тайтла.
			if type(TitleStatusDetermination) is dict and "name" in TitleStatusDetermination.keys():
				if TitleStatusDetermination["name"] in ["Анонс"]:
					Status = "ANNOUNCED"
				elif TitleStatusDetermination["name"] in ["Продолжается"]:
					Status = "ONGOING"
				elif TitleStatusDetermination["name"] in ["Закончен"]:
					Status = "COMPLETED"
				elif TitleStatusDetermination["name"] in ["Заморожен", "Нет переводчика", "Лицензировано"]:
					Status = "ABANDONED"
				else:
					Status = "UNKNOWN"

			else:
				pass

			return Status
		
		#---> Генерация структуры.
		#==========================================================================================#
		FormattedTitle["format"] = "rn-v2"
		FormattedTitle["site"] = "remanga.org"
		FormattedTitle["id"] = self.__OriginalTitle["id"]
		FormattedTitle["slug"] = self.__OriginalTitle["dir"]
		FormattedTitle["covers"] = list()
		FormattedTitle["ru-name"] = self.__OriginalTitle["rus_name"]
		FormattedTitle["en-name"] = self.__OriginalTitle["en_name"]
		FormattedTitle["another-names"] = self.__OriginalTitle["another_name"].split(" / ")
		FormattedTitle["author"] = None
		FormattedTitle["publication-year"] = self.__OriginalTitle["issue_year"]
		FormattedTitle["age-rating"] = self.__OriginalTitle["age_limit"]
		FormattedTitle["description"] = HTML(self.__OriginalTitle["description"]).plain_text.replace("\r\n\r\n", "\n") if self.__OriginalTitle["description"] else ""
		FormattedTitle["type"] = IdentifyTitleType(self.__OriginalTitle["type"])
		FormattedTitle["status"] = IdentifyTitleStatus(self.__OriginalTitle["status"])
		FormattedTitle["is-licensed"] = self.__OriginalTitle["is_licensed"]
		FormattedTitle["series"] = list()
		FormattedTitle["genres"] = list()
		FormattedTitle["tags"] = list()
		FormattedTitle["branches"] = list()
		FormattedTitle["chapters"] = dict()

		#---> Внесение правок.
		#==========================================================================================#

		# Конвертирование обложек.
		for CoverType in self.__OriginalTitle["img"].keys():
			
			# Если есть данные об обложке.
			if self.__OriginalTitle["img"][CoverType] != "":
				FormattedTitle["covers"].append({"link": "https://remanga.org" + self.__OriginalTitle["img"][CoverType], "filename": self.__OriginalTitle["img"][CoverType].split('/')[-1], "width": None, "height": None})

		# Конвертирование ветвей.
		for OriginalBranch in self.__OriginalTitle["branches"]:
			# Буфер текущей ветви.
			CurrentBranch = dict()
			# Перенос данных.
			CurrentBranch["id"] = OriginalBranch["id"]
			CurrentBranch["chapters-count"] = OriginalBranch["count_chapters"]
			# Сохранение результата.
			FormattedTitle["branches"].append(CurrentBranch)

		# Конвертирование глав.
		for CurrentBranchID in self.__OriginalTitle["chapters"].keys():
			# Буфер текущей ветви.
			CurrentBranch = list()

			# Конвертирование глав.
			for Chapter in self.__OriginalTitle["chapters"][CurrentBranchID]:
				# Буфер текущей главы.
				CurrentChapter = dict()
				# Счётчик слайдов.
				SlideIndex = 0
				# Перенос данных.
				CurrentChapter["id"] = Chapter["id"]
				CurrentChapter["volume"] = Chapter["tome"]
				CurrentChapter["number"] = None
				CurrentChapter["name"] = Chapter["name"]
				CurrentChapter["is-paid"] = Chapter["is_paid"]
				CurrentChapter["free-publication-date"] = Chapter["pub_date"] if CurrentChapter["is-paid"] == True else None
				CurrentChapter["translator"] = ""
				CurrentChapter["slides"] = list()

				# Если у главы нет названия, то обнулить его.
				if CurrentChapter["name"] == "":
					CurrentChapter["name"] = None

				# Перенос номера главы c конвертированием.
				if '.' in str(Chapter["chapter"]):
					CurrentChapter["number"] = float(re.search(r"\d+(\.\d+)?", str(Chapter["chapter"])).group(0))
				else:
					CurrentChapter["number"] = int(re.search(r"\d+(\.\d+)?", str(Chapter["chapter"])).group(0))

				# Перенос переводчиков.
				for Publisher in Chapter["publishers"]:
					CurrentChapter["translator"] += Publisher["name"] + " / "

				# Перенос слайдов.
				for Slide in Chapter["slides"]:
					# Инкремент индекса слайда.
					SlideIndex += 1
					# Буфер текущего слайда.
					CurrentSlide = dict()
					# Перенос данных.
					CurrentSlide["index"] = SlideIndex
					CurrentSlide["link"] = Slide["link"]
					CurrentSlide["width"] = Slide["width"]
					CurrentSlide["height"] = Slide["height"]
					# Сохранение результата.
					CurrentChapter["slides"].append(CurrentSlide)

				# Удаление запятой из конца поля переводчика или обнуление поля.
				if CurrentChapter["translator"] != "":
					CurrentChapter["translator"] = CurrentChapter["translator"][:-3]
				else:
					CurrentChapter["translator"] = None

				# Сохранение результата.
				CurrentBranch.append(CurrentChapter)

			# Сохранение результата.
			FormattedTitle["chapters"][CurrentBranchID] = CurrentBranch

		# Вычисление размера локальных обложек.
		for CoverIndex in range(0, len(FormattedTitle["covers"])):
			# Буфер изображения.
			CoverImage = None

			try:

				# Поиск локальных файлов обложек c ID в названии.
				if self.__Settings["use-id-instead-slug"] is True and os.path.exists(self.__Settings["covers-directory"] + str(FormattedTitle["id"]) + "/" + FormattedTitle["covers"][CoverIndex]["filename"]):
					CoverImage = Image.open(self.__Settings["covers-directory"] + str(FormattedTitle["id"]) + "/" + FormattedTitle["covers"][CoverIndex]["filename"])

				# Поиск локальных файлов обложек c алиасом в названии.
				elif self.__Settings["use-id-instead-slug"] is False and os.path.exists(self.__Settings["covers-directory"] + FormattedTitle["slug"] + "/" + FormattedTitle["covers"][CoverIndex]["filename"]):
					CoverImage = Image.open(self.__Settings["covers-directory"] + FormattedTitle["slug"] + "/" + FormattedTitle["covers"][CoverIndex]["filename"])

			except UnidentifiedImageError:
				# Запись в лог ошибки: неизвестная ошибка при чтении изображения.
				logging.error("Resolution of the cover couldn't be determined.")

			# Получение размеров.
			if CoverImage is not None:
				FormattedTitle["covers"][CoverIndex]["width"], FormattedTitle["covers"][CoverIndex]["height"] = CoverImage.size

		# Конвертирование тегов.
		for TagIndex in range(0, len(self.__OriginalTitle["categories"])):
			FormattedTitle["tags"].append(self.__OriginalTitle["categories"][TagIndex]["name"].lower())

		# Конвертирование жанров.
		for GenreIndex in range(0, len(self.__OriginalTitle["genres"])):
			FormattedTitle["genres"].append(self.__OriginalTitle["genres"][GenreIndex]["name"].lower())

		# Сортировка глав по возрастанию.
		for BranchID in FormattedTitle["chapters"].keys():
			FormattedTitle["chapters"][BranchID] = sorted(FormattedTitle["chapters"][BranchID], key = lambda Value: (Value["volume"], Value["number"])) 

		return FormattedTitle
	
	# Конвертер: RN-V2 > RN-V1.
	def __RN2_to_RN1(self) -> dict:
		# Преобразование DMP-V1 в RN-V1.
		FormattedTitle = self.__DMP1_to_RN1()
		
		return FormattedTitle

	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	# Конструктор: задаёт описательную структуру тайтла.
	def __init__(self, Settings: dict, Title: dict, Format: str = None):

		#---> Генерация динамических свойств.
		#==========================================================================================#
		# Список известных форматов.
		self.__FormatsList = ["dmp-v1", "hcmp-v1", "htcrn-v1", "htmp-v1", "rn-v1", "rn-v2"]
		# Формат оригинальной структуры тайтла.
		self.__OriginalFormat = None
		# Оригинальная структура тайтла.
		self.__OriginalTitle = Title
		# Глобальные настройки.
		self.__Settings = Settings.copy()

		# Определение формата оригинальной структуры.
		if Format is None and "format" in Title.keys() and Title["format"] in self.__FormatsList:
			self.__OriginalFormat = Title["format"]
		elif Format is not None and Format in self.__FormatsList:
			self.__OriginalFormat = Format
		else:
			raise UnknownFormat(Format)

	# Конвертирует оригинальную структуру тайтла в заданный формат.
	def convert(self, Format: str | None) -> dict:
		# Буфер возвращаемой структуры.
		FormattedTitle = None

		# Проверка поддержки формата.
		if Format not in self.__FormatsList:
			raise UnknownFormat(Format)

		# Поиск необходимого конвертера.
		else:

			# Конвертирование: HCMP-V1.
			if self.__OriginalFormat == "hcmp-v1":
				# Выброс исключения: устаревший формат.
				raise DeprecatedFormat("hcmp-v1", "1.4.1")

			# Конвертирование: HTCRN-V1.
			if self.__OriginalFormat == "htcrn-v1":
				# Выброс исключения: устаревший формат.
				raise DeprecatedFormat("htcrn-v1", "1.4.1")

			# Конвертирование: HTMP-V1.
			if self.__OriginalFormat == "htmp-v1":
				# Выброс исключения: устаревший формат.
				raise DeprecatedFormat("htmp-v1", "1.4.1")

			# Конвертирование: DMP-V1.
			if self.__OriginalFormat == "dmp-v1":

				# Не конвертировать исходный формат.
				if Format == "dmp-v1": FormattedTitle = self.__OriginalTitle

				# Выброс исключения: устаревший формат.
				if Format == "hcmp-v1": raise DeprecatedFormat("hcmp-v1", "1.4.1")

				# Выброс исключения: устаревший формат.
				if Format == "htcrn-v1": raise DeprecatedFormat("htcrn-v1", "1.4.1")

				# Выброс исключения: устаревший формат.
				if Format == "htmp-v1": raise DeprecatedFormat("htmp-v1", "1.4.1")
					
				# Запуск конвертера: DMP-V1 > RN-V1.
				if Format == "rn-v1": FormattedTitle = self.__DMP1_to_RN1()
					
				# Выброс исключения: не существует подходящего конвертера.
				if Format == "rn-v2": raise UnableToConvert(self.__OriginalFormat, Format)

			# Конвертирование: RN-V1.
			if self.__OriginalFormat == "rn-v1":

				# Запуск конвертера: RN-V1 > DMP-V1.
				if Format == "dmp-v1": FormattedTitle = self.__RN1_to_DMP1()

				# Выброс исключения: устаревший формат.
				if Format == "hcmp-v1": raise DeprecatedFormat("hcmp-v1", "1.4.1")

				# Выброс исключения: устаревший формат.
				if Format == "htcrn-v1": raise DeprecatedFormat("htcrn-v1", "1.4.1")

				# Запуск конвертера: RN-V1 > HTMP-V1.
				if Format == "htmp-v1": FormattedTitle = self.__RN1_to_HTMP1()

				# Не конвертировать исходный формат.
				if Format == "rn-v1": FormattedTitle = self.__OriginalTitle
					
				# Запуск конвертера: RN-V1 > RN-V2.
				if Format == "rn-v2": FormattedTitle = self.__RN1_to_RN2()
					
			# Конвертирование: RN-V2.
			if self.__OriginalFormat == "rn-v2":

				# Выброс исключения: не существует подходящего конвертера.
				if Format == "dmp-v1": raise UnableToConvert(self.__OriginalFormat, Format)

				# Выброс исключения: устаревший формат.
				if Format == "hcmp-v1": raise DeprecatedFormat("hcmp-v1", "1.4.1")

				# Выброс исключения: устаревший формат.
				if Format == "htcrn-v1": raise DeprecatedFormat("htcrn-v1", "1.4.1")

				# Выброс исключения: устаревший формат.
				if Format == "htmp-v1": raise DeprecatedFormat("htmp-v1", "1.4.1")

				# Запуск конвертера: RN-V2 > RN-V1.
				if Format == "rn-v1": FormattedTitle = self.__RN2_to_RN1()
					
				# Не конвертировать исходный формат.
				if Format == "rn-v2": FormattedTitle = self.__OriginalTitle

		return FormattedTitle

	# Возвращает автоматически определённый формат.
	def getFormat(self) -> str:
		return self.__OriginalFormat;