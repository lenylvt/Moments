# YouVersion Moments Fetcher

Ce projet récupère automatiquement vos moments (notes) depuis l'API YouVersion et les sauvegarde dans un fichier JSON.

## Fonctionnalités

- 🕐 Exécution automatique quotidienne à minuit UTC via GitHub Actions
- 📝 Filtrage automatique des notes (`kind_id: "note.v1"`) et highlights (`kind_id: "highlight.v1"`)
- 📄 Sauvegarde au format JSON avec les champs demandés :
  - `content` : Le contenu de la note/highlight
  - `color` : La couleur associée
  - `references` : Les références bibliques
  - `tag` : Champ de tag (actuellement vide)
- 🔄 Gestion de la pagination pour récupérer toutes les notes et highlights
- 📅 Suivi de la date de dernière note pour éviter les doublons
- 🎨 Liste des couleurs utilisées dans les moments
- 🚀 Push automatique vers le repository GitHub

## Structure du projet

```
.
├── .github/workflows/
│   └── fetch-moments.yml    # GitHub Action workflow
├── scripts/
│   └── fetch_moments.py     # Script Python principal
├── moments.json            # Fichier de données généré
├── last_update.txt         # Date de dernière mise à jour
└── README.md              # Ce fichier
```

## Configuration

Le script est configuré pour l'utilisateur ID `224177359`. Pour changer d'utilisateur, modifiez la variable `user_id` dans `scripts/fetch_moments.py`.

⚠️ **Important** : Le script utilise un token d'authentification Bearer dans les en-têtes. Ce token a une durée de validité limitée et devra être mis à jour périodiquement. Si vous obtenez une erreur 401 ou 403, vérifiez et mettez à jour le token dans la variable `headers['Authorization']` du script.

## Exécution manuelle

Pour tester le script localement :

```bash
cd scripts
python fetch_moments.py
```

### Mise à jour du token d'authentification

Si le token expire (erreur 401/403), utilisez le script de mise à jour :

```bash
cd scripts
python update_token.py "votre_nouveau_token_bearer"
```

Pour obtenir un nouveau token, inspectez les requêtes réseau dans l'app YouVersion et copiez le Bearer token de l'en-tête `Authorization`.

## Format des données

Le fichier `moments.json` généré contient :

```json
{
  "moments": [
    {
      "content": "ne provoquons pas Dieu...",
      "color": "ffc66f",
      "references": [
        {
          "usfm": ["MAT.4.7"],
          "version_id": 133,
          "human": "Matthieu 4:7"
        }
      ],
      "tag": ""
    }
  ],
  "last_updated": "2025-09-20T00:00:00+00:00",
  "last_update": "2025-08-26T15:09:17.304000+00:00",
  "total_moments": 1,
  "colors_used": ["ffc66f", "ff95ef", "beffaa"]
}
```

### Explication des champs

- **moments** : Liste des moments/notes récupérés (triés par date décroissante, plus récents en premier)
  - `content` : Le contenu de la note/highlight
  - `color` : La couleur hexadécimale associée
  - `references` : Les références bibliques avec format USFM et texte lisible
  - `tag` : Champ de tag (actuellement vide)
- **last_updated** : Horodatage de la dernière exécution du script  
- **last_update** : Date de création de la dernière note récupérée (utilisée pour éviter les doublons)
- **total_moments** : Nombre total de moments dans le fichier
- **colors_used** : Liste des couleurs hexadécimales utilisées dans les moments

## GitHub Action

L'action s'exécute automatiquement :
- ⏰ Quotidiennement à minuit UTC
- 🔧 Peut être déclenchée manuellement via l'interface GitHub
- 📤 Commit et push automatique des changements

## Permissions requises

La GitHub Action nécessite les permissions :
- `contents: write` pour pouvoir pousser les modifications
