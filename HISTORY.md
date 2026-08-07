# Qalam Studio History

Ce document retrace les étapes importantes de l'évolution de Qalam Studio Engine.

---

## 2026-08-07

### Sprint 2 — Core Domain Model v0.1

#### 🎯 Objectif

Définir le langage métier de Qalam Studio avant toute implémentation des moteurs.

#### ✅ Réalisé

- Création de `project_rule.schema.json`
- Création de `project_rule_assignment.schema.json`
- Séparation entre la définition d'une règle et son application à un projet
- Première fondation du Rule Engine

#### Décisions d'architecture

- Une règle est réutilisable et indépendante de tout projet.
- Un projet applique des règles via des `ProjectRuleAssignment`.
- Les schémas décrivent les objets métier ; ils n'exécutent aucune logique.

#### Commit

`e0f87bd` — Define project rule foundation
