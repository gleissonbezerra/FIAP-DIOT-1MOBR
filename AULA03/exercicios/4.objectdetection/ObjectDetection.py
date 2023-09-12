import cv2 as cv

from InferenceCapture import InferenceCapture

ic = InferenceCapture()

cap = cv.VideoCapture(0)

if not cap.isOpened():
    print("Erro ao tentar abrir a camera")
    exit()


while True:
    # Captura um frame de cada vez
    ret, frame = cap.read()

    # se frame foi lido
    if not ret:
        print("Erro ao tentar ler o frame!")
        continue

    #inferencia
    result = ic.inference(frame)

    #carrega colecao de objetos detectados
    d = result["detections"]


    for i in d:
        #print(i["name"])
        x = i["bbox"]["x"]
        y = i["bbox"]["y"]
        w = i["bbox"]["w"]
        h = i["bbox"]["h"]

        cv.rectangle(frame, (x, y), (x + w, y + h), (0,255,0), 2)
        text = "{}: {:.2f}%".format(i["label"], i["score"]*100)
        cv.putText(frame, text, (x, y - 5), cv.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

    
    # display do resultado
    cv.imshow('frame', frame)

    #monitora o teclado para detectar se foi pressionado o q
    if cv.waitKey(1) == ord('q'):
        break

cap.release()
cv.destroyAllWindows()