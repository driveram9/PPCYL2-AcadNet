from flask import Blueprint, request, jsonify

uploads_bp = Blueprint("uploads", __name__)

@uploads_bp.route("/upload", methods=["POST"])
def upload():
    archivo = request.files.get("file")
    if not archivo:
        return jsonify({"error": "No se envió ningún archivo"}), 400

    # Aquí podrías guardar el archivo en tu carpeta "uploads"
    archivo.save(f"uploads/{archivo.filename}")
    return jsonify({"mensaje": f"Archivo {archivo.filename} subido correctamente"})
