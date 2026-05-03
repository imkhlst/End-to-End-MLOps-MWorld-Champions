# Esports-Match-Outcome-Prediction

## Overview

This project aims to predict the outcome of esports matches using historical team performance data. The model focuses on identifying key factors that influence match results, such as team strength, objective control, and game dynamics.

## Problem Statement

Predict whether the home team wins or loses based on pre-match and historical performance features.

## Data

The dataset was built from scraped match data and processed into a structured format.

**Key components**:
- Match metadata (teams, duration, etc.)
- Historical team performance (last N matches)
- In-game metrics (gold, objectives, etc.)

## Feature Engineering

Key features used in the final model:
- **Elo Difference (elo_diff)**
-> Represents relative team strength.
- **Objective Difference (objective_diff)**
-> Measures macro gameplay dominance (towers, lords, turtles).
- **Winrate Difference (winrate_diff)**
-> Reflects recent team consistency.
- **Scaling Difference (scaling_diff)**
-> Represents gold efficiency relative to match duration.

## Modeling
Model Used:
- Logistic Regression (main model)
- Compared with tree-based models (Random Forest, XGBoost)
Why Logistic Regression?
- Interpretable
- Stable performance
- Suitable for understanding feature impact

## Evaluation
Metrics:
- Accuracy: ~0.60
- ROC-AUC: ~0.68
- Log Loss: ~0.70
- Confusion Matrix: Balanced performance but notable false negatives (missed wins)

## Model Interpretation
**Feature Importance (SHAP)**

<img width="760" height="780" alt="output" src="https://github.com/user-attachments/assets/6afc7c1b-ff58-4cf7-b75f-28fe879c256e" />

Key observations:

- Elo difference (feature 1), scaling difference (feature 10), and objective control (feature 3) are dominant predictors
- Winrate difference (feature 8) contributes less compared to structural features

**Example Prediction (SHAP Waterfall)**

<img width="856" height="600" alt="output2" src="https://github.com/user-attachments/assets/9466b38e-36b5-4838-b199-8e76d79431ce" />

This example highlights a misclassified match where:

- The model predicts loss
- The team actually wins due to late-game scaling (comeback)

## Insights
**Error Analysis**
- The model shows reduced performance in closely matched games (small Elo differences), where predictions fall within a low-confidence range (0.4–0.65).
- The model is biased toward early and macro-level indicators (Elo and objective control), often misclassifying matches where teams win through late-game scaling (comeback scenarios).
**Segment Analysis**
- The model performs significantly better in matches with large disparities in team strength and economic advantage.
- In balanced matches, the model struggles due to limited discriminative signals.
- Elo and objective features dominate the prediction process, overshadowing the contribution of winrate.

## Limitations
- Difficulty capturing comeback scenarios
- Limited modeling of feature interactions
- Performance drops in balanced matches
- No draft/hero-level intelligence included

## Future Improvements
- Add draft intelligence (hero pick analysis)
- Model feature interactions (e.g., scaling vs objective)
- Introduce match pressure factors (stage, bracket importance)
- Build real-time prediction system
