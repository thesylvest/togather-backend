from fastapi import APIRouter, Depends, HTTPException
from tortoise.expressions import Q

from app.core.auth.utils.contrib import get_current_active_user, get_current_active_user_optional
from .schemas import PostOut, PostCreate, PostUpdate, CommentOut, CommentCreate, CommentUpdate
from app.core.base.utils import get_object_or_404, has_permission
from app.applications.interactions.schemas import RateItem
from app.applications.interactions.models import Tag, Rate
from app.applications.organisations.models import Club
from app.applications.events.models import Event
from app.applications.users.models import User
from app.core.base.paginator import Paginator
from app.core.base.extractor import Extractor
from .utils import PostFilter, CommentFilter
from .models import Post, Comment


post_router = APIRouter()


@post_router.get("", tags=["posts"], status_code=200)
async def get_posts(
    paginator: Paginator = Depends(),
    current_user: User = Depends(get_current_active_user_optional),
    posts=Depends(PostFilter.dependency())
):
    return await paginator.paginate(posts, PostOut, current_user)


@post_router.get("/{id}", tags=["posts"])
async def get_post(
    id: int,
    current_user: User = Depends(get_current_active_user_optional),
):
    post = await get_object_or_404(Post, id=id)
    return await PostOut.serialize(post, current_user)


@post_router.post("", tags=["posts"])
async def create_post(
    data: PostCreate,
    current_user: User = Depends(get_current_active_user),
):
    if data.event_id:
        event = await get_object_or_404(Event, id=data.event_id)
        await has_permission(event.can_post, current_user)
    elif data.author_club_id:
        club = await get_object_or_404(Club, id=data.author_club_id)
        await has_permission(club.can_post, current_user)
    else:
        raise HTTPException(status_code=422, detail="At least an event or a club must specified")

    extractor = Extractor(data)
    urls, media_dict = extractor.media_files()
    post_dict = data.dict(exclude_none=True, exclude=["media"])
    post_dict["media_dict"] = media_dict

    post = await Post.create(**post_dict, creator=current_user)

    await Tag.bulk_create(
        Tag(name=name, item_id=post.id, item_type="Post") for name in data.tags
    )
    return {"created": await PostOut.serialize(post, current_user), "media_upload": urls}


@post_router.put("/{id}", tags=["posts"], status_code=200)
async def update_post(
    id: int,
    data: PostUpdate,
    current_user: User = Depends(get_current_active_user),
):
    post: Post = await get_object_or_404(Post, id=id)
    await has_permission(post.is_creator, current_user)

    extractor = Extractor(data)
    urls, media_dict = extractor.media_files()
    post_dict = data.dict(exclude_none=True, exclude=["media"])
    post_dict["media_dict"] = media_dict

    await post.update_from_dict(post_dict).save()

    if data.tags is not None:
        await Tag.filter(Q(item_id=id, item_type="Post") & ~Q(name__in=data.tags)).delete()
        for tag in data.tags:
            await Tag.get_or_create(name=tag, item_id=id, item_type="Post")
    return {"updated": await PostOut.serialize(post, current_user), "media_upload": urls}


@post_router.delete("/{id}", tags=["posts"], status_code=200)
async def delete_post(
    id: int,
    current_user: User = Depends(get_current_active_user),
):
    post: Post = await get_object_or_404(Post, id=id)
    await has_permission(post.is_creator, current_user)

    await post.delete()
    return post


@post_router.post("/{id}/rate", tags=["posts"], status_code=200)
async def rate_post(
    id: int,
    rate: RateItem,
    current_user: User = Depends(get_current_active_user),
):
    post: Post = await get_object_or_404(Post, id=id)
    try:
        rate_obj = await current_user.rates.get(item_id=post.id, item_type="Post")
        rate_obj.rate = rate.rate
        await rate_obj.save()
    except Exception:
        rate_obj = await Rate.create(item_id=post.id, item_type="Post", rate=rate.rate, rater=current_user)
    return rate_obj


comment_router = APIRouter()


@comment_router.get("", tags=["comments"])
async def get_comments(
    paginator: Paginator = Depends(),
    current_user: User = Depends(get_current_active_user_optional),
    comments=Depends(CommentFilter.dependency())
):
    return await paginator.paginate(comments, CommentOut, current_user)


@comment_router.get("/{id}", tags=["comments"])
async def get_comment(
    id: int,
    current_user: User = Depends(get_current_active_user_optional),
):
    comment = await get_object_or_404(Comment, id=id)
    return CommentOut.serialize(comment, current_user)


@comment_router.post("", tags=["comments"])
async def create_comment(
    data: CommentCreate,
    current_user: User = Depends(get_current_active_user),
):
    extractor = Extractor(data)
    urls, media_dict = extractor.media_files()
    comment_dict = data.dict(exclude_none=True, exclude=["media"])
    comment_dict["media_dict"] = media_dict

    comment: Comment = await Comment.create(**comment_dict, creator=current_user)

    await Tag.bulk_create(
        Tag(name=name, item_id=comment.id, item_type="Comment") for name in data.tags
    )
    return {"created": await CommentOut.serialize(comment, current_user), "media_upload": urls}


@comment_router.put("/{id}", tags=["comments"], status_code=200)
async def update_comment(
    id: int,
    data: CommentUpdate,
    current_user: User = Depends(get_current_active_user),
):
    comment: Comment = await get_object_or_404(Comment, id=id)
    await has_permission(comment.is_creator, current_user)

    extractor = Extractor(data)
    urls, media_dict = extractor.media_files()
    comment_dict = data.dict(exclude_none=True, exclude=["media"])
    comment_dict["media_dict"] = media_dict

    await comment.update_from_dict(comment_dict).save()

    if data.tags is not None:
        await Tag.filter(Q(item_id=id, item_type="Comment") & ~Q(name__in=data.tags)).delete()
        for tag in data.tags:
            await Tag.get_or_create(name=tag, item_id=id, item_type="Comment")
    return {"updated": await CommentOut.serialize(comment, current_user), "media_upload": urls}


@comment_router.delete("/{id}", tags=["comments"], status_code=200)
async def delete_comment(
    id: int,
    current_user: User = Depends(get_current_active_user),
):
    comment: Comment = await get_object_or_404(Comment, id=id)
    await has_permission(comment.is_creator, current_user)

    await comment.delete()
    return comment


@post_router.post("/{id}/rate", tags=["comments"], status_code=200)
async def rate_comment(
    id: int,
    rate: RateItem,
    current_user: User = Depends(get_current_active_user),
):
    comment: Comment = await get_object_or_404(Comment, id=id)
    try:
        rate_obj = await current_user.rates.get(item_id=comment.id, item_type="Comment")
        rate_obj.rate = rate.rate
        await rate_obj.save()
    except Exception:
        rate_obj = await Rate.create(item_id=comment.id, item_type="Comment", rate=rate.rate, rater=current_user)
    return rate_obj
