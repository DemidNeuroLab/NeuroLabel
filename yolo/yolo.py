from ultralytics.models import YOLO

model = YOLO("./yolo/yolo11n-seg.pt")

model.train(epochs = 100,           # количество эпох обучения
            data = "./yolo/yolo.yaml",     # указываем датасет для обучения
            imgsz = 640,            # размер изоображений получаемых на вход модели
            batch = 20,             # размер пакета
            device = 'cpu',           # устройство для обучения 0 - cuda
            plots = True)