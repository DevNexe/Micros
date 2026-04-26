from flask import Flask, Response, request
import time

app = Flask(__name__)

# Глобальный буфер для хранения аудиоданных
audio_buffer = bytearray()

@app.route('/audio.wav', methods=['POST'])
def receive_audio():
    """Эндпоинт для приема аудио с телефона"""
    global audio_buffer
    try:
        # Читаем поток данных от телефона
        while True:
            chunk = request.stream.read(1024)
            if not chunk:
                break
            audio_buffer.extend(chunk)
            # Ограничиваем размер буфера, чтобы не переполнить память
            if len(audio_buffer) > 1024 * 1024: # 1MB
                audio_buffer = audio_buffer[-512*1024:]
    except Exception as e:
        print(f"Connection closed: {e}")
    return "OK"

@app.route('/audio.wav', methods=['GET'])
def stream_audio():
    """Эндпоинт для отдачи аудио вашему скрипту"""
    def generate():
        global audio_buffer
        last_pos = 0
        while True:
            if len(audio_buffer) > last_pos:
                chunk = audio_buffer[last_pos:]
                last_pos = len(audio_buffer)
                yield chunk
            else:
                time.sleep(0.1)
    
    return Response(generate(), mimetype='audio/wav')

if __name__ == '__main__':
    # Запускаем на всех интерфейсах на порту 8080
    app.run(host='0.0.0.0', port=8080, threaded=True)
