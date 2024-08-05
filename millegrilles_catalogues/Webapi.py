import argparse
import pathlib
import json

from os import path
from typing import Optional

from millegrilles_messages.messages import Constantes
from millegrilles_messages.messages.EnveloppeCertificat import EnveloppeCertificat
from millegrilles_messages.messages.CleCertificat import CleCertificat
from millegrilles_messages.messages.FormatteurMessages import SignateurTransactionSimple, FormatteurMessageMilleGrilles

from millegrilles_catalogues.CleSignature import CleSignature


def signer_webapi(args: argparse.Namespace):
    path_fichier = pathlib.Path(args.path)
    if path_fichier.exists() is False:
        raise FileNotFoundError('Fichier de cle non trouve')

    cle = CleSignature.default()
    signer_fichier(path_fichier, cle)


def charger_cle(path_cle: Optional[pathlib.Path] = None, path_cert: Optional[pathlib.Path] = None,
                path_ca: Optional[pathlib.Path] = None) -> (CleCertificat, EnveloppeCertificat):

    if path_cle is None:
        path_cle = pathlib.Path(path.expanduser('~/.millegrilles/secrets/signing_key.pem'))

    if path_cert is None:
        path_cert = pathlib.Path(path.expanduser('~/.millegrilles/secrets/signing_cert.pem'))

    if path_ca is None:
        path_ca = pathlib.Path(path.expanduser('~/.millegrilles/secrets/signing_ca.pem'))

    cle_cert = CleCertificat.from_files(path_cle, path_cert)
    ca_cert = EnveloppeCertificat.from_file(str(path_ca))

    # Verifier la correspondance cle et certificat. raise Exception en cas de probleme.
    cle_cert.cle_correspondent()
    idmg_cert = cle_cert.enveloppe.idmg

    if ca_cert.idmg != idmg_cert:
        raise Exception('Mismatch CA et certificat de signature')

    roles = cle_cert.enveloppe.get_roles
    if 'webapi' not in roles or 'signature' not in roles:
        raise Exception('Certificat n\'a pas le role webapi et signature')

    return cle_cert, ca_cert


def signer_fichier(path_fichier: pathlib.Path, cle: CleSignature) -> dict:
    with open(path_fichier, 'rt') as fichier:
        data = json.load(fichier)

    clecert = cle.cle_cert
    ca_cert = cle.ca

    idmg = clecert.enveloppe.idmg
    signateur = SignateurTransactionSimple(clecert)
    formatteur = FormatteurMessageMilleGrilles(idmg, signateur, ca_cert)

    signed_api, message_id = formatteur.signer_message(Constantes.KIND_COMMANDE, data, 'webapi', action='configuration')
    signed_api['millegrille'] = ca_cert.certificat_pem

    print('\n------\n')
    print(json.dumps(signed_api, indent=2))
    print('\n------\n')

    return signed_api
