# Context Directory Index

Reference files for business logic, measurement patterns, and cross-table conventions. Load these on demand — they are not always-on. Check this index before searching blindly.

---

## New Here?

| File | When to load |
|------|-------------|
| `quick-reference.md` | First time using PreQL, or any time you want a fast lookup — global rules, join keys, timestamp patterns, debug flowchart, skill triggers |

## Measurement

| File | When to load |
|------|-------------|
| `funnel-measurement-patterns.md` | Writing funnel SQL — phase-by-phase patterns, user counting, terminal node accounting |
| `revenue-aging.md` | Any revenue metric with a reporting lag — defines the standard aging window for funded/converted events |
| `sampling-methodology.md` | Before running expensive queries — cheap sampling approach to validate field values first |

## Experiment Analysis

| File | When to load |
|------|-------------|
| `experiment-analysis.md` | Any A/B experiment — standard metrics, retention templates, assignment exclusion rules, reseed handling |
| `advanced-experiment-topics.md` | SRM detection, CUPED variance reduction, interaction effects between experiments |
| `funnel-experiments.md` | Experiment + funnel join patterns — scoping conversion events to experiment window, user counting |
| `drop-off-to-experiment.md` | Routing funnel drop-off users into experiment designs |

## Identity & Joins

| File | When to load |
|------|-------------|
| `cross-table-joins.md` | Any cross-table join — join keys, identity field mapping, event table join patterns |

## Business Context

| File | When to load |
|------|-------------|
| `business-context.md` | Company/product overview, key metrics, revenue model — populate during setup; load when writing analysis context |
| `term-disambiguation.md` | Ambiguous terms: conversion rate, new user, session, dormant vs churned — resolve before writing SQL |
