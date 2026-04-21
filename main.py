import os
import socket
import sys
import json
import threading
import time
import webbrowser
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

sys.path.append(str(Path(__file__).parent / "src"))

from engelamiento.data.loader import WRFLoader
from engelamiento.detection.engelamiento import detect_engelamiento
from engelamiento.detection.trajectory import calculate_vertical_profile
from engelamiento.visualization.radar_map import plot_engelamiento_map
from engelamiento.visualization.exporter import FrameExporter


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == "/api/profile":
            self.handle_profile_api(parsed_url)
        else:
            super().do_GET()

    def handle_profile_api(self, parsed_url):
        query = parse_qs(parsed_url.query)
        try:
            # Asegurar que leemos correctamente lat1, lon1 (A) y lat2, lon2 (B)
            lat1 = float(query.get("lat1")[0])
            lon1 = float(query.get("lon1")[0])
            lat2 = float(query.get("lat2")[0])
            lon2 = float(query.get("lon2")[0])
            time_idx = int(query.get("time", [0])[0])

            # Cargar datos para el cálculo
            DATA_PATH = Path("Data/wrfout_d01_2015-04-17_18_00_00_corte.nc")
            loader = WRFLoader(DATA_PATH)
            ds = loader._open_dataset()

            # El orden de los argumentos aquí debe ser estricto: A -> B
            result = calculate_vertical_profile(ds, time_idx, lat1, lon1, lat2, lon2)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode("utf-8"))


def start_server(port=5000, directory=None):
    if directory:
        os.chdir(directory)

    # Allow port reuse to avoid TIME_WAIT issues
    class ReusableServer(HTTPServer):
        def server_bind(self):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            super().server_bind()

    server = ReusableServer(("127.0.0.1", port), QuietHandler)
    print(f"\n[OK] Servidor iniciado en http://127.0.0.1:{port}")
    print(f"[OK] Accede a: http://127.0.0.1:{port}/templates/index.html")
    server.serve_forever()


def main():
    DATA_PATH = Path("Data/wrfout_d01_2015-04-17_18_00_00_corte.nc")
    OUTPUT_DIR = Path("output")
    OUTPUT_DIR.mkdir(exist_ok=True)

    loader = WRFLoader(DATA_PATH)

    print("=" * 50)
    print("  EXPORTACION DE FRAMES PARA INTERFAZ WEB")
    print("=" * 50)
    exporter = FrameExporter(loader, OUTPUT_DIR)
    exporter.export_all()

    print("\n" + "=" * 50)
    print("  GENERACION DE MAPAS ESTATICOS")
    print("=" * 50)

    TIME_IDX = 0
    for t in range(loader.num_times):
        temp_data = loader.load_timestep(t)
        risk_check = ((temp_data["QRAIN"] > 0) | (temp_data["QCLOUD"] > 0)) & (
            temp_data["TK"] < 273.15
        )
        if int(risk_check.sum()) > 0:
            TIME_IDX = t
            print(f"[OK] Riesgo detectado en timestep {t}")
            break

    data = loader.load_timestep(time_idx=TIME_IDX)
    engelamiento = detect_engelamiento(data)

    output_path_png = OUTPUT_DIR / "engelamiento_map.png"
    output_path_svg = OUTPUT_DIR / "engelamiento_map.svg"

    plot_engelamiento_map(
        engelamiento_pressure=engelamiento,
        lats=data["XLAT"],
        lons=data["XLONG"],
        output_path=str(output_path_png),
        title=f"Riesgo de Engelamiento - {loader.times.values[TIME_IDX]}",
    )
    print(f"[OK] Mapa PNG guardado: {output_path_png}")

    plot_engelamiento_map(
        engelamiento_pressure=engelamiento,
        lats=data["XLAT"],
        lons=data["XLONG"],
        output_path=str(output_path_svg),
        title=f"Riesgo de Engelamiento - {loader.times.values[TIME_IDX]}",
    )
    print(f"[OK] Mapa SVG guardado: {output_path_svg}")

    print("\n" + "=" * 50)
    print("  INICIANDO INTERFAZ INTERACTIVA")
    print("=" * 50)

    port = 5000
    project_root = Path(__file__).parent

    server_thread = threading.Thread(
        target=start_server, args=(port, str(project_root)), daemon=False
    )
    server_thread.start()

    time.sleep(2)

    webbrowser.open(f"http://127.0.0.1:{port}/templates/index.html")

    print("\n[OK] Listo!")
    print("[OK] El servidor seguira funcionando en background.")
    print(f"[OK] Accede a: http://127.0.0.1:{port}/templates/index.html")
    print("[OK] Para detener el servidor, cierra esta ventana o presiona Ctrl+C")


if __name__ == "__main__":
    main()
