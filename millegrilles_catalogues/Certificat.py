import argparse
import datetime
import json
import getpass
import pathlib

from os import makedirs, path
from typing import Optional
from cryptography.x509.base import CertificateBuilder

from millegrilles_messages.messages.CleCertificat import CleCertificat
from millegrilles_messages.certificats.Generes import ajouter_roles, CleCsrGenere


def generer_certificat_signature(args: argparse.Namespace):
    path_ca = pathlib.Path(args.ca)
    if path_ca.exists() is False:
        raise FileNotFoundError('Fichier de cle non trouve')

    clecert = charger_cle(path_ca)
    output_path = preparer_output_folder(args.output)
    cle_cert = generer_certificat(clecert)
    sauvegarder(cle_cert, output_path)


def charger_cle(path_ca: pathlib.Path) -> CleCertificat:

    if path_ca.name.endswith('.json'):
        with path_ca.open('rt') as fichier:
            cle_ca = json.load(fichier)
    else:
        raise Exception('Type de fichier de certificat non supporte')

    racine = cle_ca['racine']
    cle_chiffree = racine['cleChiffree']
    certificat = racine['certificat']

    pass_ca = getpass.getpass('Entrez le mot de passe du certificat CA :\n')

    cle_cert = CleCertificat.from_pems(cle_chiffree, certificat, pass_ca)

    # Verifier la correspondance cle et certificat. raise Exception en cas de probleme.
    cle_cert.cle_correspondent()

    return cle_cert


def preparer_output_folder(output: Optional[str]) -> pathlib.Path:

    if output is None:
        output = path.expanduser('~/.millegrilles/secrets')

    output_path = pathlib.Path(output)
    if output_path.exists() is False:
        makedirs(output_path)

    return output_path


def generer_certificat(cle_ca: CleCertificat) -> CleCertificat:
    builder = CertificateBuilder()

    idmg = cle_ca.enveloppe.idmg
    cle_csr_genere = CleCsrGenere.build(cn='Signature', idmg=idmg)

    roles = ['signature', 'catalogues', 'webapi']
    builder = ajouter_roles(builder, roles)

    not_valid_after = datetime.datetime.now() + datetime.timedelta(days=7)
    builder.not_valid_after(not_valid_after)

    certificat = cle_csr_genere.signer(cle_ca, builder=builder, role='signature')

    return certificat.clecertificat


def sauvegarder(certificat: CleCertificat, output: pathlib.Path):
    key_pem = certificat.private_key_bytes()
    cert_pem = certificat.enveloppe.certificat_pem

    key_path = pathlib.Path(output, 'signing_key.pem')
    cert_path = pathlib.Path(output, 'signing_cert.pem')

    with open(key_path, 'wb') as fichier:
        fichier.write(key_pem)

    with open(cert_path, 'wt') as fichier:
        fichier.write(cert_pem)

    print('Fichiers signing_key.pem et signing_cert.pem sauvegardes sous %s' % output)
