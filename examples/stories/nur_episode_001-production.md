# Nûr — Le signal · Préparation des médias

Les plans partagent une palette bleu nuit, des lumières ambre et un décor de science-fiction sobre. Dans les plans 2 et 3, reprendre le même poste et la même veste anthracite de l’opératrice. Cadrer en vertical 9:16.

| Fichier | Durée utile | Direction |
| --- | ---: | --- |
| plan-1.mp4 | 6 s | Plan large de la cité au crépuscule. Lent rapprochement. Quelques fenêtres ambre dans des bâtiments sombres. |
| plan-2.mp4 | 6 s | Gros plan fixe sur une radio analogique et son interrupteur. La main de l’opératrice, manche anthracite, se retire après le signal. |
| plan-3.mp4 | 8 s | Plan rapproché latéral. L’opératrice se penche vers le microphone du même poste. Une seconde main entre dans le cadre vers l’interrupteur. Coupe au noir en fin de plan. |

## Voix et effets

- Narration, de 0,5 à 5,5 s. Voix française calme. « En deux mille cent quarante-cinq, dix mille survivants se croyaient seuls. »
- Voix radio, de 13 à 18 s. Voix française distante, avec un léger filtrage radio. « Si quelqu’un nous entend… nous sommes encore là. »
- Exporter les deux répliques sur une piste `narration.wav`, avec les silences entre les prises.
- Exporter les trois impulsions espacées sur une piste `signal.wav`, sans silence en tête. Le montage la déclenche à 6 s.

## Montage

Placer `shots.json` à côté des trois clips.

```json
[
  {"source": "plan-1.mp4", "frames": 144},
  {"source": "plan-2.mp4", "frames": 144},
  {"source": "plan-3.mp4", "frames": 192}
]
```

Depuis la racine du dépôt, avec une constitution approuvée et les médias prêts.

```powershell
python -B workflows/video_factory/render.py constitution-approved.json shots.json narration.wav nur-le-signal.mp4 --subtitles captions.srt --cue signal.wav --cue-offset-ms 6000
```

Reprendre dans `captions.srt` les deux fenêtres de voix ci-dessus. Le fichier de sortie doit être nouveau.
