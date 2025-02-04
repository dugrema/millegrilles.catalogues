import argparse
import pathlib

from millegrilles_messages.messages.Hachage import hacher_fichier

def parse() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Digests a file with blake2s, outputs digest text encoding")
    parser.add_argument('--name', default='blake2s-256', help='Digest algorithm: blake2s-256, blake2b-512')
    parser.add_argument('--encoding', default='base64', help='Output encoding: hex, base64, base58btc')
    parser.add_argument('filepath', help='File to digest')

    args = parser.parse_args()

    return args

def main(params: argparse.Namespace):
    file_path = pathlib.Path(args.filepath)
    if file_path.exists() is False:
        raise FileNotFoundError('Fichier non trouve')
    if file_path.is_file() is False:
        raise Exception('Path fourni n\'est pas un fichier')

    algo_name = params.name
    encoding = params.encoding
    if encoding == 'hex':
        encoding = 'base16'

    digest = hacher_fichier(str(file_path), algo_name, encoding)
    print('Digest: %s' % digest[1:])


if __name__ == '__main__':
    args = parse()
    main(args)
