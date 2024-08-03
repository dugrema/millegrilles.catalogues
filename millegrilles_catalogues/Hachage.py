import argparse
import pathlib

from millegrilles_messages.messages.Hachage import hacher_fichier


def main(args: argparse.Namespace):
    file_path = pathlib.Path(args.filepath)
    if file_path.exists() is False:
        raise FileNotFoundError('Fichier non trouve')
    if file_path.is_file() is False:
        raise Exception('Path fourni n\'est pas un fichier')

    algo_name = args.name
    encoding = args.encoding
    if encoding == 'hex':
        encoding = 'base16'

    digest = hacher_fichier(str(file_path), algo_name, encoding)
    print('Digest: %s' % digest[1:])
