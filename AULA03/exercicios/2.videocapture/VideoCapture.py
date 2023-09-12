import cv2 as cv

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

    # Manipulação da imagem
    #frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # display do resultado
    cv.imshow('frame', frame)

    #monitora o teclado para detectar se foi pressionado o q
    if cv.waitKey(1) == ord('q'):
        break

cap.release()
cv.destroyAllWindows()