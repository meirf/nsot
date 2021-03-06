import pytest
from sqlalchemy.exc import IntegrityError

from nsot import exc
from nsot import models

from .fixtures import session, site, user


def test_creation(session, site, user):
    models.NetworkAttribute.create(
        session, user.id,
        site_id=site.id, name="test_attribute"
    )
    session.commit()

    attributes = session.query(models.NetworkAttribute).all()
    assert len(attributes) == 1
    assert attributes[0].id == 1
    assert attributes[0].site_id == site.id
    assert attributes[0].name == "test_attribute"
    assert attributes[0].required == False


def test_conflict(session, site, user):
    models.NetworkAttribute.create(
        session, user.id,
        site_id=site.id, name="test_attribute"
    )

    with pytest.raises(IntegrityError):
        models.NetworkAttribute.create(
            session, user.id,
            site_id=site.id, name="test_attribute"
        )

    models.NetworkAttribute.create(
        session, user.id,
        site_id=site.id, name="test_attribute_2"
    )


def test_validation(session, site, user):
    with pytest.raises(exc.ValidationError):
        models.NetworkAttribute.create(
            session, user.id,
            site_id=site.id, name=None,
        )

    with pytest.raises(exc.ValidationError):
        models.NetworkAttribute.create(
            session, user.id,
            site_id=site.id, name="",
        )

    attribute = models.NetworkAttribute.create(
        session, user.id,
        site_id=site.id, name="test_attribute"
    )

    with pytest.raises(exc.ValidationError):
        attribute.update(user.id, name="")

    with pytest.raises(exc.ValidationError):
        attribute.update(user.id, name=None)

    attribute.update(user.id, name="test_attribute_new")
    session.commit()


def test_deletion(session, site, user):
    attribute = models.NetworkAttribute.create(
        session, user.id,
        site_id=site.id, name="test_attribute"
    )

    network = models.Network.create(
        session, user.id, site.id,
        cidr=u"10.0.0.0/8", attributes={"test_attribute": "foo"}
    )

    with pytest.raises(IntegrityError):
        attribute.delete(user.id)

    network.delete(user.id)
    attribute.delete(user.id)

def test_required(session, site, user):
    attribute_1 = models.NetworkAttribute.create(
        session, user.id,
        site_id=site.id, name="required_1", required=True
    )

    attribute_2 = models.NetworkAttribute.create(
        session, user.id,
        site_id=site.id, name="required_2", required=True
    )

    with pytest.raises(exc.ValidationError):
        network = models.Network.create(
            session, user.id, site.id,
            cidr=u"10.0.0.0/8"
        )

    with pytest.raises(exc.ValidationError):
        network = models.Network.create(
            session, user.id, site.id,
            cidr=u"10.0.0.0/8", attributes={
                "required_1": "foo",
            }
        )

    network = models.Network.create(
        session, user.id, site.id,
        cidr=u"10.0.0.0/8", attributes={
            "required_1": "foo",
            "required_2": "bar",
        }
    )
