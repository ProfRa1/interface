import tkinter as tk
import cv2
from PIL import Image, ImageTk
import os
from datetime import datetime

class WebcamApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        
        self.cap = None
        self.camera_active = False
        self.counting = False
        
        self.canvas = tk.Canvas(window, width=640, height=480)
        self.canvas.pack()
        
        self.btn_start = tk.Button(window, text="Abrir Câmera", width=15, command=self.start_camera)
        self.btn_start.pack(anchor=tk.CENTER, expand=True)
        
        self.btn_stop = tk.Button(window, text="Fechar Câmera", width=15, command=self.stop_camera)
        self.btn_stop.pack(anchor=tk.CENTER, expand=True)
        self.btn_stop["state"] = "disabled"
        
        self.btn_capture = tk.Button(window, text="Capturar Foto", width=15, command=self.capture_photo)
        self.btn_capture.pack(anchor=tk.CENTER, expand=True)
        self.btn_capture["state"] = "disabled"
        
        self.btn_count = tk.Button(window, text="Contar Objetos", width=15, command=self.toggle_counting)
        self.btn_count.pack(anchor=tk.CENTER, expand=True)
        self.btn_count["state"] = "disabled"
        
        self.label_status = tk.Label(window, text="Câmera inativa", fg="red")
        self.label_status.pack(anchor=tk.CENTER, expand=True)
        
        self.label_count = tk.Label(window, text="", fg="blue")
        self.label_count.pack(anchor=tk.CENTER, expand=True)
        
        self.update()
        
        self.window.mainloop()
    
    def start_camera(self):
        if not self.camera_active:
            self.label_status.config(text="Câmera sendo aberta...", fg="blue")
            self.window.update_idletasks()  # Atualiza a janela para mostrar o texto antes de abrir a câmera
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                self.camera_active = True
                self.btn_start["state"] = "disabled"
                self.btn_stop["state"] = "normal"
                self.btn_capture["state"] = "normal"
                self.btn_count["state"] = "normal"
                self.label_status.config(text="Câmera ativa", fg="green")
            else:
                self.label_status.config(text="Erro ao abrir a câmera", fg="red")
        
    def stop_camera(self):
        if self.camera_active:
            self.cap.release()
            self.camera_active = False
            self.btn_start["state"] = "normal"
            self.btn_stop["state"] = "disabled"
            self.btn_capture["state"] = "disabled"
            self.btn_count["state"] = "disabled"
            self.canvas.delete("all")
            self.label_status.config(text="Câmera inativa", fg="red")
            self.label_count.config(text="", fg="blue")
    
    def capture_photo(self):
        if self.camera_active:
            ret, frame = self.cap.read()
            if ret:
                try:
                    # Diretório para salvar a imagem (pasta Imagens do usuário)
                    images_dir = os.path.join(os.path.expanduser("~"), "Pictures")
                    if not os.path.exists(images_dir):
                        os.makedirs(images_dir)
                    # Salva a imagem com um nome de arquivo baseado na data e hora atuais
                    filename = datetime.now().strftime("foto_%Y%m%d_%H%M%S.png")
                    filepath = os.path.join(images_dir, filename)
                    # Salvar a imagem
                    success = cv2.imwrite(filepath, frame)
                    if success:
                        self.label_status.config(text=f"Foto capturada: {filepath}", fg="green")
                    else:
                        self.label_status.config(text="Erro ao salvar a foto", fg="red")
                        print("Erro: Falha ao salvar a foto.")
                except Exception as e:
                    self.label_status.config(text="Erro ao salvar a foto", fg="red")
                    print(f"Erro ao salvar a foto: {e}")
            else:
                self.label_status.config(text="Erro ao capturar a foto", fg="red")
    
    def toggle_counting(self):
        self.counting = not self.counting
        
    def update(self):
        if self.camera_active:
            ret, frame = self.cap.read()
            if ret:
                if self.counting:
                    # Converte a imagem para escala de cinza
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    # Melhora o contraste da imagem
                    gray = cv2.equalizeHist(gray)
                    # Aplica um filtro Gaussian Blur para suavizar a imagem
                    blurred = cv2.GaussianBlur(gray, (15, 15), 0)
                    # Aplica um limiar adaptativo para segmentação
                    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
                    # Operações morfológicas para remover ruídos e melhorar a segmentação
                    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
                    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
                    # Encontra contornos
                    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    # Filtra contornos muito pequenos
                    min_contour_area = 500  # Ajuste conforme necessário
                    filtered_contours = [contour for contour in contours if cv2.contourArea(contour) > min_contour_area]
                    # Atualiza a contagem de objetos
                    self.label_count.config(text=f"Objetos contados: {len(filtered_contours)}")
                    # Desenha os contornos e numera os objetos
                    for i, contour in enumerate(filtered_contours):
                        x, y, w, h = cv2.boundingRect(contour)
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        cv2.putText(frame, str(i+1), (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                # Converte a imagem para RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.window.after(10, self.update)

if __name__ == "__main__":
    root = tk.Tk()
    app = WebcamApp(root, "Webcam App")
