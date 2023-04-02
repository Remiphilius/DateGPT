# DateGPT

Ce programme permet de faire se parler ChatGPT avec lui-même.

## Prérequis

Pour faire fonctionner le programme, vous devez stocker votre clé API OpenAI dans un fichier `.env` sous cette forme :

```
OPENAI_API_KEY = "API_KEY"
```

## Personnalisation

Vous pouvez modifier le comportement de chaque individu avec la prompt system dans le fichier main_date.py au niveau des variables `user0sys` et `user1sys`.

J'ai mis ces comportements là parce qu'il s'avère que ce sont eux qui donnent les résultats les plus drôles mais libre à vous de les modifier : tout est possible !

