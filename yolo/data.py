import bs4 # Позволяет читать XML-файлы.
import lxml # Вспомогательный парсер XML-файлов
import cv2 # Позволяет работать с изображениями.
import os # Пакет для манипуляции каталогами и файлами.

# Получить YOLO-разметку для одного файла.
def label_to_yolo(labels, name:str, image_width, image_height):
    new_labels_text = '' # Сюда будет сохраняться разметка.
    class_code = 0 if name == 'textregion' else 1 # Текст обозначим меткой 0, а строки -- меткой 1.
    texts = labels.find_all(name)
    for text in texts:
        new_labels_text += str(class_code) # Запись метки класса.
        coords = text.find('coords')
        points = coords.get('points')
        points = points.split(' ')
        for point in points:
            coords = point.split(',')

            # Иногда разметка поломана и там написаны пустые строки. Нужно их пропускать!
            if(coords[0] == ''):
                continue

            # Каждая точка в YOLO-разметке находится как координата исходного пикселя, делённая на длину (по X) или на ширину (по Y).
            x = round(int(coords[0]) / image_width, 5)
            y = round(int(coords[1]) / image_height, 5)
            new_labels_text += f' {x} {y}'

        new_labels_text += '\n' # Перевод строки.

    return new_labels_text

# Получить YOLO-разметку для целого каталога.
def translate_to_yolo_format(label_folder: str, new_label_folder: str):
    if not os.path.exists(new_label_folder):
        os.mkdir(new_label_folder)
    
    for label_file in os.listdir(label_folder):
        with open(os.path.join(label_folder, label_file), 'r') as labels:
            labels = bs4.BeautifulSoup(labels.read(), 'lxml')
            image_parameters = labels.find('page')
            image_width = int(image_parameters.get('imagewidth'))
            image_height = int(image_parameters.get('imageheight'))

            # Заменим расширение файла с xml на txt.
            new_label_file = label_file.replace('.xml', '.txt')

            with open(os.path.join(new_label_folder, new_label_file), 'w') as new_labels:
                textregions = label_to_yolo(labels, 'textregion', image_width, image_height)
                textlines = label_to_yolo(labels, 'textline', image_width, image_height)
                new_labels.write(textregions+textlines)

translate_to_yolo_format('./Guerin/train/page', './Guerin/train/labels')
translate_to_yolo_format('./Guerin/val/page', './Guerin/val/labels')
