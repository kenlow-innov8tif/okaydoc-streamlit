"""Builders for API request parameter payloads."""


def build_okaydoc_api_params(
    doc_type,
    version,
    landmark_check,
    font_check,
    microprint_check,
    photo_substitution_check,
    ic_type_check,
    color_mode,
    hologram,
    screen_detection,
    ghost_photo_color_detection,
    id_blur_detection,
    islam_field_tampering_detection,
    quality_check_detection,
):
    return {
        "docType": doc_type,
        "version": version,
        "landmarkCheck": landmark_check,
        "fontCheck": font_check,
        "microprintCheck": microprint_check,
        "photoSubstitutionCheck": photo_substitution_check,
        "icTypeCheck": ic_type_check,
        "colorMode": color_mode,
        "hologram": hologram,
        "screenDetection": screen_detection,
        "ghostPhotoColorDetection": ghost_photo_color_detection,
        "idBlurDetection": id_blur_detection,
        "islamFieldTamperingDetection": islam_field_tampering_detection,
        "qualityCheckDetection": quality_check_detection,
    }
