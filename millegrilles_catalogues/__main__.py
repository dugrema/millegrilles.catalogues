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
    elif args.command == 'signer':
        from millegrilles_catalogues.GenerateurCatalogues import Generateur
        generation = Generateur(args)
        generation.generer()
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

    subparser_signer = subparsers.add_parser('signer', help='Signer les catalogues')
    subparser_signer.add_argument('path', nargs='+', help='Repertoire ou fichier a signer')

    subparser_certificat = subparsers.add_parser('certificat', help='Generer un nouveau certificat de signature')
    subparser_certificat.add_argument('--output', help='Repertoire utilise pour conserver le certificat')
    subparser_certificat.add_argument('ca', help='Fichier de certificat CA')

    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    logger.debug("args : %s" % args)

    return args


if __name__ == '__main__':
    main()
