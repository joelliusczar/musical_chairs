from typing import Optional
from fastapi import APIRouter, Depends, Security, Query
from musical_chairs_libs.dtos import\
	TableData,\
	Tag,\
	AccountInfo,\
	UserRoleDef
from musical_chairs_libs.tag_service import TagService
from api_dependencies import \
	tag_service,\
	get_current_user

router = APIRouter(prefix="/tags")

@router.get("")
def get_tags(
	page: int = 0,
	pageSize: Optional[int]=None,
	stationId: Optional[int]=None,
	stationName: Optional[str]=None,
	tagIds: Optional[list[int]] = Query(default=None),
	tagService: TagService = Depends(tag_service),
) -> TableData[Tag]:
	totalRows = tagService.get_tags_count()
	items = list(tagService.get_tags(
		page=page,
		pageSize=pageSize,
		stationId=stationId,
		stationName=stationName,
		tagIds=tagIds
	))
	return TableData(totalRows=totalRows, items=items)

@router.post("")
def create_tag(
	tagName: str,
	tagService: TagService = Depends(tag_service),
	user: AccountInfo = Security(
		get_current_user,
		scopes=[UserRoleDef.TAG_EDIT()]
	)
) -> Tag:
	tag = tagService.save_tag(tagName, userId=user.id)
	return tag

@router.delete("")
def delete_tag(
	tagId: int,
	tagService: TagService = Depends(tag_service),
	user: AccountInfo = Security(
		get_current_user,
		scopes=[UserRoleDef.TAG_DELETE()]
	)
) -> int:
	return tagService.delete_tag(tagId)