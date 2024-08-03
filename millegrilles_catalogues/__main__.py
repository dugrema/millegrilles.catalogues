import argparse
import logging


def main():

    args = parse()
    if args.verbose:
        logging.getLogger('__main__').setLevel(logging.DEBUG)
        logging.getLogger('millegrilles').setLevel(logging.DEBUG)

    if args.command == 'certificat':
        from millegrilles_catalogues import Certificat
        Certificat.generer_certificat_signature(args)
    elif args.command == 'catalogues':
        from millegrilles_catalogues.GenerateurCatalogues import Generateur
        generation = Generateur(args)
        generation.generer()
    elif args.command == 'webapi':
        from millegrilles_catalogues.Webapi import signer_webapi
        signer_webapi(args)
    elif args.command == 'digest':
        from millegrilles_catalogues.Hachage import main as hacher_fichier
        hacher_fichier(args)
    else:
        raise Exception('Commande non supportee')


def parse():
    logger = logging.getLogger(__name__ + '.parse')
    parser = argparse.ArgumentParser(description="Utilitaire d'entretien des catalogues d'applications MilleGrilles")

    parser.add_argument(
        '--verbose', action="store_true", required=False,
        help="Active le logging maximal"
    )

    subparsers = parser.add_subparsers(dest='command', required=True, help="Commandes")

    subparser_certificat = subparsers.add_parser('certificat', help='Generer un nouveau certificat de signature')
    subparser_certificat.add_argument('--output', help='Repertoire utilise pour conserver le certificat')
    subparser_certificat.add_argument('ca', help='Fichier de certificat CA')

    subparser_signer = subparsers.add_parser('catalogues', help='Signer les catalogues')
    subparser_signer.add_argument('path', nargs='+', help='Repertoire ou fichier a signer')

    subparser_signer = subparsers.add_parser('webapi', help='Signer un fichier webapi')
    subparser_signer.add_argument('--output', help='Fichier utilise pour conserver l\'output')
    subparser_signer.add_argument('path', help='Fichier a signer')

    subparser_digest = subparsers.add_parser('digest', help='Hacher un fichier')
    subparser_digest.add_argument('--name', default='blake2s-256', help='Nom de l\'algorithme de hachage (blake2s-256, blake2b-512)')
    subparser_digest.add_argument('--encoding', default='base64', help='Encodage (hex, base64, base58btc) de l\'algorithme de hachage')
    subparser_digest.add_argument('filepath', help='Fichier a hacher')

    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.debug("args : %s" % args)

    return args


if __name__ == '__main__':
    main()
