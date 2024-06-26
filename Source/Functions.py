from skimage.metrics import structural_similarity
from dublib.Methods import ReadJSON

import logging
import shutil
import cv2
import os

# Возвращает процент различий изображений.
def CompareImages(PatternPath: str, ImagePath: str) -> float | None:
	# Процент отличий.
	Differences = None
	
	# Если не удалось найти файл шаблона.
	if os.path.exists(PatternPath) == False:
		raise FileNotFoundError(PatternPath)
	
	# Если удалось найти файл для сравнения.
	elif os.path.exists(ImagePath) == True:

		try:
			# Чтение изображений.
			Pattern = cv2.imread(PatternPath)
			Image = cv2.imread(ImagePath)
			# Преобразование изображений в чёрно-белый формат.
			Pattern = cv2.cvtColor(Pattern, cv2.COLOR_BGR2GRAY)
			Image = cv2.cvtColor(Image, cv2.COLOR_BGR2GRAY)
			# Получение разрешений изображений.
			PatternHeight, PatternWidth = Pattern.shape
			ImageHeight, ImageWidth = Image.shape
		
			# Если шаблон и изображение имеют одинаковое разрешение.
			if PatternHeight == ImageHeight and PatternWidth == ImageWidth:
				# Сравнение двух изображений.
				(Similarity, Differences) = structural_similarity(Pattern, Image, full = True)
				# Конвертирование в проценты.
				Differences = 100.0 - (float(Similarity) * 100.0)

		except cv2.error as ExceptionData:
			# Запись в лог ошибки: исключение.
			logging.error("Error occurred during comparing images: \"" + str(ExceptionData) + "\".")		
			# Обнуление процента отличий.
			Differences = None

	return Differences

# Удаляет или перемещает файлы JSON, имеющий отличный от заданного формат.
def ManageOtherFormatsFiles(Settings: dict, Format: str, TargetDirectory: str | None):
	# Список файлов в директории хранения JSON.
	FilesList = os.listdir(Settings["titles-directory"])
	# Фильтрация только файлов JSON.
	FilesList = list(filter(lambda x: x.endswith(".json"), FilesList))
		
	# Для каждого файла.
	for Filename in FilesList:
		# Чтение файла.
		File = ReadJSON(Settings["titles-directory"] + "/" + Filename)
		# Формат файла.
		FileFormat = None
		
		# Если указан формат.
		if "format" in File.keys():
			FileFormat = File["format"].lower()

		# Если в файле не указан формат или он не соответствует заданному.
		if FileFormat == None or FileFormat != Format.lower():
				
			# Если указано куда, то переместить файл.
			if TargetDirectory != None:
					
				# Если путь к директории не заканчивается слешем, то добавить его.
				if TargetDirectory[-1] not in ["/", "\\"]:
					TargetDirectory += "\\" if "\\" in TargetDirectory else "/"
					
				# Если целевая директория существует.
				if os.path.exists(TargetDirectory):
					# Переместить файл.
					shutil.move(Settings["titles-directory"] + "/" + Filename, TargetDirectory + Filename)
					
					# Запись в лог сообщения: файл перемещён.
					if Format != None:
						logging.info("File \"" + Filename+ "\"" + " in \"" + Format.upper() + "\"format. Moved.")
					else:
						logging.info("File \"" + Filename+ "\"" + " without format. Moved.")
						
				else:
					raise FileNotFoundError
					
			# Иначе удалить.
			else:
				# Удаление файла.
				os.remove(Settings["titles-directory"] + "/" + Filename)
				
				# Запись в лог сообщения: файл удалён.
				if Format != None:
					logging.info("File \"" + Filename+ "\"" + "in \"" + Format.upper() + "\" format. Removed.")
				else:
					logging.info("File \"" + Filename+ "\"" + " without format. Removed.")

# Объединяет список списков в один список.
def MergeListOfLists(ListOfLists: list) -> list:
	
	# Если список не пустой и включает списки, то объединить.
	if len(ListOfLists) > 0 and type(ListOfLists[0]) is list:
		# Результат объединения.
		Result = list()

		# Объединить все списки в один список.
		for List in ListOfLists:
			Result.extend(List)

		return Result
	# Если список включет словари, то вернуть без изменений.
	else:
		return ListOfLists
				
# Проевращает число секунд в строку-дескриптор времени по формату [<x> hours <y> minuts <z> seconds].
def SecondsToTimeString(Seconds: float) -> str:
	# Количество часов.
	Hours = int(Seconds / 3600.0)
	Seconds -= Hours * 3600
	# Количество минут.
	Minutes = int(Seconds / 60.0)
	Seconds -= Minutes * 60
	# Количество секунд.
	Seconds = ToFixedFloat(Seconds, 2)
	# Строка-дескриптор времени.
	TimeString = ""

	# Генерация строки.
	if Hours > 0:
		TimeString += str(Hours) + " hours "
	if Minutes > 0:
		TimeString += str(Minutes) + " minutes "
	if Seconds > 0:
		TimeString += str(Seconds) + " seconds"

	return TimeString

# Усекает число до определённого количества знаков после запятой.
def ToFixedFloat(FloatNumber: float, Digits: int = 0) -> float:
	return float(f"{FloatNumber:.{Digits}f}")