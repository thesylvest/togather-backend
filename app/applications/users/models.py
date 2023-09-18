from tortoise.expressions import Q
from tortoise import fields

from app.core.base.models import BaseCreatedAtModel, LocationModel, BaseDBModel, MediaModel
from app.core.auth.utils import password


class User(BaseDBModel, BaseCreatedAtModel, LocationModel, MediaModel):
    class Meta:
        table = "users"

    class PydanticMeta:
        backward_relations = False
        exclude = [
            "password_hash",
            "clubs",
            "hosted_events",
            "attended_events",
            "places",
            "notifications",
            "is_superuser",
            "is_active",
            "unread_notifications",
            "blocked_users",
            "blocked_by",
            "latitude",
            "longitude"
        ]
        computed = ["media"]
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=255, unique=True)
    first_name = fields.CharField(max_length=50, null=True)
    last_name = fields.CharField(max_length=50, null=True)
    password_hash = fields.CharField(max_length=60, null=True)
    last_login = fields.DatetimeField(null=True)
    is_active = fields.BooleanField(default=True)
    bio = fields.TextField(null=True)
    gender = fields.CharField(max_length=10, null=True)
    social_links = fields.JSONField(null=True)
    birth_date = fields.DateField(null=True)
    unread_notifications = fields.IntField(default=0)
    private_profile = fields.BooleanField(default=False)
    is_verified = fields.BooleanField(default=False)

    sent_connections: fields.ReverseRelation
    received_connections: fields.ReverseRelation
    posts: fields.ReverseRelation
    comments: fields.ReverseRelation
    form_responses: fields.ReverseRelation
    reports: fields.ReverseRelation
    hides: fields.ReverseRelation
    devices: fields.ReverseRelation
    memberships: fields.ReverseRelation
    hosted_events: fields.ManyToManyRelation
    attended_events: fields.ManyToManyRelation
    places: fields.ManyToManyRelation
    notifications: fields.ManyToManyRelation
    clubs: fields.ManyToManyRelation
    interests: fields.ManyToManyRelation
    blocked_by: fields.ManyToManyRelation

    university: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.University", related_name="students", null=True
    )
    blocked_users: fields.ManyToManyRelation = fields.ManyToManyField(
        "models.User", related_name="blocked_by", through="blocked", backward_key="blocking_user_id", forward_key="blocked_user_id"
    )

    async def connection_status(self, user):
        if self == user:
            return Connection.Status.me
        connection = await Connection.get_or_none(
            Q(from_user=user, to_user=self) | Q(from_user=self, to_user=user)
        ).prefetch_related("from_user", "to_user")
        if connection:
            if connection.is_accepted:
                return Connection.Status.connected
            return Connection.Status.request_sent if connection.from_user == self else Connection.Status.request_received
        return Connection.Status.not_connected

    @classmethod
    async def create(cls, user) -> "User":
        user_dict = user.dict()
        password_hash = password.get_password_hash(password=user.password)
        model = cls(**user_dict, password_hash=password_hash)
        await model.save()
        return model


class Connection(BaseDBModel):
    class Status:
        me = -1
        not_connected = 0
        request_sent = 1
        request_received = 2
        connected = 3

    class Meta:
        table = "connections"
    is_accepted = fields.BooleanField(default=False)

    from_user: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="sent_connections"
    )
    to_user: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="received_connections"
    )


class University(BaseDBModel, LocationModel):
    class Meta:
        table = "universities"
    name = fields.CharField(max_length=255, unique=True)

    class PydanticMeta:
        backward_relations = False
    clubs: fields.ReverseRelation
    students: fields.ReverseRelation
    events: fields.ReverseRelation


class Blocked(BaseDBModel):
    class Meta:
        table = "blocked"
    blocking_user: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="blocking"
    )
    blocked_user: fields.ForeignKeyRelation = fields.ForeignKeyField(
        "models.User", related_name="blocked"
    )
