import cv2

from google.cloud import vision
from google.oauth2 import service_account

# Configure a chave de API
credentials = service_account.Credentials.from_service_account_file(
    'api_key.json'
)


client = vision.ImageAnnotatorClient(credentials=credentials)

mainCamera = cv2.VideoCapture(0)

if not mainCamera.isOpened():
    print("Erro ao tentar abrir a camera")
    exit()


while True:

        ret, frame = mainCamera.read()
        if not ret:
            print("Erro ao tentar ler o frame!")
            continue

        w = frame.shape[1]
        h = frame.shape[0]

        content = cv2.imencode(".jpg", frame)[1].tostring()

        image = vision.Image(content=content)

        objects = client.object_localization(image=image).localized_object_annotations
        objects = objects[:2] #2 primeiros

        for o in objects:

            x1, y1 = int(o.bounding_poly.normalized_vertices[0].x*w), int(o.bounding_poly.normalized_vertices[0].y*h)
            x2, y2 = int(o.bounding_poly.normalized_vertices[1].x*w), int(o.bounding_poly.normalized_vertices[1].y*h)
            x3, y3 = int(o.bounding_poly.normalized_vertices[2].x*w), int(o.bounding_poly.normalized_vertices[2].y*h)
            x4, y4 = int(o.bounding_poly.normalized_vertices[3].x*w), int(o.bounding_poly.normalized_vertices[3].y*h)

            cv2.rectangle(frame, (x1, y1), (x3, y3), (0, 255, 0), 2)
            cv2.putText(frame,o.name+": "+str(round(o.score*100,1))+"%", (x1, y1-15), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        cv2.imshow("Analise em Tempo Real", frame)

mainCamera.release()

