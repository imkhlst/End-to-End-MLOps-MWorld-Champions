# Esports-Match-Outcome-Prediction

## Quick Summary

- Built a machine learning model to predict esports match outcomes
- Achieved ROC-AUC ~0.74
- Key insight: model struggles with comeback scenarios and balanced matches

## Overview

This project aims to predict the outcome of esports matches using historical team performance data. The model focuses on identifying key factors that influence match results, such as team strength, objective control, game dynamics, and draft intelligence.

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
- **Draft Winrate Difference (draft_wr_diff)**
-> Represent relative draft performance consistency.
- **Draft Stability Difference (draft_stability_diff)**
-> Refresent relative average draft stability.
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

## Feature Selection
SHAP shows interaction feature has represented by scaling or main transistion feature and draft tendency feature does not improve model performance significantly but make noisy interpretability. 

## Evaluation
Metrics:
- Accuracy: ~0.62
- ROC-AUC: ~0.74
- Log Loss: ~0.59
- Confusion Matrix: Balanced performance but notable false negatives (missed wins)

## Model Interpretation
Model -> Logistic Regression
Threshold prediction -> ~0.50
F1 score -> ~0.74
**Feature Importance (SHAP)**

![Feature Importance](/feature_importance.png)

Key observations:

- Scaling difference(feature 6), elo difference (feature 2), objective difference (feature 4), and draft tendency (feature 1) are dominant impact on model output
- Draft stability difference (feature 1) and kda difference (feature 3) contributes less compared to structural features

**Example Prediction (SHAP Waterfall)**

![Sample Match SHAP Waterfall](/sample_match_shap_waterfall.png)

This example highlights a misclassified match where:
- The model predicts loss
- The team actually wins due to late-game scaling (comeback)

## Insights
### Draft Intelligence significantly improve prediction
incorporating draft-based features improve model recall and overall predictive performance, indicating that hero selection plays a critical role beyond traditional performance metrics. in other hand, draft tendency feature does not improve model performance significantly but make noisy interpretability.
### Feature redundancy harms model clarity
Removing redundant features imporve model stability and interpretability without sacrificing performance.
### Simpler model performs better
A reduced feature set leads to better generalization suggesting tha model simplicity is preferable over feature abundance.
### Error Analysis
- The model shows reduced performance in closely matched games (small draft winrate and economy differences features), where predictions fall within a low-confidence range (0.4–0.65).
- The model is biased toward early and macro-level indicators (draft winrate, early and mid gold differences feature), often misclassifying matches where teams win through late-game scaling (comeback scenarios).
### Segment Analysis
- The model performs significantly better in matches with large disparities in draft composition and economic advantage.
- In balanced matches, the model struggles due to limited discriminative signals.
- Economy difference features dominate the prediction process, overshadowing the contribution of draft intellingence.

## Limitations
- Difficulty capturing comeback scenarios
- Limited modeling of feature interactions
- Performance drops in balanced matches

## Future Improvements
- Model feature interactions (e.g., scaling vs objective)
- Introduce match pressure factors (stage, bracket importance)
- Build real-time prediction system
