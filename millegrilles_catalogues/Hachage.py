import argparse
import binascii
import pathlib

from millegrilles_messages.messages.Hachage import Hacheur

CHUNK_SIZE = 1024 * 64


def hacher_fichier(args: argparse.Namespace):
    file_path = pathlib.Path(args.filepath)
    if file_path.exists() is False:
        raise FileNotFoundError('Fichier non trouve')
    if file_path.is_file() is False:
        raise Exception('Path fourni n\'est pas un fichier')

    algo_name = args.name
    encoding = args.encoding
    if encoding == 'hex':
        encoding = 'base16'

    digest = traiter(file_path, algo_name, encoding)
    print('Digest: %s' % digest)


def traiter(file_path: pathlib.Path, algo: str, encoding: str) -> str:

    hacheur = Hacheur(algo, encoding)

    with file_path.open('rb') as fichier:
        chunk = fichier.read(64*1024)
        while chunk:
            hacheur.update(chunk)
            chunk = fichier.read(64*1024)

    digest = hacheur.finalize()[1:]  # Retirer encodage multibase

    return digest
