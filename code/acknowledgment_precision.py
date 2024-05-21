  
import json
import fuzzywuzzy.fuzz as fuzz

def load_results(file_path):
    """
    Load paper results from a JSON file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        list: List of paper results.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def compare_entities(gold_entities, predicted_entities):
  """
  Compares entities between two lists using fuzzy matching and returns counts for TP, FP, FN.

  Args:
      gold_entities: List of gold standard entities (strings).
      predicted_entities: List of predicted entities (strings).

  Returns:
      A dictionary containing TP, FP, and FN counts along with their corresponding fuzzy match scores.
  """
  tp = 0
  fp = 0
  fn = len(gold_entities)
  entity_matches = {}  # Dictionary to store entity matches with fuzzy scores

  for gold_entity in gold_entities:
    best_match = None
    best_score = 0

    for predicted_entity in predicted_entities:
      score = fuzz.ratio(gold_entity, predicted_entity)  # Calculate fuzzy match score

      if score > best_score:
        best_match = predicted_entity
        best_score = score

    if best_score >= 70:  # Consider a match if fuzzy score is 70 or above
      tp += 1
      entity_matches[gold_entity] = (best_match, best_score)
      predicted_entities.remove(best_match)  # Remove matched entity from predictions
    else:
      fn -= 1  # Decrement FN count if no close match found

  fp = len(predicted_entities)  # Remaining predicted entities are FPs

  return {"TP": tp, "FP": fp, "FN": fn, "EntityMatches": entity_matches}

def calculate_metrics(TP, FP, FN):
  """
  Calculates Precision, Recall, Accuracy, and F1-score based on TP, FP, and FN.

  Args:
      tp: True Positives count (integer).
      fp: False Positives count (integer).
      fn: False Negatives count (integer).

  Returns:
      A dictionary containing Precision, Recall, Accuracy, and F1-score values.
  """
  precision = TP / (TP + FP) if (TP + FP) > 0 else 0
  recall = TP / (TP + FN) if (TP + FN) > 0 else 0
  accuracy = (TP) / (TP + FP + FN) if (TP + FP + FN) > 0 else 0
  f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
  return {
      "Precision": precision,
      "Recall": recall,
      "Accuracy": accuracy,
      "F1-score": f1
  }

gold_standard_data = load_results("results/acknowledgment_manual.json")
predicted_data = load_results("results/acknowledgment.json")
  
per_metrics = {"TP": 0, "FP": 0, "FN": 0}
org_metrics = {"TP": 0, "FP": 0, "FN": 0}

for gold_data, prediction in zip(gold_standard_data, predicted_data):
  # Compare PER entities
  per_comparison = compare_entities(gold_data["PER"], prediction["PER"])
  per_metrics["TP"] += per_comparison["TP"]
  per_metrics["FP"] += per_comparison["FP"]
  per_metrics["FN"] += per_comparison["FN"]

  # Compare ORG entities
  org_comparison = compare_entities(gold_data["ORG"], prediction["ORG"])
  org_metrics["TP"] += org_comparison["TP"]
  org_metrics["FP"] += org_comparison["FP"]
  org_metrics["FN"] += org_comparison["FN"]

per_results = calculate_metrics(**per_metrics)
org_results = calculate_metrics(**org_metrics)

print("PER Entity Metrics:")
for metric, value in per_results.items():
  print(f"\t{metric}: {value:.4f}")

print("\nORG Entity Metrics:")
for metric, value in org_results.items():
  print(f"\t{metric}: {value:.4f}")
