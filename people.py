

"""
This is the people module and supports all the REST actions for the
people data
"""

from flask import make_response, abort
from config import db
from models import Person, PersonSchema


def read_all():
    """
    This function responds to a request for /api/people
    with the complete lists of people
    :return:        json string of list of people
    """
    # Create the list of people from our data
    people = Person.query.order_by(Person.lname).all()

    # Serialize the data for the response
    person_schema = PersonSchema(many=True)
    data = person_schema.dump(people).data
    return data


def read_one(person_id):
    """
    This function responds to a request for /api/people/{person_id}
    with one matching person from people
    :param person_id:   Id of person to find
    :return:            person matching id
    """
    # Get the person requested
    person = Person.query.filter(Person.person_id == person_id).one_or_none()

    # Did we find a person?
    if person is not None:

        # Serialize the data for the response
        person_schema = PersonSchema()
        data = person_schema.dump(person).data
        return data

    # Otherwise, nope, didn't find that person
    else:
        abort(
            404,
            "Person not found for Id: {person_id}".format(person_id=person_id),
        )


def create(person):
    """
    This function creates a new person in the people structure
    based on the passed in person data
    :param person:  person to create in people structure
    :return:        201 on success, 406 on person exists
    """
    fname = person.get("fname")
    lname = person.get("lname")

    existing_person = (
        Person.query.filter(Person.fname == fname)
        .filter(Person.lname == lname)
        .one_or_none()
    )

    # Can we insert this person?
    if existing_person is None:

        # Create a person instance using the schema and the passed in person
        schema = PersonSchema()
        new_person = schema.load(person, session=db.session).data

        # Add the person to the database
        db.session.add(new_person)
        db.session.commit()

        # Serialize and return the newly created person in the response
        data = schema.dump(new_person).data

        return data, 201

    # Otherwise, nope, person exists already
    else:
        abort(
            409,
            "Person {fname} {lname} exists already".format(
                fname=fname, lname=lname
            ),
        )


def update(person_id, person):
    """
    This function updates an existing person in the people structure
    Throws an error if a person with the name we want to update to
    already exists in the database.
    :param person_id:   Id of the person to update in the people structure
    :param person:      person to update
    :return:            updated person structure
    """
    # Get the person requested from the db into session
    update_person = Person.query.filter(
        Person.person_id == person_id
    ).one_or_none()

    # Try to find an existing person with the same name as the update
    fname = person.get("fname")
    lname = person.get("lname")

    existing_person = (
        Person.query.filter(Person.fname == fname)
        .filter(Person.lname == lname)
        .one_or_none()
    )

    # Are we trying to find a person that does not exist?
    if update_person is None:
        abort(
            404,
            "Person not found for Id: {person_id}".format(person_id=person_id),
        )

    # Would our update create a duplicate of another person already existing?
    elif (
        existing_person is not None and existing_person.person_id != person_id
    ):
        abort(
            409,
            "Person {fname} {lname} exists already".format(
                fname=fname, lname=lname
            ),
        )

    # Otherwise go ahead and update!
    else:

        # turn the passed in person into a db object
        schema = PersonSchema()
        update = schema.load(person, session=db.session).data

        # Set the id to the person we want to update
        update.person_id = update_person.person_id

        # merge the new object into the old and commit it to the db
        db.session.merge(update)
        db.session.commit()

        # return updated person in the response
        data = schema.dump(update_person).data

        return data, 200


def delete(person_id):
    """
    This function deletes a person from the people structure
    :param person_id:   Id of the person to delete
    :return:            200 on successful delete, 404 if not found
    """
    # Get the person requested
    person = Person.query.filter(Person.person_id == person_id).one_or_none()

    # Did we find a person?
    if person is not None:
        db.session.delete(person)
        db.session.commit()
        return make_response(
            "Person {person_id} deleted".format(person_id=person_id), 200
        )

    # Otherwise, nope, didn't find that person
    else:
        abort(
            404,
            "Person not found for Id: {person_id}".format(person_id=person_id),
        )
