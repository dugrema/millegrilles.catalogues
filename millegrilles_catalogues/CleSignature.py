from os.path import expanduser
import pathlib

from typing import Optional

from millegrilles_messages.messages.EnveloppeCertificat import EnveloppeCertificat
from millegrilles_messages.messages.CleCertificat import CleCertificat


class CleSignature:

    def __init__(self):
        self.cle_cert: Optional[CleCertificat] = None
        self.ca: Optional[EnveloppeCertificat] = None
        self.ca_pem: Optional[str] = None

    def charger_cle(self, path_cle: Optional[pathlib.Path] = None, path_cert: Optional[pathlib.Path] = None,
                    path_ca: Optional[pathlib.Path] = None) -> (CleCertificat, EnveloppeCertificat):

        if path_cle is None:
            path_cle = pathlib.Path(expanduser('~/.millegrilles/secrets/signing_key.pem'))

        if path_cert is None:
            path_cert = pathlib.Path(expanduser('~/.millegrilles/secrets/signing_cert.pem'))

        if path_ca is None:
            path_ca = pathlib.Path(expanduser('~/.millegrilles/secrets/signing_ca.pem'))

        cle_cert = CleCertificat.from_files(path_cle, path_cert)

        with open(path_ca, 'rt') as fichier:
            self.ca_pem = fichier.read()

        ca_cert = EnveloppeCertificat.from_pem(self.ca_pem)

        # Verifier la correspondance cle et certificat. raise Exception en cas de probleme.
        cle_cert.cle_correspondent()
        idmg_cert = cle_cert.enveloppe.idmg

        if ca_cert.idmg != idmg_cert:
            raise Exception('Mismatch CA et certificat de signature')

        roles = cle_cert.enveloppe.get_roles
        if 'webapi' not in roles or 'signature' not in roles:
            raise Exception('Certificat n\'a pas le role webapi et signature')

        self.ca = ca_cert
        self.cle_cert = cle_cert

        return cle_cert, ca_cert

    @staticmethod
    def default():
        cle = CleSignature()
        cle.charger_cle()
        return cle
