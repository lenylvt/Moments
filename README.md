# YouVersion Moments avec Tags IA

Ce projet récupère automatiquement vos moments (notes) depuis l'API YouVersion, remplit les textes bibliques, et génère des tags intelligents via IA.

## 🚀 Fonctionnalités

- � **Récupération automatique** des moments YouVersion via API
- � **Textes bibliques** automatiquement récupérés et ajoutés
- 🏷️ **Tags IA** générés via l'API 1min.ai avec 42 tags prédéfinis
- 🕐 **Exécution automatique** quotidienne via GitHub Actions
- � **Sécurisé** avec variables d'environnement pour les clés API
- 📄 **Format JSON** structuré et optimisé

## 📁 Structure du projet

```
.
├── .github/workflows/
│   └── fetch-moments.yml    # GitHub Action workflow
├── scripts/
│   ├── fetch_moments.py     # Script principal de récupération
│   ├── fill_bible_texts.py # Remplissage des textes bibliques
│   └── generate_tags.py     # Génération des tags IA
├── .env.example            # Exemple de configuration
├── .env                    # Configuration (non versionnée)
├── requirements.txt        # Dépendances Python
├── moments.json           # Données générées
└── README.md             # Ce fichier
```

## ⚙️ Configuration

### 1. Variables d'environnement

Copiez `.env.example` vers `.env` et remplissez les valeurs :

```bash
cp .env.example .env
```

Variables requises :
- `ONEMIN_AI_API_KEY` : Clé API pour 1min.ai (génération de tags)
- `YOUVERSION_BEARER_TOKEN` : Token d'authentification YouVersion
- `BIBLE_API_BEARER_TOKEN` : Token pour l'API Bible (si nécessaire)

### 2. Installation des dépendances

```bash
pip install -r requirements.txt
```

## 🎯 Tags disponibles (42 tags)

Le système utilise 42 tags prédéfinis pour catégoriser les moments :

**Spiritualité :** `priere`, `discipulat`, `obeissance`, `esperance`, `gratitude`, `pardon`, `perseverance`

**Défis personnels :** `courage`, `tentation`, `humilite`, `colere`, `orgueil`, `convoitise`, `jalousie`

**Relations :** `famille`, `mariage`, `amitie`, `conflit`, `trahison`, `service`, `autorite`

**Sagesse :** `paroles`, `discernement`, `discipline`, `mensonge`, `hypocrisie`, `fausseDoctrine`

**Société :** `richesse`, `travail`, `justice`, `pauvres`, `persecution`, `ivresse`

**Épreuves :** `maladie`, `solitude`, `mort`, `avenir`, `vaincreMal`, `esperer`

**Créat. & Corp :** `creation`, `organe`, `sexualite`, `idolatrie`

## 🔄 Utilisation

### Exécution manuelle complète

```bash
cd scripts
python fetch_moments.py  # Récupère + textes bibliques + tags IA
```

### Exécution par étapes

```bash
# 1. Récupération des moments seulement
cd scripts  
python fetch_moments.py

# 2. Ajout des textes bibliques
python fill_bible_texts.py

# 3. Génération des tags IA
python generate_tags.py
```

## 📊 Format des données

### Structure JSON générée

```json
{
  "moments": [
    {
      "content": "Seigneur, aide-moi à avoir confiance en toi...",
      "color": "#4ECDC4",
      "references": [
        {
          "usfm": [1130023001],
          "version_id": 133,
          "human": "Proverbes 3:5",
          "human_text": "Confie-toi en l'Éternel de tout ton cœur..."
        }
      ],
      "tag": ["priere", "confiance"]
    }
  ],
  "last_updated": "2025-09-21T12:00:00Z",
  "last_update": "2025-09-21T08:15:30Z",
  "total_moments": 125,
  "colors_used": ["#4ECDC4", "#FF6B6B", "#96CEB4"],
  "tags_used": ["priere", "courage", "gratitude"],
  "total_tags_available": 42,
  "last_tag_update": "2025-09-21T12:00:00Z"
}
```

### Champs expliqués

- **moments** : Liste des moments (plus récents en premier)
  - `content` : Contenu de la note/highlight
  - `color` : Couleur hexadécimale
  - `references` : Références bibliques avec texte complet
  - `tag` : Liste des tags IA (max 2, préférence 1)
- **Métadonnées** : Statistiques et dates de mise à jour
- **tags_used** : Liste des tags utilisés dans cette session
- **total_tags_available** : Nombre total de tags prédéfinis (42)

## 🤖 IA et Tags

### Fonctionnement

1. **Analyse du contenu** : L'IA analyse le moment + texte biblique
2. **Sélection intelligente** : Choix parmi les 42 tags prédéfinis uniquement
3. **Préférence qualité** : 1 tag précis > 2 tags moins pertinents
4. **Validation** : Vérification que les tags existent dans la liste

### Première exécution

Au premier run, le système :
- Affiche tous les tags disponibles
- Les sauvegarde dans le JSON pour référence
- Génère les tags pour tous les moments

## 🔧 GitHub Actions

### Configuration secrets

Ajoutez dans les secrets du repository :
- `ONEMIN_AI_API_KEY`
- `YOUVERSION_BEARER_TOKEN` 
- `BIBLE_API_BEARER_TOKEN`

### Workflow automatique

- ⏰ Exécution quotidienne à minuit UTC
- 🔧 Déclenchement manuel possible
- 📤 Commit automatique des changements
- 🏷️ Génération complète : moments → textes → tags

## 🔐 Sécurité

- ✅ Clés API externalisées dans `.env`
- ✅ `.env` exclu du versioning
- ✅ Variables d'environnement pour GitHub Actions
- ✅ Validation des tokens avant utilisation

## 🛠️ Maintenance

### Mise à jour des tokens

Si erreur 401/403, mettez à jour les tokens dans :
- Fichier `.env` (local)
- Secrets GitHub Actions (production)

### Ajout de nouveaux tags

Pour ajouter des tags, modifiez la liste `predefined_tags` dans `scripts/generate_tags.py`.

## 📝 Logs et Debug

Le système affiche :
- ✅ Moments récupérés et traités
- 📖 Textes bibliques ajoutés  
- 🏷️ Tags générés par l'IA
- ⚠️ Erreurs et avertissements
- 📊 Statistiques finales
