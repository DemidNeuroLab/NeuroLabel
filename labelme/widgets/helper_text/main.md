Сюда надо вставить текст, который будет отображаться в подсказке в главном окне

# Как вставлять картинки

1. Копириуем нужную картинку в папку labelme\widgets\helper_text\images
2. Вставляем в файл labelme\widgets\helper_text\help.qrc строку с именем файла: <file>images/9.jpg</file>
3. Компилируем ресурсы в терминале, который запущен из папки labelme\widgets\helper_text: pyrcc5 -o help.py help.qrc
4. Вставляем в markdown картинку как обычно: ![Фото](images/9.jpg)

![Фото](images/9.jpg)