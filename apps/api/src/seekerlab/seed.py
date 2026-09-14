from uuid import UUID

from seekerlab.config import get_settings
from seekerlab.db import SessionLocal
from seekerlab.modules.campaigns.models import Campaign
from seekerlab.modules.campaigns.schemas import CampaignCreate

EXAMPLES = [
    ("11111111-1111-4111-8111-111111111111", {
        "title": "Primeros pasos sin fricción", "description": "Campaña de ejemplo: revisa el recorrido inicial de SeekerLab y explica qué cambiarías.",
        "instructions": ["Explora las campañas disponibles", "Abre una campaña y revisa las instrucciones", "Describe un punto de confusión y cómo lo mejorarías"],
        "reward_amount": "3.00", "currency": "USDC", "estimated_minutes": 5, "capacity": 20,
    }),
    ("22222222-2222-4222-8222-222222222222", {
        "title": "¿Se entiende la recompensa?", "description": "Campaña de ejemplo: comprueba si los importes y las condiciones de una prueba están claros.",
        "instructions": ["Localiza la recompensa anunciada", "Revisa cuándo se cobraría y qué está pendiente", "Propón una mejora concreta para mostrar esta información"],
        "reward_amount": "5.00", "currency": "USDC", "estimated_minutes": 8, "capacity": 12,
    }),
    ("33333333-3333-4333-8333-333333333333", {
        "title": "Lectura y accesibilidad", "description": "Campaña de ejemplo: evalúa el tamaño del texto, los botones y la claridad del formulario.",
        "instructions": ["Aumenta el tamaño de fuente en Android", "Abre el formulario de una campaña", "Explica qué elementos resultan difíciles de leer o pulsar"],
        "reward_amount": "4.00", "currency": "USDC", "estimated_minutes": 6, "capacity": 15,
    }),
]


def main() -> None:
    if get_settings().app_env == "production":
        raise SystemExit("Demo seed is disabled in production")
    with SessionLocal() as session:
        created = 0
        for identifier, data in EXAMPLES:
            campaign_id = UUID(identifier)
            if session.get(Campaign, campaign_id) is None:
                payload = CampaignCreate.model_validate(data)
                session.add(Campaign(id=campaign_id, owner_id="local-builder", **payload.model_dump()))
                created += 1
        session.commit()
        print(f"Seed complete: {created} example campaigns created. No real rewards are funded.")


if __name__ == "__main__":
    main()
