import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper
from io import BytesIO

TARGET_W = 3840
TARGET_H = 2160
ASPECT_RATIO = (TARGET_W, TARGET_H)
PREVIEW_WIDTH = 800

st.title("🖼️ Samsung The Frame – Art Mode")

uploaded = st.file_uploader(
    "Sube una imagen",
    type=["jpg", "jpeg", "png"]
)

if uploaded:
    original = Image.open(uploaded).convert("RGB")
    ow, oh = original.size

    if ow < TARGET_W or oh < TARGET_H:
        st.error("La imagen debe ser mayor a 3840 × 2160 px")
        st.stop()

    # ======================
    # Selector de preset
    # ======================
    is_vertical = oh > ow

    if is_vertical:
        preset = st.radio(
            "Preset de encuadre",
            ["👤 Retrato (recomendado)", "🎨 Centrado", "🏛️ Inferior"],
            horizontal=True
        )
    else:
        preset = "🎨 Centrado"

    # ======================
    # Preview base
    # ======================
    scale = PREVIEW_WIDTH / ow
    preview_h = int(oh * scale)
    preview = original.resize((PREVIEW_WIDTH, preview_h), Image.LANCZOS)

    # ======================
    # DESPLAZAMIENTO POR PRESET (CLAVE)
    # ======================
    crop_h = int(PREVIEW_WIDTH / (TARGET_W / TARGET_H))
    max_shift = preview_h - crop_h

    if preset.startswith("👤"):
        shift_y = int(max_shift * 0.15)
    elif preset.startswith("🏛️"):
        shift_y = int(max_shift * 0.75)
    else:
        shift_y = int(max_shift * 0.5)

    # recortar preview según preset
    preview_for_cropper = preview.crop(
        (0, shift_y, PREVIEW_WIDTH, shift_y + crop_h)
    )

    st.markdown("### Ajusta el encuadre (16:9)")

    cropped_box = st_cropper(
        preview_for_cropper,
        aspect_ratio=ASPECT_RATIO,
        box_color="#00FFAA",
        realtime_update=True,
        return_type="box"
    )

    # ======================
    # Procesamiento final
    # ======================
    if st.button("Convertir a 3840 × 2160"):
        left = int(cropped_box["left"] / scale)
        top = int((cropped_box["top"] + shift_y) / scale)
        width = int(cropped_box["width"] / scale)
        height = int(cropped_box["height"] / scale)

        cropped_original = original.crop(
            (left, top, left + width, top + height)
        )

        final = cropped_original.resize(
            (TARGET_W, TARGET_H),
            Image.LANCZOS
        )

        st.image(final, caption="Resultado final")

        buffer = BytesIO()
        final.save(buffer, format="JPEG", quality=95, optimize=True)
        buffer.seek(0)

        st.download_button(
            "Descargar JPG",
            data=buffer,
            file_name="the_frame_art.jpg",
            mime="image/jpeg"
        )
