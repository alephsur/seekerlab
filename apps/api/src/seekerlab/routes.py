from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from seekerlab.db import get_session
from seekerlab.modules.campaigns.repository import CampaignRepository
from seekerlab.modules.campaigns.schemas import CampaignCreate, CampaignRead, SubmissionCreate, SubmissionRead
from seekerlab.modules.campaigns.service import CampaignService
from seekerlab.modules.identity.dependencies import Principal, require_builder, require_tester

router = APIRouter(prefix="/api/v1")
Db = Annotated[Session, Depends(get_session)]
Builder = Annotated[Principal, Depends(require_builder)]
Tester = Annotated[Principal, Depends(require_tester)]
Limit = Annotated[int, Query(ge=1, le=100)]
Offset = Annotated[int, Query(ge=0)]


@router.get("/campaigns", response_model=list[CampaignRead], tags=["campaigns"])
def list_campaigns(session: Db, limit: Limit = 50, offset: Offset = 0):
    return CampaignRepository(session).list_open(limit, offset)


@router.post("/campaigns", response_model=CampaignRead, status_code=201, tags=["campaigns"])
def create_campaign(data: CampaignCreate, session: Db, principal: Builder):
    return CampaignService(session).create(data, principal.id)


@router.get("/campaigns/{campaign_id}", response_model=CampaignRead, tags=["campaigns"])
def get_campaign(campaign_id: UUID, session: Db):
    return CampaignService(session).get(campaign_id)


@router.post("/campaigns/{campaign_id}/close", response_model=CampaignRead, tags=["campaigns"])
def close_campaign(campaign_id: UUID, session: Db, principal: Builder):
    return CampaignService(session).close(campaign_id, principal.id)


@router.post("/campaigns/{campaign_id}/submissions", response_model=SubmissionRead,
             status_code=201, tags=["submissions"])
def submit_feedback(campaign_id: UUID, data: SubmissionCreate, session: Db, principal: Tester):
    return CampaignService(session).submit(campaign_id, principal.id, data.feedback)


@router.get("/submissions/me", response_model=list[SubmissionRead], tags=["submissions"])
def my_submissions(session: Db, principal: Tester, limit: Limit = 50, offset: Offset = 0):
    return CampaignRepository(session).for_tester(principal.id, limit, offset)


@router.get("/campaigns/{campaign_id}/submissions", response_model=list[SubmissionRead], tags=["submissions"])
def campaign_submissions(campaign_id: UUID, session: Db, principal: Builder,
                         limit: Limit = 50, offset: Offset = 0):
    service = CampaignService(session)
    service.require_owner(service.get(campaign_id), principal.id)
    return service.repo.for_campaign(campaign_id, limit, offset)
