from flask import abort
from flask.ext.login import login_required
import sqlalchemy.orm as orm
from webargs import fields
from webargs.flaskparser import use_args

from bauble.controllers.api import api
import bauble.db as db
from bauble.middleware import use_model
from bauble.models import Accession, Collection, Propagation, Source, Taxon
import bauble.utils as utils


@api.route("/accession")
@login_required
def index_accession():
    accession = Accession.query.all()
    data = Accession.jsonify(accession, many=True)
    return utils.json_response(data)


@api.route("/accession/<int:id>")
@login_required
@use_model(Accession)
def get_accession(accession, id):
    return utils.json_response(accession.jsonify())


@api.route("/accession/<int:id>", methods=['PATCH'])
@login_required
@use_model(Accession)
def patch_accession(accession, id):
    # if 'source' in request.json:
    #     if request.accession.source is None:
    #         request.accession.source = Source()
    #     source = request.accession.source  # shorthand

    #     source_json = request.json['source']
    #     source_data = {col: source_json[col] for col in source_json.keys()
    #                    if col in source_mutable}
    #     source_data['source_detail_id'] = source_data.pop('id', None)

    #     # make a copy of the data for only those fields that are columns
    #     source.set_attributes(source_data)

    #     # make sure the propagation type is not empty b/c we'll get an error
    #     # trying to set the propagation details (even if it's an empty dict) if
    #     # the prop_type hasn't been set
    #     if 'propagation' in source_json and len(source_json['propagation']) > 0:
    #         # TODO: validate prop_type
    #         if source.propagation is None:
    #             source.propagation = Propagation()

    #         prop_data = source_json['propagation']
    #         source.propagation.prop_type = prop_data.pop('prop_type', source.propagation.prop_type)
    #         prop_mutable = prop_seed_mutable if source.propagation.prop_type == 'Seed' \
    #             else prop_cutting_mutable
    #         source.propagation.details = {col: prop_data[col] for col in prop_data.keys()
    #                                       if col in prop_mutable}

    #     if 'collection' in source_json and len(source_json['collection']) > 0:
    #         # TODO: validate collection datand set mutable properties
    #         if source.collection is None:
    #             source.collection = Collection()
    #         coll_data = {col: value for col, value in source_json['collection'].items()
    #                      if col in coll_mutable}
    #         source.collection.set_attributes(coll_data)
    db.session.commit()
    return utils.json_response(accession.jsonify())


@api.route("/accession", methods=['POST'])
@login_required
@use_model(Accession)
def post_accession(accession):
    taxon = Taxon.query.filter_by(id=accession.taxon_id).first()
    if not taxon:
        abort(422, "Invalid taxon id")

    # if 'source' in request.json:
    #     source_json = request.json['source']
    #     source_data = {col: source_json[col] for col in source_json.keys()
    #                    if col in source_mutable}
    #     source_data['source_detail_id'] = source_data.pop('id', None)

    #     # make a copy of the data for only those fields that are columns
    #     source = Source(**source_data)
    #     request.session.add(source)

    #     if 'propagation' in source_json:
    #         # TODO: validate prop_type
    #         prop_data = source_json['propagation']
    #         propagation = Propagation(prop_type=prop_data.pop('prop_type'))
    #         prop_mutable = prop_seed_mutable if propagation.prop_type == 'Seed' \
    #             else prop_cutting_mutable

    #         propagation.details = {col: prop_data[col] for col in prop_data.keys()
    #                                if col in prop_mutable}
    #         source.propagation = propagation


    #     collection = Collection()
    #     if 'collection' in source_json:
    #         # TODO: validate collection datand set mutable properties
    #         coll_data = {col: value for col, value in source_json['collection'].items()
    #                      if col in coll_mutable}
    #         collection = Collection(**coll_data)
    #         source.collection = collection

    db.session.add(accession)
    db.session.commit()
    return utils.json_response(accession.jsonify(), 201)


@api.route("/accession/<int:id>", methods=['DELETE'])
@login_required
@use_model(Accession)
def delete_accession(accession, id):
    db.session.delete(accession)
    db.session.commit()
    return '', 204


@api.route("/accession/<int:id>/count")
@login_required
@use_args({
    'relation': fields.DelimitedList(fields.String(), required=True)
})
def accession_count(args, id):
    data = {}
    accession = Accession.query.get_or_404(id)
    for relation in args['relation']:
        _, base = relation.rsplit('/', 1)
        data[base] = utils.count_relation(accession, relation)
    return utils.json_response(data)
