import json
import argparse
import pathlib


def traiter_fichier(fichier: pathlib.Path):
    images = []
    with fichier.open(mode='rt') as fichier:
        contenu = json.load(fichier)

    print('Contenu : %s' % contenu)
    try:
        images.append(contenu['image'])
    except KeyError:
        pass

    try:
        dependances = contenu['dependances']
    except KeyError:
        pass
    else:
        for d in dependances:
            try:
                images.append(d['image'])
            except KeyError:
                pass

    return images


def lire_images(params):
    fichiers = params.fichiers
    repertoire = params.repertoire
    catalogues = params.catalogues

    images = []

    print("Fichiers a traiter : %s" % fichiers)
    if repertoire:
        repertoire_path = pathlib.Path(repertoire)
        for fichier in repertoire_path.iterdir():
            if fichier.name.endswith('.json'):
                images_fichier = traiter_fichier(fichier)
                images.extend(images_fichier)

    if catalogues:
        repertoire_path = pathlib.Path(catalogues)
        for item in repertoire_path.iterdir():
            if item.is_dir():
                path_fichier = pathlib.Path(item, 'docker.json')
                images_fichier = traiter_fichier(path_fichier)
                images.extend(images_fichier)

    if fichiers:
        for fichier in fichiers:
            images_fichier = traiter_fichier(pathlib.Path(fichier))
            images.extend(images_fichier)

    print("Images trouvees : %s" % images)
    return images


def conserver_output(fichier: pathlib.Path, images: list):
    with fichier.open(mode='wt') as foutput:
        for image in images:
            foutput.write(image)
            foutput.write(' ')


def lire_params():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fichiers", type=str, nargs='+', required=False, help="Nom du fichier a traiter")
    parser.add_argument("-d", "--repertoire", type=str, required=False, help="Nom du repertoire a traiter (*.json)")
    parser.add_argument("-c", "--catalogues", type=str, required=False, help="Nom du repertoire de catalogues (*/docker.json)")
    parser.add_argument("-o", "--output", type=str, help="Nom du fichier output")
    return parser.parse_args()


def main():
    params = lire_params()
    images = lire_images(params)
    if params.output:
        conserver_output(pathlib.Path(params.output), images)


if __name__ == '__main__':
    main()