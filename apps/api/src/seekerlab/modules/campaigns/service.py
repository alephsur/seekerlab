from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from seekerlab.modules.campaigns.domain import (
    Conflict, Forbidden, NotFound, clean_feedback, ensure_can_submit, validate_reward,
)
from seekerlab.modules.campaigns.models import Campaign, Submission
from seekerlab.modules.campaigns.repository import CampaignRepository
from seekerlab.modules.campaigns.schemas import CampaignCreate


class CampaignService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = CampaignRepository(session)

    def get(self, campaign_id: UUID, *, lock: bool = False) -> Campaign:
        campaign = self.repo.get(campaign_id, lock=lock)
        if campaign is None:
            raise NotFound("Campaign not found")
        return campaign

    def create(self, data: CampaignCreate, owner_id: str) -> Campaign:
        validate_reward(data.reward_amount)
        campaign = Campaign(**data.model_dump(), owner_id=owner_id)
        self.session.add(campaign)
        self.session.commit()
        self.session.refresh(campaign)
        return campaign

    def submit(self, campaign_id: UUID, tester_id: str, feedback: str) -> Submission:
        feedback = clean_feedback(feedback)
        # PostgreSQL serializes submissions to the same campaign before checking capacity.
        campaign = self.get(campaign_id, lock=True)
        ensure_can_submit(campaign.status, campaign.submitted_count, campaign.capacity,
                          self.repo.already_submitted(campaign_id, tester_id))
        submission = Submission(campaign_id=campaign_id, tester_id=tester_id, feedback=feedback)
        self.session.add(submission)
        campaign.submitted_count += 1
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise Conflict("Duplicate submission or campaign capacity reached") from exc
        self.session.refresh(submission)
        return submission

    def close(self, campaign_id: UUID, owner_id: str) -> Campaign:
        campaign = self.get(campaign_id, lock=True)
        self.require_owner(campaign, owner_id)
        campaign.status = "closed"
        self.session.commit()
        return campaign

    @staticmethod
    def require_owner(campaign: Campaign, owner_id: str) -> None:
        if campaign.owner_id != owner_id:
            raise Forbidden("Only the campaign owner can access this resource")
