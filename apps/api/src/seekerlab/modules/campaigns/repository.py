from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from seekerlab.modules.campaigns.models import Campaign, Submission


class CampaignRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_open(self, limit: int, offset: int) -> list[Campaign]:
        query = (select(Campaign).where(Campaign.status == "open")
                 .order_by(Campaign.created_at.desc(), Campaign.id).limit(limit).offset(offset))
        return list(self.session.scalars(query))

    def get(self, campaign_id: UUID, *, lock: bool = False) -> Campaign | None:
        query = select(Campaign).where(Campaign.id == campaign_id)
        if lock:
            query = query.with_for_update()
        return self.session.scalar(query)

    def already_submitted(self, campaign_id: UUID, tester_id: str) -> bool:
        return self.session.scalar(select(Submission.id).where(
            Submission.campaign_id == campaign_id, Submission.tester_id == tester_id,
        )) is not None

    def for_tester(self, tester_id: str, limit: int, offset: int) -> list[Submission]:
        return list(self.session.scalars(select(Submission).where(
            Submission.tester_id == tester_id,
        ).order_by(Submission.created_at.desc(), Submission.id).limit(limit).offset(offset)))

    def for_campaign(self, campaign_id: UUID, limit: int, offset: int) -> list[Submission]:
        return list(self.session.scalars(select(Submission).where(
            Submission.campaign_id == campaign_id,
        ).order_by(Submission.created_at.desc(), Submission.id).limit(limit).offset(offset)))
