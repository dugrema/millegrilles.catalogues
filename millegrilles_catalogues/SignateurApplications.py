import json
import lzma
import logging
import argparse
import tarfile
import tempfile
import pathlib

from os import listdir, path, mkdir, unlink
from base64 import b64encode

from millegrilles_messages.messages import Constantes
from millegrilles_messages.messages.CleCertificat import CleCertificat
from millegrilles_messages.messages.FormatteurMessages import SignateurTransactionSimple, FormatteurMessageMilleGrilles
from millegrilles_messages.messages.EnveloppeCertificat import EnveloppeCertificat

from millegrilles_catalogues.CleSignature import CleSignature


class Generateur:

    def __init__(self, args: argparse.Namespace):
        self.__logger = logging.getLogger(__name__ + '.' + self.__class__.__name__)

        self.__cle_signature = CleSignature.default()
        cle_cert = self.__cle_signature.cle_cert
        idmg = cle_cert.enveloppe.idmg
        signateur = SignateurTransactionSimple(cle_cert)
        self.__formatteur = FormatteurMessageMilleGrilles(idmg, signateur, self.__cle_signature.ca)

        self.__repertoire_src = pathlib.Path(args.path)
        output_path = args.output or '.'
        self.__repertoire_signed = pathlib.Path(output_path)

        # Information de signature
        self.__logger.info("Utilisation idmg %s pour signer les catalogues" % idmg)
        self.__logger.info("Certificat %s expiration %s" % (cle_cert.fingerprint, cle_cert.enveloppe.not_valid_after))

    def generer_catalogue_applications(self):
        """
        Genere les fichiers de configuration d'application et le fichier de catalogue d'applications
        :return:
        """
        path_catalogues = self.__repertoire_src
        path_archives_application = self.__repertoire_signed

        try:
            mkdir(path_archives_application)
        except FileExistsError:
            pass

        catalogue_apps = dict()
        for rep, config in IterateurApplications(path_catalogues):
            nom_application = config['nom']
            self.__logger.debug("Repertoire : %s" % rep)
            catalogue_apps[nom_application] = {
                'version': config['version']
            }

            # Verifier si on doit creer une archive tar pour cette application
            # Tous les fichiers sauf docker.json sont inclus et sauvegarde sous une archive tar.xz
            # dans l'entree de catalogue
            try:
                script_files = config['scripts']
            except KeyError:
                pass
            else:
                fpconfig, path_config_temp = tempfile.mkstemp()
                try:
                    with tarfile.open(path_config_temp, 'w:xz') as fichier:
                        for filename in script_files:
                            file_path = path.join(rep, filename)
                            fichier.add(file_path, arcname=filename)

                    # Lire fichier .tar, convertir en base64
                    with open(path_config_temp, 'rb') as fichier:
                        contenu_tar_b64 = b64encode(fichier.read())

                    config['scripts_content'] = contenu_tar_b64.decode('utf-8')
                finally:
                    unlink(path_config_temp)  # Cleanup fichier temporaire

            # fichier_app = [f for f in listdir(rep) if f not in ['docker.json']]
            try:
                conf_files = config['nginx']['conf']
                dict_conf_files = dict()
                for conf_file in conf_files:
                    path_conf = path.join(rep, conf_file)
                    with open(path_conf, 'r') as fichier:
                        contenu = fichier.read()
                    dict_conf_files[conf_file] = contenu

                config['nginx']['conf'] = dict_conf_files
            except KeyError:
                pass

            # Preparer archive .json.xz avec le fichier de configuration signe et les scripts
            config = self.signer(config, 'CoreCatalogues', 'catalogueApplication')
            path_archive_application = path.join(path_archives_application, nom_application + '.json.xz')
            with lzma.open(path_archive_application, 'wt') as output:
                json.dump(config, output)

        # catalogue = {
        #     'applications': catalogue_apps
        # }
        # catalogue = self.signer(catalogue, 'CoreCatalogues', 'catalogueApplications')
        #
        # # Exporter fichier de catalogue
        # path_output = path.join(path_catalogues, 'generes', 'catalogue.applications.json.xz')
        # with lzma.open(path_output, 'wt') as output:
        #     json.dump(catalogue, output)

    def signer(self, contenu: dict, domaine_action: str, action: str = None):
        message_signe, uuid_enveloppe = self.__formatteur.signer_message(
            Constantes.KIND_COMMANDE, contenu, domaine_action, ajouter_chaine_certs=True, action=action)

        # Ajouter certificat _millegrille
        message_signe['millegrille'] = self.__cle_signature.ca_pem

        return message_signe

    def generer(self):
        self.generer_catalogue_applications()


class IterateurApplications:

    def __init__(self, path_catalogue='.'):
        self.__path_catalogue = path_catalogue
        self.__logger = logging.getLogger(__name__ + '.' + self.__class__.__name__)

        self.__liste = None
        self.__termine = False

    def __iter__(self):
        liste = listdir(self.__path_catalogue)
        self.__iter = liste.__iter__()
        return self

    def __next__(self):
        nom_item = self.__iter.__next__()
        path_item = path.join(self.__path_catalogue, nom_item)

        while not path.isdir(path_item):
            nom_item = self.__iter.__next__()
            path_item = path.join(self.__path_catalogue, nom_item)

        # Charger fichier docker.json
        with open(path.join(path_item, 'docker.json'), 'r') as fichier:
            config = json.load(fichier)

        return path_item, config
