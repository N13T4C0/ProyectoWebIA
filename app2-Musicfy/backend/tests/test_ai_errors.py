import pytest

from app import errors

ERRORES = [
    # PR-10
    (errors.timeout(), 504, "TIMEOUT", "La IA ha tardado demasiado en responder. Inténtalo de nuevo."),
    # PR-11
    (
        errors.ia_no_disponible(),
        502,
        "IA_NO_DISPONIBLE",
        "El servicio de recomendaciones no está disponible ahora mismo. Inténtalo más tarde.",
    ),
    # PR-12
    (
        errors.respuesta_invalida(),
        502,
        "RESPUESTA_INVALIDA",
        "La IA no ha devuelto recomendaciones válidas. Inténtalo de nuevo.",
    ),
    (
        RuntimeError("secreto-interno"),
        500,
        "ERROR_INTERNO",
        "Se ha producido un error inesperado. Inténtalo más tarde.",
    ),
]


@pytest.mark.parametrize(
    ("exc", "status", "codigo", "mensaje"),
    ERRORES,
    ids=["timeout", "ia-no-disponible", "respuesta-invalida", "inesperado"],
)
def test_fallo_de_la_ia_da_el_error_del_contrato(client, fake_ai, auth_header, exc, status, codigo, mensaje):
    fake_ai.exc = exc

    response = client.post("/api/recommend", json={"tastes": "Rock"}, headers=auth_header)

    assert response.status_code == status
    assert response.json() == {"error": {"codigo": codigo, "mensaje": mensaje}}
    assert fake_ai.calls == ["Rock"]
    assert "secreto-interno" not in response.text
    assert "Traceback" not in response.text
